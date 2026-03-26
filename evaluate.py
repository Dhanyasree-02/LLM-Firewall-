"""
evaluate.py — Evaluation harness for the LLM Firewall Classifier

Usage:
    python evaluate.py
    python evaluate.py --dataset data/redteam_dataset.json --output results.json

Expects:
    - classify_prompt(text) importable from llm_firewall (adjust import if needed)
    - Dataset JSON: list of {"text": str, "label": str}
"""

import argparse
import json
import sys
from pathlib import Path

# ── Import your classifier ────────────────────────────────────────────────────
# Adjust this import to match your actual module / function location.
try:
    from llm_firewall import classify_prompt
    print(classify_prompt("test"))

except ImportError:
    print("[ERROR] Could not import 'classify_prompt' from 'llm_firewall'.")
    print("        Update the import at the top of evaluate.py to match your module.")
    sys.exit(1)


# ── Constants ─────────────────────────────────────────────────────────────────

SAFE_LABEL = "safe"          # the one label the classifier treats as non-harmful
DEFAULT_DATASET = "data/redteam_dataset.json"
DEFAULT_OUTPUT  = "results.json"


# ── Dataset loader ────────────────────────────────────────────────────────────

def load_dataset(path: str) -> list[dict]:
    """Load and validate the evaluation dataset from a JSON file."""
    dataset_path = Path(path)

    if not dataset_path.exists():
        print(f"[ERROR] Dataset not found: {dataset_path}")
        sys.exit(1)

    with dataset_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        print("[ERROR] Dataset must be a non-empty JSON array.")
        sys.exit(1)

    for i, item in enumerate(data):
        if "text" not in item or "label" not in item:
            print(f"[ERROR] Item {i} is missing 'text' or 'label' keys.")
            sys.exit(1)

    print(f"[INFO] Loaded {len(data)} samples from '{dataset_path}'.")
    return data


# ── Single-sample evaluation ──────────────────────────────────────────────────

def evaluate_sample(item: dict) -> dict:
    """
    Run classify_prompt on one sample and return a result record.

    A prediction is 'correct' when:
      - true label is safe   AND verdict is allowed, OR
      - true label is unsafe AND verdict is blocked
    """
    text       = item["text"]
    true_label = item["label"].strip().lower()

    result = classify_prompt(text)

    predicted_label = result.get("category", "unknown").strip().lower()
    verdict         = result.get("verdict", "unknown").strip().lower()
    confidence      = result.get("confidence", 0.0)

    true_is_safe    = (true_label == SAFE_LABEL)
    correct = (
        (true_is_safe     and verdict == "allowed") or
        (not true_is_safe and verdict == "blocked")
    )

    return {
        "text":            text,
        "true_label":      true_label,
        "predicted_label": predicted_label,
        "verdict":         verdict,
        "confidence":      round(confidence, 4),
        # internal flags (stripped before saving)
        "_correct":        correct,
        "_true_is_safe":   true_is_safe,
    }


# ── Full evaluation run ───────────────────────────────────────────────────────

def run_evaluation(dataset: list[dict]) -> list[dict]:
    """Evaluate every sample; show a progress indicator."""
    results = []
    total = len(dataset)

    for idx, item in enumerate(dataset, start=1):
        print(f"  [{idx:>4}/{total}] Classifying…", end="\r")
        results.append(evaluate_sample(item))

    print()  # newline after progress line
    return results


# ── Metrics ───────────────────────────────────────────────────────────────────

def compute_metrics(results: list[dict]) -> dict:
    """
    Compute accuracy, false positives, and missed attacks.

    False Positive : true=safe   but verdict=blocked
    Missed Attack  : true=unsafe but verdict=allowed
    """
    total          = len(results)
    correct        = sum(1 for r in results if r["_correct"])
    false_positives = sum(
        1 for r in results
        if r["_true_is_safe"] and r["verdict"] == "blocked"
    )
    missed_attacks  = sum(
        1 for r in results
        if not r["_true_is_safe"] and r["verdict"] == "allowed"
    )

    return {
        "total":           total,
        "correct":         correct,
        "accuracy":        round(correct / total, 4) if total else 0.0,
        "false_positives": false_positives,
        "missed_attacks":  missed_attacks,
    }


# ── Output helpers ────────────────────────────────────────────────────────────

def strip_internal_flags(results: list[dict]) -> list[dict]:
    """Remove evaluation-only keys before saving to disk."""
    keep_keys = {"text", "true_label", "predicted_label", "verdict", "confidence"}
    return [{k: v for k, v in r.items() if k in keep_keys} for r in results]


def save_results(results: list[dict], output_path: str) -> None:
    """Write the per-sample result records to a JSON file."""
    clean = strip_internal_flags(results)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Detailed results saved → '{output_path}'")


def print_summary(metrics: dict) -> None:
    """Print a human-readable evaluation summary."""
    accuracy_pct       = metrics["accuracy"] * 100
    fp_pct = (metrics["false_positives"] / metrics["total"] * 100) if metrics["total"] else 0
    ma_pct = (metrics["missed_attacks"]  / metrics["total"] * 100) if metrics["total"] else 0

    print("\n" + "═" * 50)
    print("  EVALUATION SUMMARY")
    print("═" * 50)
    print(f"  Total Samples   : {metrics['total']}")
    print(f"  Correct         : {metrics['correct']}")
    print(f"  Accuracy        : {accuracy_pct:.1f}%")
    print(f"  False Positives : {metrics['false_positives']}  ({fp_pct:.1f}%  of total)")
    print(f"  Missed Attacks  : {metrics['missed_attacks']}  ({ma_pct:.1f}%  of total)")
    print("═" * 50 + "\n")


# ── CLI entry point ───────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the LLM firewall classifier against a labelled dataset."
    )
    parser.add_argument(
        "--dataset", default=DEFAULT_DATASET,
        help=f"Path to the evaluation dataset JSON (default: {DEFAULT_DATASET})"
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help=f"Path for the detailed results JSON (default: {DEFAULT_OUTPUT})"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("\n── LLM Firewall Evaluator ─────────────────────────────")

    dataset = load_dataset(args.dataset)

    print(f"[INFO] Running classifier on {len(dataset)} samples …\n")
    results = run_evaluation(dataset)

    metrics = compute_metrics(results)
    save_results(results, args.output)
    print_summary(metrics)


if __name__ == "__main__":
    main()