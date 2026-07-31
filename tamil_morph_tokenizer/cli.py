from __future__ import annotations

import argparse
import json

from .tokenizer import TamilMorphTokenizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Morphology-aware Tamil tokenizer demo")
    parser.add_argument("text", nargs="*", help="Tamil text or words to tokenize")
    parser.add_argument(
        "--mode",
        choices=["best", "compact_ambiguity", "all_analyses"],
        default="compact_ambiguity",
        help="Token rendering mode for analyzed Tamil words",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON records")
    args = parser.parse_args()

    text = " ".join(args.text).strip()
    tokenizer = TamilMorphTokenizer(mode=args.mode)
    records = tokenizer.tokenize(text)

    if args.json:
        print(json.dumps([
            {
                "surface": record.surface,
                "tokens": list(record.tokens),
                "fallback": record.fallback,
                "semantic_special": record.semantic_special,
                "special_handling": record.special_handling,
                "best_analysis": record.best_analysis.raw if record.best_analysis else None,
                "analyses": [analysis.raw for analysis in record.analyses],
            }
            for record in records
        ], ensure_ascii=False, indent=2))
        return

    for record in records:
        print(record.surface)
        print("  tokens:", " ".join(record.tokens))
        if record.best_analysis:
            print("  best:", record.best_analysis.raw, f"[{record.best_analysis.model}]")
        if len(record.analyses) > 1:
            print("  analyses:")
            for analysis in record.analyses:
                print("   -", analysis.raw, f"[{analysis.model}]")
        if record.fallback:
            print("  fallback:", record.fallback)
        if record.semantic_special:
            print("  semantic_special:", record.semantic_special)
            print("  special_handling:", record.special_handling)

if __name__ == "__main__":
    main()
