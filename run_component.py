"""Execute the unmodified EPI2ME contamination CLI and save reviewable evidence."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from verify_aav import ROOT, REVISION, sha256


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def make_inputs(spec, directory):
    directory.mkdir(parents=True)
    rows = [(f"r{i:03d}", "transgene", 1000) for i in range(80)]
    rows += [(f"r{i:03d}", "helper", 1200) for i in range(80, 90)]
    rows += [(f"r{i:03d}", "host", 1500) for i in range(90, 95)]
    recipe = spec["recipe"]
    if recipe == "duplicate_alignment":
        rows.append(rows[0])
    elif recipe == "reversed":
        rows.reverse()
    elif recipe == "all_mapped":
        rows = [(f"r{i}", ref, 1000) for i, ref in enumerate(("transgene", "transgene", "helper", "host", "repcap"))]
    elif recipe == "transgene_only":
        rows = rows[:2]
    elif recipe == "empty":
        rows = []
    elif recipe == "unknown_reference":
        rows.append(("r095", "unlisted_reference", 1600))
    elif recipe not in ("baseline", "missing_column", "missing_fasta"):
        raise ValueError(f"Unknown fixture recipe: {recipe}")
    with (directory / "alignments.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["Read", "Ref"] if recipe == "missing_column" else ["Read", "Ref", "ReadLen"])
        writer.writerows([row[:2] for row in rows] if recipe == "missing_column" else rows)
    (directory / "transgene.fasta").write_text(">transgene fixture reference\nACGTACGTACGT\n", encoding="utf-8")
    save_json(directory / "reference_ids.json", {"Helper": ["helper"], "Host": ["host"], "RepCap": ["repcap"]})
    return {p.name: sha256(p) for p in directory.iterdir() if p.is_file()}


def parse_output(path):
    result = {}
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"Reference", "Number of alignments", "Percentage of alignments", "sample_id"}
        if set(reader.fieldnames or []) != required:
            raise ValueError("Output schema differs from the pinned component contract")
        for row in reader:
            label = row["Reference"]
            if not label or label in result:
                raise ValueError("Duplicate or empty output category")
            numbers = [float(row["Number of alignments"]), float(row["Percentage of alignments"])]
            if not all(math.isfinite(x) for x in numbers):
                raise ValueError("Non-finite output number")
            result[label] = {"count": numbers[0], "percentage": numbers[1], "sample_id": row["sample_id"]}
    return result


def assess(spec, receipt, output):
    if receipt.get("execution_error"):
        return "BLOCKED", receipt["execution_error"]
    if "explore" in spec:
        return "OBSERVATION", spec["explore"]
    if "error_contains" in spec:
        if receipt["exit_code"] != 0 and spec["error_contains"] in receipt["stderr"] and not output.exists():
            return "PASS", "Expected input failure and specific diagnostic observed; no output emitted"
        return "FAIL", "Expected a specific input diagnostic and no output, not merely any nonzero exit"
    if receipt["exit_code"] != 0:
        return "FAIL", f"Component exited {receipt['exit_code']}; inspect stderr.txt"
    try:
        observed = parse_output(output)
        expected = spec["expected"]
        if set(observed) != set(expected):
            raise ValueError(f"Category set differs: {sorted(observed)}")
        for name, (count, percentage) in expected.items():
            row = observed[name]
            if row["count"] != count or not math.isclose(row["percentage"], percentage, rel_tol=0, abs_tol=1e-8):
                raise ValueError(f"{name}: expected {[count, percentage]}, got {row}")
            if row["sample_id"] != spec.get("sample_id", "SYNTHETIC_A"):
                raise ValueError("Sample identity differs")
        return "PASS", "Exact categories/counts, expected percentages and sample identity confirmed"
    except (OSError, ValueError, KeyError) as error:
        return "FAIL", str(error)


def write_summary(directory, results):
    lines = ["# EPI2ME contamination component verification", "",
             "Executed upstream Python component with real native SeqKit. Synthetic alignment tables; no full Nextflow run.", "",
             "Contract checks are assessed against declared expectations. Exploratory probes record behaviour without declaring an upstream defect.", "",
             "| Case | Requirement | Assessment | Detail |", "|---|---|---|---|"]
    for row in results:
        detail = row["detail"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| [{row['id']}]({row['id']}/receipt.json) | {row['requirement']} | {row['status']} | {detail} |")
    lines += ["", "Each case contains its inputs, declared expectations, receipt, stdout/stderr and any component output.",
              "", "Review status: applicant review pending. These results are component verification in the recorded environment, not clinical accuracy or regulatory approval."]
    (directory / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    contracts = [r for r in results if r["status"] != "OBSERVATION"]
    suite = ET.Element("testsuite", name="EPI2ME component contracts", tests=str(len(contracts)),
                       failures=str(sum(r["status"] == "FAIL" for r in contracts)),
                       skipped=str(sum(r["status"] == "BLOCKED" for r in contracts)))
    for row in contracts:
        case = ET.SubElement(suite, "testcase", name=row["id"], classname=row["requirement"])
        if row["status"] != "PASS":
            ET.SubElement(case, "failure" if row["status"] == "FAIL" else "skipped").text = row["detail"]
    ET.ElementTree(suite).write(directory / "junit.xml", encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--case", help="Run a single declared case, e.g. C02")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "upstream/SOURCE.json").read_text())
    if manifest["revision"] != REVISION:
        raise SystemExit("Upstream revision differs from project lock")
    for name, expected in manifest["files"].items():
        if sha256(ROOT / "upstream" / name) != expected:
            raise SystemExit(f"Upstream source modified: {name}")
    tools_dir = ROOT / "cache/component-tools"
    seqkit = tools_dir / ("seqkit.exe" if os.name == "nt" else "seqkit")
    tool_receipt = json.loads((tools_dir / "receipt.json").read_text())
    if sha256(seqkit) != tool_receipt["executable_sha256"]:
        raise SystemExit("SeqKit executable differs from setup receipt")
    env = os.environ.copy()
    env["PATH"] = str(tools_dir) + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    specs = json.loads((ROOT / "fixtures/component/cases.json").read_text())["cases"]
    if args.case:
        specs = [s for s in specs if s["id"] == args.case]
        if not specs:
            raise SystemExit("Unknown case ID")
    directory = args.report.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    run = {"started_at": datetime.now(timezone.utc).isoformat(), "finished_at": None,
           "revision": REVISION, "python": sys.version, "platform": platform.platform(),
           "dependencies": {n: importlib.metadata.version(n) for n in ("numpy", "pandas")},
           "seqkit": tool_receipt, "source_manifest_sha256": sha256(ROOT / "upstream/SOURCE.json"),
           "project_files_sha256": {n: sha256(ROOT/n) for n in ("run_component.py", "component_entry.py", "fixtures/component/cases.json", "requirements-component.txt")},
           "results": []}
    save_json(directory / "run.json", run)
    for spec in specs:
        case_dir = directory / spec["id"]
        hashes = make_inputs(spec, case_dir / "inputs")
        save_json(case_dir / "expectation.json", spec)
        output = case_dir / "output.tsv"
        inputs = case_dir / "inputs"
        command = [sys.executable, "-B", str(ROOT / "component_entry.py"), "contamination",
                   "--bam_info", str(inputs / "alignments.tsv"), "--sample_id", spec.get("sample_id", "SYNTHETIC_A"),
                   "--transgene_fasta", str(inputs / ("missing.fasta" if spec["recipe"] == "missing_fasta" else "transgene.fasta")),
                   "--ref_ids", str(inputs / "reference_ids.json"), "--n_reads", str(spec["n_reads"]),
                   "--contam_class_counts", str(output)]
        receipt = {"argv": command, "input_sha256": hashes, "started_at": datetime.now(timezone.utc).isoformat()}
        try:
            process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
            receipt.update(exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr)
        except (OSError, subprocess.TimeoutExpired) as error:
            receipt.update(exit_code=None, stdout="", stderr="", execution_error=str(error))
        receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
        status, detail = assess(spec, receipt, output)
        receipt.update(status=status, detail=detail)
        if output.exists():
            receipt["output_sha256"] = sha256(output)
        save_json(case_dir / "receipt.json", receipt)
        (case_dir / "stdout.txt").write_text(receipt["stdout"], encoding="utf-8")
        (case_dir / "stderr.txt").write_text(receipt["stderr"], encoding="utf-8")
        run["results"].append({"id": spec["id"], "requirement": spec["requirement"], "status": status, "detail": detail})
        save_json(directory / "run.json", run)
        print(spec["id"], status, detail)
    run["finished_at"] = datetime.now(timezone.utc).isoformat()
    run["review_status"] = "PENDING_APPLICANT_REVIEW"
    save_json(directory / "run.json", run)
    write_summary(directory, run["results"])
    return 1 if any(r["status"] == "FAIL" for r in run["results"]) else (2 if any(r["status"] == "BLOCKED" for r in run["results"]) else 0)


if __name__ == "__main__":
    raise SystemExit(main())
