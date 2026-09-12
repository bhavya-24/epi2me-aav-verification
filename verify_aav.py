"""Small, auditable verification harness. Python 3.10+, standard library only.

Checks the upstream demo and outputs; does not establish clinical validity.
Missing tools/evidence are BLOCKED, never PASS. Synthetic tests are independent
of, and must not be described as, execution of the EPI2ME workflow.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REVISION = "43a4266fc30a131c9e2b49654a97a3fd59e41d94"
DEMO_SHA = "7a62b511c2cfaece8a64312858ae60200354c3d55f9329a21031d279d81c1d53"
SAMPLES = ("sample_1", "sample_2")
REFS = ("transgene.fasta", "helper.fasta", "repcap.fasta", "cell_line.fasta.gz")
MEMBERS = (*REFS, *(f"fastq/{s}/simulated_reads.fq" for s in SAMPLES))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_text(path):
    path = Path(path)
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open(encoding="utf-8")


def fastq_ids(path):
    """Validate the four-line FASTQ dialect used by this pinned demo."""
    seen = set()
    with open_text(path) as stream:
        while header := stream.readline():
            sequence = stream.readline().rstrip("\r\n")
            plus = stream.readline().rstrip("\r\n")
            quality = stream.readline().rstrip("\r\n")
            if not header.startswith("@") or not header[1:].strip():
                raise ValueError("FASTQ header must start with @ and contain a read ID")
            read_id = header[1:].split()[0]
            if read_id in seen:
                raise ValueError(f"Duplicate read ID: {read_id}")
            if not sequence or not re.fullmatch("[ACGTNacgtn]+", sequence):
                raise ValueError(f"Empty/unsupported sequence for {read_id}")
            if not plus.startswith("+") or len(sequence) != len(quality):
                raise ValueError(f"Truncated FASTQ or sequence/quality mismatch for {read_id}")
            if plus[1:] and plus[1:].split()[0] != read_id:
                raise ValueError(f"Repeated identifier differs for {read_id}")
            if any(ord(c) < 33 or ord(c) > 126 for c in quality):
                raise ValueError(f"Invalid Phred+33 character for {read_id}")
            seen.add(read_id)
    if not seen:
        raise ValueError("No FASTQ reads")
    return seen


def fasta_records(path):
    records, name, chunks = {}, None, []
    with open_text(path) as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    records[name] = "".join(chunks)
                if not line[1:].strip():
                    raise ValueError("Empty FASTA identifier")
                name = line[1:].split()[0]
                if name in records:
                    raise ValueError(f"Duplicate FASTA identifier: {name}")
                chunks = []
            else:
                if name is None or not re.fullmatch("[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+", line):
                    raise ValueError("Invalid FASTA sequence/header")
                chunks.append(line.upper())
    if name is not None:
        records[name] = "".join(chunks)
    if not records or any(not value for value in records.values()):
        raise ValueError("Empty FASTA file/record")
    return records


def prepare(archive, destination):
    archive, destination = Path(archive), Path(destination)
    if sha256(archive) != DEMO_SHA:
        raise ValueError("Demo archive SHA256 differs from the reviewed lock file")
    if destination.exists():
        raise ValueError("Destination exists; use a new directory to preserve evidence")
    with tarfile.open(archive, "r:gz") as source:
        selected = []
        for relative in MEMBERS:
            member = source.getmember("wf-aav-qc-demo/" + relative)
            if not member.isfile() or member.issym() or member.islnk():
                raise ValueError(f"Expected regular file: {relative}")
            selected.append((relative, member))
        destination.mkdir(parents=True)
        for relative, member in selected:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.extractfile(member) as incoming, target.open("xb") as outgoing:
                shutil.copyfileobj(incoming, outgoing)
    manifest = {
        "source_archive_sha256": DEMO_SHA,
        "files": {name: sha256(destination / name) for name in MEMBERS},
        "samples": list(SAMPLES),
        "data_type": "upstream simulated demonstration reads",
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def derive_baseline(source, destination):
    """Quarantine the one observed malformed demo record; never guess its base."""
    source, destination = Path(source), Path(destination)
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('source_archive_sha256') != DEMO_SHA or manifest.get('derivation'):
        raise ValueError('Baseline must derive directly from the reviewed original demo')
    if set(manifest.get('files', {})) != set(MEMBERS):
        raise ValueError('Unexpected original manifest file set')
    for name in MEMBERS:
        if sha256(source / name) != manifest['files'][name]:
            raise ValueError(f'Original source changed: {name}')
    if destination.exists():
        raise ValueError('Baseline destination exists; preserve previous evidence')
    destination.mkdir(parents=True)
    omitted = 0
    for name in MEMBERS:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name != 'fastq/sample_1/simulated_reads.fq':
            shutil.copyfile(source / name, target)
            continue
        with (source / name).open('rb') as incoming, target.open('xb') as outgoing:
            while header := incoming.readline():
                seq, plus, quality = incoming.readline(), incoming.readline(), incoming.readline()
                record = header + seq + plus + quality
                if header.split()[0] == b'@transgene_cassette_3':
                    sequence = seq.rstrip(b'\r\n')
                    invalid = [(i, c) for i, c in enumerate(sequence) if c not in b'ACGTNacgtn']
                    if invalid != [(412, ord('q'))] or len(sequence) != len(quality.rstrip(b'\r\n')):
                        raise ValueError('Observed record differs from the documented anomaly; investigate instead of filtering')
                    if omitted:
                        raise ValueError('More than one matching read; investigate duplicate IDs')
                    (destination / 'quarantined-record.fastq').write_bytes(record)
                    omitted += 1
                else:
                    outgoing.write(record)
    if omitted != 1:
        raise ValueError('Documented anomaly not found; no approved derivation can be recorded')
    counts = {sample: len(fastq_ids(destination / 'fastq' / sample / 'simulated_reads.fq')) for sample in SAMPLES}
    derived = {
        'source_archive_sha256': DEMO_SHA,
        'files': {name: sha256(destination / name) for name in MEMBERS},
        'samples': list(SAMPLES), 'data_type': 'derived upstream simulated demonstration reads',
        'derivation': {'action': 'quarantine_one_malformed_record', 'sample': 'sample_1',
                       'read_id': 'transgene_cassette_3', 'reason': 'non-nucleotide q at one-based position 413',
                       'source_manifest_sha256': sha256(source / 'manifest.json'),
                       'source_files': manifest['files'], 'remaining_reads': counts,
                       'quarantine_sha256': sha256(destination / 'quarantined-record.fastq')},
    }
    (destination / 'manifest.json').write_text(json.dumps(derived, indent=2) + '\n', encoding='utf-8')
    return derived


@dataclass
class Check:
    id: str
    requirement: str
    status: str
    detail: str


def capture(checks, identifier, requirement, operation):
    try:
        detail = operation()
        checks.append(Check(identifier, requirement, "PASS", str(detail)))
    except (OSError, ValueError, KeyError, csv.Error, EOFError) as error:
        checks.append(Check(identifier, requirement, "FAIL", str(error)))


def require_file(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty file: {path}")
    return f"Present, {path.stat().st_size} bytes; SHA256 {sha256(path)}"


def preflight(demo):
    demo, checks = Path(demo), []
    def provenance():
        manifest = json.loads((demo / "manifest.json").read_text(encoding="utf-8"))
        if manifest["source_archive_sha256"] != DEMO_SHA or set(manifest["files"]) != set(MEMBERS):
            raise ValueError("Unexpected manifest source or input file set")
        for name in MEMBERS:
            if sha256(demo / name) != manifest["files"][name]:
                raise ValueError(f"Input changed since preparation: {name}")
        return "All six selected input files match the prepared SHA256 manifest"
    capture(checks, "IN-01", "REQ-01", provenance)
    for sample in SAMPLES:
        capture(checks, f"IN-02:{sample}", "REQ-02", lambda sample=sample:
                f"{len(fastq_ids(demo / 'fastq' / sample / 'simulated_reads.fq'))} unique valid reads")
    for reference in REFS:
        capture(checks, f"IN-03:{reference}", "REQ-03", lambda reference=reference:
                f"{len(fasta_records(demo / reference))} nonempty reference sequences")
    def coordinates():
        records = fasta_records(demo / "transgene.fasta")
        if len(records) != 1 or not (0 <= 11 < 156 < 2156 < 2286 <= len(next(iter(records.values())))):
            raise ValueError("Demo ITR coordinates are not ordered or are outside the single transgene reference")
        ids = [name for ref in REFS for name in fasta_records(demo / ref)]
        if len(ids) != len(set(ids)):
            raise ValueError("Reference identifiers overlap across input FASTAs")
        return "Reviewed demo coordinates fit; reference identifiers are unique. Coordinate convention inherited from upstream demo."
    capture(checks, "IN-04", "REQ-03", coordinates)
    return checks


def tsv_read_ids(path, allowed):
    with open_text(path) as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not reader.fieldnames or "Read" not in reader.fieldnames:
            raise ValueError("Missing upstream 'Read' column")
        ids = set()
        for row in reader:
            read_id = row.get("Read")
            if not read_id or read_id not in allowed:
                raise ValueError(f"Output read absent from expected sample input: {read_id}")
            ids.add(read_id)
    if not ids:
        raise ValueError("No classified reads in demo structure table")
    return f"{len(ids)} unique output IDs found in this sample's input; table is a subset, not all reads"


def external_check(checks, identifier, requirement, command, evidence, timeout=300):
    """Run a tool without a shell. Preserve exit status and stderr as evidence."""
    if not shutil.which(command[0]):
        checks.append(Check(identifier, requirement, "BLOCKED", f"Required executable unavailable: {command[0]}"))
        return
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        evidence.append({"id": identifier, "argv": command, "exit_code": completed.returncode,
                         "stdout": completed.stdout, "stderr": completed.stderr})
        checks.append(Check(identifier, requirement, "PASS" if completed.returncode == 0 else "FAIL",
                            f"Exit {completed.returncode}; see command evidence"))
    except (OSError, subprocess.TimeoutExpired) as error:
        checks.append(Check(identifier, requirement, "BLOCKED", str(error)))


def verify_outputs(demo, output, run):
    demo, output, run = Path(demo), Path(output), Path(run)
    checks, evidence = preflight(demo), []
    def receipt():
        data = json.loads((run / "run.json").read_text(encoding="utf-8"))
        if data.get("revision") != REVISION or data.get("exit_code") != 0:
            raise ValueError("Run receipt does not record a successful pinned workflow")
        if data.get("demo_manifest_sha256") != sha256(demo / "manifest.json"):
            raise ValueError("Run input manifest differs from verification input manifest")
        if Path(data.get("output", "")).resolve() != output.resolve():
            raise ValueError("Run receipt names a different output directory")
        if not data.get("finished_at") or not data.get("argv"):
            raise ValueError("Incomplete run receipt")
        return f"Successful pinned run finished {data['finished_at']}; receipt is local provenance, not a signed attestation"
    capture(checks, "RUN-01", "REQ-04", receipt)
    for name in ("wf-aav-qc-report.html", "combined_reference.fa.gz", "combined_reference.fa.gz.fai",
                 "combined_reference.fa.gz.gzi", "execution/trace.txt"):
        capture(checks, "OUT-01:" + name, "REQ-05", lambda name=name: require_file(output / name))
    for sample in SAMPLES:
        for suffix in ("_bam_info.tsv", "_aav_per_read_info.tsv", "_transgene_plasmid_consensus.fasta.gz",
                       "_transgene_plasmid_variants.vcf.gz"):
            file = output / sample / (sample + suffix)
            capture(checks, f"OUT-02:{sample}{suffix}", "REQ-05", lambda file=file: require_file(file))
        capture(checks, f"OUT-03:{sample}", "REQ-06", lambda sample=sample:
                tsv_read_ids(output / sample / f"{sample}_aav_per_read_info.tsv",
                             fastq_ids(demo / "fastq" / sample / "simulated_reads.fq")))
        capture(checks, f"OUT-04:{sample}", "REQ-05", lambda sample=sample:
                f"{len(fasta_records(output / sample / f'{sample}_transgene_plasmid_consensus.fasta.gz'))} consensus sequences")
        bam = output / sample / "tagged_bams/sorted.tagged.bam"
        capture(checks, f"BAM-00:{sample}", "REQ-07", lambda bam=bam: require_file(Path(str(bam) + ".bai")))
        external_check(checks, f"BAM-01:{sample}", "REQ-07", ["samtools", "quickcheck", "-v", str(bam)], evidence)
        external_check(checks, f"BAM-02:{sample}", "REQ-07", ["samtools", "view", "-c", str(bam)], evidence)
        external_check(checks, f"BAM-03:{sample}", "REQ-07", ["samtools", "idxstats", str(bam)], evidence)
        vcf = output / sample / f"{sample}_transgene_plasmid_variants.vcf.gz"
        external_check(checks, f"VCF-01:{sample}", "REQ-08", ["bcftools", "stats", str(vcf)], evidence)
        external_check(checks, f"VCF-02:{sample}", "REQ-08",
                       ["bcftools", "norm", "--check-ref", "e", "--fasta-ref", str(demo / "transgene.fasta"),
                        "--output-type", "v", "--output", str(run / f"{sample}.normalised.vcf"), str(vcf)], evidence)
    checks.append(Check("MAN-01", "REQ-09", "NOT_RUN", "Inspect report and selected alignments; record your biological interpretation in docs/manual-review.md"))
    checks.append(Check("PERF-01", "REQ-10", "NOT_RUN", "Independent truth-set benchmarking is an extension; demo execution alone supplies no accuracy estimate"))
    return checks, evidence


def metrics(truth, predictions):
    """Binary metrics with explicit abstentions. Labels: positive/negative/unclassified."""
    def read(path, allowed):
        values = {}
        with Path(path).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["read_id", "label"]:
                raise ValueError("CSV header must be read_id,label")
            for row in reader:
                key, label = row["read_id"], row["label"]
                if not key or key in values or label not in allowed:
                    raise ValueError("Duplicate/empty ID or unsupported label")
                values[key] = label
        if not values:
            raise ValueError("Empty label table")
        return values
    actual = read(truth, {"positive", "negative"})
    predicted = read(predictions, {"positive", "negative", "unclassified"})
    if set(actual) != set(predicted):
        raise ValueError("Prediction IDs must match truth exactly; represent abstentions explicitly")
    counts = dict(tp=0, tn=0, fp=0, fn=0, unclassified_positive=0, unclassified_negative=0)
    for key, value in actual.items():
        pred = predicted[key]
        if pred == "unclassified":
            counts["unclassified_" + value] += 1
        else:
            counts[{("positive", "positive"): "tp", ("negative", "negative"): "tn",
                    ("negative", "positive"): "fp", ("positive", "negative"): "fn"}[(value, pred)]] += 1
    tp, tn, fp, fn = (counts[key] for key in ("tp", "tn", "fp", "fn"))
    def ratio(a, b):
        return a / b if b else None
    return {"counts": counts, "n": len(actual),
            "sensitivity_on_classified": ratio(tp, tp + fn),
            "specificity_on_classified": ratio(tn, tn + fp),
            "precision_on_classified": ratio(tp, tp + fp),
            "classification_coverage": (tp + tn + fp + fn) / len(actual),
            "positive_detection_rate_all": ratio(tp, tp + fn + counts["unclassified_positive"]),
            "negative_correct_rate_all": ratio(tn, tn + fp + counts["unclassified_negative"]),
            "truth_sha256": sha256(truth), "predictions_sha256": sha256(predictions),
            "interpretation": "Conditional sensitivity/specificity exclude abstentions; read coverage and all-read rates alongside them. Null means undefined."}


def write_report(checks, directory, scope, evidence=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    complete = all(c.status == "PASS" for c in checks) and bool(checks)
    payload = {"created_at": datetime.now(timezone.utc).isoformat(), "scope": scope,
               "all_checks_passed": complete, "checks": [asdict(c) for c in checks]}
    (directory / "report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (directory / "commands.json").write_text(json.dumps(evidence or [], indent=2) + "\n", encoding="utf-8")
    lines = ["# EPI2ME AAV verification evidence", "", f"Scope: **{scope}**", "",
             "This report records the checks below. It is not a clinical validation or regulatory approval.", "",
             "| Check | Requirement | Status | Evidence / limitation |", "|---|---|---|---|"]
    for check in checks:
        detail = check.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {check.id} | {check.requirement} | {check.status} | {detail} |")
    (directory / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    suite = ET.Element("testsuite", name=scope, tests=str(len(checks)),
                       failures=str(sum(c.status == "FAIL" for c in checks)),
                       skipped=str(sum(c.status in ("BLOCKED", "NOT_RUN") for c in checks)))
    for check in checks:
        case = ET.SubElement(suite, "testcase", name=check.id, classname=check.requirement)
        if check.status != "PASS":
            node = ET.SubElement(case, "failure" if check.status == "FAIL" else "skipped", message=check.status)
            node.text = check.detail
        ET.SubElement(case, "system-out").text = check.detail
    ET.ElementTree(suite).write(directory / "junit.xml", encoding="utf-8", xml_declaration=True)
    return 1 if any(c.status == "FAIL" for c in checks) else (2 if not complete else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--archive", type=Path, required=True)
    prep.add_argument("--destination", type=Path, required=True)
    derived = sub.add_parser('derive-baseline')
    derived.add_argument('--source', type=Path, required=True)
    derived.add_argument('--destination', type=Path, required=True)
    pre = sub.add_parser("preflight")
    pre.add_argument("--demo", type=Path, required=True)
    pre.add_argument("--report", type=Path, required=True)
    out = sub.add_parser("outputs")
    out.add_argument("--demo", type=Path, required=True)
    out.add_argument("--output", type=Path, required=True)
    out.add_argument("--run", type=Path, required=True)
    out.add_argument("--report", type=Path, required=True)
    met = sub.add_parser("metrics")
    met.add_argument("--truth", type=Path, required=True)
    met.add_argument("--predictions", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            print(json.dumps(prepare(args.archive, args.destination), indent=2))
            return 0
        if args.command == 'derive-baseline':
            print(json.dumps(derive_baseline(args.source, args.destination), indent=2))
            return 0
        if args.command == "preflight":
            return write_report(preflight(args.demo), args.report, "INPUT CHECKS ONLY - no EPI2ME execution")
        if args.command == "outputs":
            checks, evidence = verify_outputs(args.demo, args.output, args.run)
            return write_report(checks, args.report, "HPC OUTPUT CHECKS - manual review and benchmarking separate", evidence)
        print(json.dumps(metrics(args.truth, args.predictions), indent=2))
        return 0
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
