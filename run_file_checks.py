"""Exercise real samtools/bcftools on tiny synthetic files; missing tools are BLOCKED."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
from verify_aav import Check, ROOT, sha256, write_report


def make_fixtures(directory):
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "reference.fa").write_text(">transgene\n" + "ACGT" * 25 + "\n", encoding="ascii")
    (directory / "reads.sam").write_text(
        "@HD\tVN:1.6\tSO:unsorted\n@SQ\tSN:transgene\tLN:100\n"
        "r1\t0\ttransgene\t1\t60\t8M\t*\t0\t0\tACGTACGT\tIIIIIIII\n"
        "r2\t0\ttransgene\t13\t60\t8M\t*\t0\t0\tACGTTCGT\tIIIIIIII\n"
        "r3\t4\t*\t0\t0\t*\t*\t0\t0\tNNNN\tIIII\n", encoding="ascii")
    header = ('##fileformat=VCFv4.2\n##contig=<ID=transgene,length=100>\n'
              '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
              '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSYNTHETIC\n')
    (directory / "valid.vcf").write_text(header + "transgene\t17\t.\tA\tT\t60\tPASS\t.\tGT\t0/1\n", encoding="ascii")
    (directory / "wrong-ref.vcf").write_text(header + "transgene\t17\t.\tC\tT\t60\tPASS\t.\tGT\t0/1\n", encoding="ascii")
    return {p.name: sha256(p) for p in directory.iterdir()}


def run_check(checks, commands, directory, identifier, requirement, argv, expected_text=None, failure_diagnostic=None):
    try:
        result = subprocess.run(argv, cwd=directory, capture_output=True, text=True, timeout=60)
        commands.append({"id": identifier, "argv": argv, "cwd": str(directory), "exit_code": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr})
        if failure_diagnostic:
            passed = result.returncode != 0 and failure_diagnostic.lower() in result.stderr.lower()
        else:
            passed = result.returncode == 0 and (expected_text is None or result.stdout.strip() == expected_text)
        checks.append(Check(identifier, requirement, "PASS" if passed else "FAIL", f"Exit {result.returncode}; see commands.json"))
        return passed
    except (OSError, subprocess.TimeoutExpired) as error:
        checks.append(Check(identifier, requirement, "BLOCKED", str(error)))
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    directory = args.report.resolve()
    if directory.exists() or directory.with_name(directory.name + "-inputs").exists():
        raise SystemExit("Use a new report name; preserve previous evidence")
    working = directory.with_name(directory.name + "-inputs")
    hashes = make_fixtures(working)
    checks, commands, versions = [], [], {}
    samtools, bcftools = shutil.which("samtools"), shutil.which("bcftools")
    if not samtools:
        checks.append(Check("BAM-TOOLS", "FILE-01", "BLOCKED", "samtools executable unavailable"))
    if not bcftools:
        checks.append(Check("VCF-TOOLS", "FILE-02", "BLOCKED", "bcftools executable unavailable"))
    for name, executable in (("samtools", samtools), ("bcftools", bcftools)):
        if executable:
            try:
                result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=30)
                versions[name] = {"path": executable, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
            except (OSError, subprocess.TimeoutExpired) as error:
                versions[name] = {"error": str(error)}
    def run(identifier, requirement, argv, **kwargs):
        return run_check(checks, commands, working, identifier, requirement, argv, **kwargs)
    bam_ready = False
    ref_ready = False
    if samtools:
        ref_ready = run("REF-INDEX", "FILE-02", [samtools, "faidx", "reference.fa"])
        if run("BAM-CONVERT", "FILE-01", [samtools, "view", "-b", "-o", "reads.bam", "reads.sam"]):
            bam_ready = run("BAM-SORT", "FILE-01", [samtools, "sort", "-o", "sorted.bam", "reads.bam"])
        if bam_ready:
            run("BAM-INDEX", "FILE-01", [samtools, "index", "sorted.bam"])
            run("BAM-QUICKCHECK", "FILE-01", [samtools, "quickcheck", "-v", "sorted.bam"])
            run("BAM-COUNT", "FILE-01", [samtools, "view", "-c", "sorted.bam"], expected_text="3")
            run("BAM-MAPPED", "FILE-01", [samtools, "view", "-c", "-F", "4", "sorted.bam"], expected_text="2")
            run("BAM-UNMAPPED", "FILE-01", [samtools, "view", "-c", "-f", "4", "sorted.bam"], expected_text="1")
            run("BAM-STATS", "FILE-01", [samtools, "flagstat", "sorted.bam"])
            bam = (working / "sorted.bam").read_bytes()
            # Remove the complete 28-byte BGZF EOF marker; preserve the good BAM.
            (working / "truncated.bam").write_bytes(bam[:-28])
            run("BAM-TRUNCATION", "FILE-03", [samtools, "quickcheck", "-v", "truncated.bam"], failure_diagnostic="EOF")
    if bcftools:
        run("VCF-STATS", "FILE-02", [bcftools, "stats", "valid.vcf"])
        run("VCF-QUERY", "FILE-02", [bcftools, "query", "-f", "%CHROM\t%POS\t%REF\t%ALT\n", "valid.vcf"],
            expected_text="transgene\t17\tA\tT")
        if ref_ready:
            run("VCF-REF", "FILE-02", [bcftools, "norm", "-c", "e", "-f", "reference.fa", "-Ov", "-o", "normalised.vcf", "valid.vcf"])
            run("VCF-WRONG-REF", "FILE-03", [bcftools, "norm", "-c", "e", "-f", "reference.fa", "-Ov", "-o", "rejected.vcf", "wrong-ref.vcf"],
                failure_diagnostic="Reference allele mismatch")
        else:
            checks.append(Check("VCF-REFERENCE-CHECKS", "FILE-02", "BLOCKED", "Reference index preparation unavailable/failed"))
    status = write_report(checks, directory, "SYNTHETIC FILE-TOOL EXERCISE; not EPI2ME-generated BAM/VCF", commands)
    provenance = {"finished_at": datetime.now(timezone.utc).isoformat(), "versions": versions,
                  "fixture_sha256": hashes, "script_sha256": sha256(ROOT / "run_file_checks.py"),
                  "input_directory": working.name,
                  "limits": "Tiny authored SAM/VCF fixtures; no variant caller or alignment algorithm was evaluated. quickcheck alone does not detect every internal corruption."}
    (directory / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    for check in checks:
        print(check.id, check.status, check.detail)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
