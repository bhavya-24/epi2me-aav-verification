"""Measure this project's FASTQ validator on explicitly labelled challenge files."""
import argparse
import csv
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import sys
from verify_aav import ROOT, fastq_ids, metrics, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    specification = ROOT / "fixtures/validator/cases.json"
    spec = json.loads(specification.read_text(encoding="utf-8"))
    directory = args.report.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    inputs = directory / "inputs"
    inputs.mkdir()
    cases = spec["cases"]
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Duplicate challenge case")
    # Record truth before executing the validator; never derive labels from its response.
    with (directory / "truth.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["read_id", "label"])
        writer.writerows((c["id"], c["label"]) for c in cases)
    evidence = []
    for case in cases:
        data = case["content"].encode("ascii")
        if case.get("gzip"):
            data = gzip.compress(data, mtime=0)
        path = inputs / (case["id"] + (".fq.gz" if case.get("gzip") else ".fq"))
        path.write_bytes(data)
        try:
            count = len(fastq_ids(path))
            prediction, detail = "negative", f"Accepted {count} records"
        except ValueError as error:
            prediction, detail = "positive", str(error)
        # OSError and unexpected exceptions deliberately propagate: a missing file
        # or broken environment is not successful malformed-input detection.
        evidence.append({"id": case["id"], "truth": case["label"], "prediction": prediction,
                         "reason": case["reason"], "detail": detail, "sha256": sha256(path)})
    with (directory / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["read_id", "label"])
        writer.writerows((e["id"], e["prediction"]) for e in evidence)
    scores = metrics(directory / "truth.csv", directory / "predictions.csv")
    payload = {"finished_at": datetime.now(timezone.utc).isoformat(), "python": sys.version,
               "scope": spec["scope"], "unit": "file; read_id is the shared metric API's case-ID column",
               "source_sha256": {name: sha256(ROOT / name) for name in ("verify_aav.py", "run_validator_benchmark.py", "fixtures/validator/cases.json")},
               "metrics": scores, "cases": evidence,
               "limitations": "Small authored challenge set, related to existing unit tests. Not independent external validation, EPI2ME workflow accuracy or clinical performance."}
    (directory / "report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    counts = scores["counts"]
    lines = ["# FASTQ validator challenge-set benchmark", "", spec["scope"], "",
             f"TP={counts['tp']}; FN={counts['fn']}; TN={counts['tn']}; FP={counts['fp']}.",
             f"Sensitivity={scores['sensitivity_on_classified']}; specificity={scores['specificity_on_classified']}; coverage={scores['classification_coverage']}.",
             "", payload["limitations"], "",
             "| Case | Truth | Prediction | Reason / actual diagnostic |", "|---|---|---|---|"]
    lines += [f"| {e['id']} | {e['truth']} | {e['prediction']} | {e['reason']}: {e['detail']} |" for e in evidence]
    (directory / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(scores, indent=2))
    return 1 if counts["fp"] or counts["fn"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
