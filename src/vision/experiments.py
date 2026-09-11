"""Deterministic experiment runner for saved sticker samples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .color_model import classify_balanced, classify_independent
from .metrics import evaluate_predictions


def run_records(records, method="balanced_lab"):
    truth, predictions, rows = [], [], []
    for record in records:
        classify = classify_balanced if method == "balanced_lab" else classify_independent
        result = classify(record["samples_bgr"], record["prototypes_bgr"])
        predicted = "".join(result.labels)
        truth.append(record["labels"])
        predictions.append(predicted)
        rows.append({"sample_id": record["sample_id"], "prediction": predicted,
                     "mean_confidence": sum(result.confidence) / len(result.confidence)})
    return evaluate_predictions(truth, predictions), rows


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON list of saved color-sample records")
    parser.add_argument("--method", choices=("independent_lab", "balanced_lab"), default="balanced_lab")
    parser.add_argument("--output", default="artifacts/predictions.csv")
    args = parser.parse_args(argv)
    records = json.loads(Path(args.input).read_text(encoding="utf-8"))
    metrics, rows = run_records(records, args.method)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps(metrics.__dict__, indent=2))


if __name__ == "__main__":
    main()
