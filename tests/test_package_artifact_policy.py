from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_tokenizer_wheel_excludes_all_source_and_generated_wordlists():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["tool"]["setuptools"]["include-package-data"] is False
    package_data = config["tool"]["setuptools"]["package-data"]["tamil_morph_tokenizer"]
    excluded = config["tool"]["setuptools"]["exclude-package-data"]["tamil_morph_tokenizer"]
    assert "data/wordlists/*" in excluded
    assert "data/wordlists/lemma_dictionary.txt" not in package_data
    assert "data/wordlists/*.txt" not in package_data
    assert not any("generated_forms" in item or "heuristic_forms" in item for item in package_data)
