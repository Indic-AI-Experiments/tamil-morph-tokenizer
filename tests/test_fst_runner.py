from pathlib import Path
import shutil
import subprocess

import pytest

from tamil_morph_tokenizer.fst import FlookupAnalyzer


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_flookup_analyzer_preserves_multiple_model_analyses():
    analyzer = FlookupAnalyzer()
    results = analyzer.analyze(["மரங்களை", "படித்தான்"])
    assert any(a.lemma == "மரம்" and "acc" in a.tags for a in results["மரங்களை"])
    assert any(a.lemma == "படி" and "verb" in a.tags for a in results["படித்தான்"])


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_predicate_questions_preserve_interrogative_readings():
    analyzer = FlookupAnalyzer()
    results = analyzer.analyze(
        ["உண்மையானதா", "அதிர்ஷ்டமானதா", "அரிதா", "இனிதா", "நன்றா"]
    )
    expected = {
        "உண்மையானதா": "உண்மை",
        "அதிர்ஷ்டமானதா": "அதிர்ஷ்டம்",
        "அரிதா": "அரிது",
        "இனிதா": "இனிது",
        "நன்றா": "நன்று",
    }
    for surface, lemma in expected.items():
        assert any(
            analysis.lemma == lemma and "ques=ஆ" in analysis.tags
            for analysis in results[surface]
        )


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_corrected_u_final_noun_paradigms_and_invalid_forms():
    analyzer = FlookupAnalyzer()
    valid = analyzer.analyze(
        ["மொட்டை", "காட்டிடம்", "ஆற்றை", "குன்றை", "காற்றை", "பூட்டை"]
    )
    forbidden = {
        "மொட்ட்டை": "மொட்டு+noun+acc",
        "மொட்டுஇடம்": "மொட்டு+noun+loc",
        "காடுஇடம்": "காடு+noun+loc",
        "ஆறை": "ஆறு+noun+acc",
        "குன்ற்றை": "குன்று+noun+acc",
        "பூட்ட்டை": "பூட்டு+noun+acc",
    }
    invalid = analyzer.analyze(list(forbidden))

    assert any(a.raw == "மொட்டு+noun+acc" for a in valid["மொட்டை"])
    assert any(a.raw == "காடு+noun+loc" for a in valid["காட்டிடம்"])
    assert any(a.raw == "ஆறு+noun+acc" for a in valid["ஆற்றை"])
    assert any(a.raw == "குன்று+noun+acc" for a in valid["குன்றை"])
    assert any(a.raw == "காற்று+noun+acc" for a in valid["காற்றை"])
    assert any(a.raw == "பூட்டு+noun+acc" for a in valid["பூட்டை"])
    for surface, forbidden_analysis in forbidden.items():
        assert all(a.raw != forbidden_analysis for a in invalid[surface])


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_final_pos_mismatch_batch_and_irregular_ney_paradigm():
    analyzer = FlookupAnalyzer()
    expected = {
        "பெயரை": "பெயர்+noun+acc",
        "பின்னை": "பின்+noun+acc",
        "மூலத்தை": "மூலம்+noun+infInc+acc",
        "இணர்ந்தான்": "இணர்+verb+fin+sim+strong+past=த்+3sgm=ஆன்",
        "சுடர்ந்தான்": "சுடர்+verb+fin+sim+strong+past=த்+3sgm=ஆன்",
        "நெய்தான்": "நெய்+verb+fin+sim+strong+past=த்+3sgm=ஆன்",
        "நெய்தல்": "நெய்+verb+nonfin+sim+verbalnoun=தல்",
        "இலங்குதல்": "இலங்கு+verb+nonfin+sim+verbalnoun=தல்",
        "மென்னுதல்": "மென்னு+verb+nonfin+sim+verbalnoun=தல்",
    }
    results = analyzer.analyze(list(expected) + ["நெய்த்தான்", "நெய்ந்தான்"])

    for surface, raw in expected.items():
        assert any(analysis.raw == raw for analysis in results[surface])
    assert not results["நெய்த்தான்"]
    assert not results["நெய்ந்தான்"]


@pytest.mark.skipif(shutil.which("flookup") is None, reason="flookup is not installed")
def test_final_structural_and_reviewed_verb_batch():
    analyzer = FlookupAnalyzer()
    results = analyzer.analyze(
        [
            "தளர்ந்தான்", "பிசைகிறான்", "பளபளப்பான்", "சிவந்தான்",
            "ஒத்துக்கொண்டான்", "வைத்துக்கொள்வான்", "ஆகு",
            "இட்டான்", "பெற்றான்", "இடுத்தான்", "பெற்டான்", "செய்திருந்தான்",
        ]
    )
    expected_lemmas = {
        "தளர்ந்தான்": "தளர்", "பிசைகிறான்": "பிசை", "பளபளப்பான்": "பளபள",
        "சிவந்தான்": "சிவ", "ஒத்துக்கொண்டான்": "ஒத்துக்கொள்",
        "வைத்துக்கொள்வான்": "வைத்துக்கொள்", "ஆகு": "ஆகு",
        "இட்டான்": "இடு", "பெற்றான்": "பெறு",
    }
    for surface, lemma in expected_lemmas.items():
        assert any(analysis.lemma == lemma for analysis in results[surface])
    assert not results["இடுத்தான்"]
    assert not results["பெற்டான்"]
    iru = [analysis.raw for analysis in results["செய்திருந்தான்"]]
    assert any("+complex+aspect+" in raw for raw in iru)
    assert all("+complex+mood+" not in raw for raw in iru)


def test_analyze_merges_identical_analyses_and_preserves_model_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    for name in ("verb-c4.fst", "verb-c11.fst"):
        (tmp_path / name).write_text("model", encoding="utf-8")
    monkeypatch.setattr("tamil_morph_tokenizer.fst.shutil.which", lambda _: "/usr/bin/flookup")

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="உடை\tஉடை+verb+fin+sim+imp=∅+2sg=∅\n",
            stderr="",
        )

    monkeypatch.setattr("tamil_morph_tokenizer.fst.subprocess.run", fake_run)
    analyzer = FlookupAnalyzer(
        fst_dir=tmp_path,
        model_names=["verb-c4.fst", "verb-c11.fst"],
    )

    analyses = analyzer.analyze(["உடை"])["உடை"]

    assert len(analyses) == 1
    assert analyses[0].model == "verb-c4.fst|verb-c11.fst"
