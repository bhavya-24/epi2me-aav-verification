# Reproduce the EPI2ME component checks

Use Python 3.12 on Windows or Linux x86-64. Open a terminal in the repository
root, where `run_component.py` is located. Setup downloads Python dependencies
and a fixed SeqKit release; the component cases use included synthetic fixtures.
These instructions do not require the large demo dataset or containers.

## Windows PowerShell

For a fresh clone, create the project environment and install tools:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-component.txt
& .\.venv\Scripts\python.exe scripts/setup-component.py
```

Skip setup if this project's environment and SeqKit are already installed.
Run a single case, then reproduce the metadata observation:

```powershell
$caseRun = Get-Date -Format 'yyyyMMdd-HHmmss'
& .\.venv\Scripts\python.exe run_component.py --case C02 --report "evidence/my-C02-$caseRun"
& .\.venv\Scripts\python.exe run_component.py --case X03 --report "evidence/my-X03-$caseRun"
```

Run the full suite:

```powershell
$caseRun = Get-Date -Format 'yyyyMMdd-HHmmss'
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe run_component.py --report "evidence/component-$caseRun"
& .\.venv\Scripts\python.exe run_validator_benchmark.py --report "evidence/validator-$caseRun"
```

## Linux Bash

For a fresh clone:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-component.txt
.venv/bin/python scripts/setup-component.py
```

Run the same individual cases and full suite:

```bash
case_run=$(date -u +%Y%m%dT%H%M%SZ)
.venv/bin/python run_component.py --case C02 --report "evidence/my-C02-$case_run"
.venv/bin/python run_component.py --case X03 --report "evidence/my-X03-$case_run"
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python run_component.py --report "evidence/component-$case_run"
.venv/bin/python run_validator_benchmark.py --report "evidence/validator-$case_run"
```

The SeqKit installer verifies its downloaded archive against the pinned release
asset digest and writes inside `cache/component-tools`. It does not change the
system PATH. The runner verifies the included upstream source hashes and the
SeqKit executable hash before executing the original CLI.

## Interpret the evidence

1. **C02:** expect PASS. Compare `inputs/alignments.tsv`, `expectation.json` and
   `output.tsv`. Explain why 96 alignment rows represent 95 mapped reads.
2. **X03:** expect OBSERVATION. Inspect the negative unmapped count and the
   successful exit in `receipt.json`. This records exploratory behaviour;
   it is not a passed contract or proof of a complete-workflow bug.
3. **Full component run:** the reference run contains eight passing contracts
   and four exploratory observations. A changed outcome should be investigated.
4. **Validator benchmark:** the reference result is TP=12, TN=8, FP=0, FN=0
   for 20 authored FASTQ files. These are not clinical/EPI2ME performance metrics.

Use a new report directory for every run. The tools refuse to overwrite an
existing report. Preserve generated evidence and put interpretation in a
separate dated review, using `docs/component-risk-review.md` as a starting point.

## Optional: samtools/bcftools on Eddie

This extension has not executed on Eddie. Neither tool
was found in the local Windows PATH, and the Eddie module search showed no
matching modules. The local report records BLOCKED.

Transfer the project to approved scratch storage. On Eddie, from that project
directory, request an interactive session:

```bash
qlogin -pe interactivemem 4 -l h_vmem=4G
```

Once the allocation opens, return to the same project directory if necessary:

```bash
module load python/3.12.9
set -o pipefail
python3 scripts/setup-file-tools.py 2>&1 | tee "file-tools-setup-$(date -u +%Y%m%dT%H%M%SZ).log"
echo "Setup exit status: ${PIPESTATUS[0]}"
```

Continue only if setup succeeds. The installer uses a checksum-pinned
Micromamba 2.9.0-0 executable to install samtools 1.22 and bcftools 1.22 into
`cache/file-tools-env`, with the resolved package list recorded. Network access
is required. It does not modify shell profiles or need a Singularity image.

Exit the interactive allocation. From the project root on the login node:

```bash
qsub hpc/file-checks.qsub
```

That script requests one slot, 4 GB and 15 minutes. It captures actual versions,
results and diagnostics. The known SAM/BAM/VCF exercise tests file handling;
it does not benchmark an aligner or variant caller. Full Nextflow instructions
are in [WORKFLOW_EXTENSION.md](WORKFLOW_EXTENSION.md).

## CI and public evidence

GitHub Actions is configured for Windows and Linux component checks and Linux
file-tool checks. The dated local snapshot predates remote CI. Inspect the current Actions run
and its uploaded artifacts for each platform; file-tool verification has an
open failure from the first Linux CI run.

New local logs contain local paths. Keep an unchanged original and remove
personal path prefixes only in a clearly labelled public copy, recording both
original and public hashes. Do not stage new run directories without inspecting
their contents.
