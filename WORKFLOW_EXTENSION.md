# Full Nextflow workflow extension: prepared, execution pending

This preserves the original end-to-end project plan. For the completed local
component work and the current evidence overview, start with [README.md](README.md).
The steps below are future work; their presence does not indicate successful
execution.

**Local component version executed on 2026-09-11:** eight contract checks passed
against the real pinned EPI2ME contamination component; four exploratory probes
were recorded. The harness now has 28 passing tests. Start with
[LOCAL_START.md](LOCAL_START.md) and the
[case study](docs/component-case-study.md). A separate 20-file challenge set
tested the local FASTQ validator. Full Nextflow execution is still pending.

[OBS-002](docs/observation-002.md) records a component-level metadata consistency
finding with its precise limits. samtools/bcftools are not available locally;
their real-tool exercise is prepared with an alternative Eddie installer.

## Original end-to-end workflow extension

An end-to-end verification extension for the bioinformatics workflow
Oxford Nanopore's `wf-aav-qc` v1.3.1, pinned to commit
`43a4266fc30a131c9e2b49654a97a3fd59e41d94`.

**Current state: verification code and Eddie scripts prepared. Local harness
and input-check results are in `evidence/local-checks.md`. The EPI2ME workflow
has not been executed by this project. No clinical accuracy or compliance
claims have been established.**

The workflow performs AAV preparation QC. This project contributes input
validation, output verification, controlled failure tests, traceability and a
reviewable evidence package. The official demo contains simulated reads, not
patient samples. Development attribution is recorded in NOTICE.md. Technical review and
full-workflow execution remain pending.

**Real finding:** the original demo has one non-nucleotide `q` in sample_1.
The failed input-check report is preserved. A documented derived baseline
quarantines that one read; see [OBS-001](docs/observation-001.md). This is an
input-data finding; the downstream workflow's response is still untested.

## First day: run and inspect the workflow

1. Copy this project folder to your approved Eddie project/scratch storage,
   using a path without spaces. Keep `cache`, `data` and `runs` out of your
   small home quota. The source demo archive is 116,723,422 bytes; containers
   and intermediates require additional space. Follow your storage retention
   policy and preserve selected evidence in durable storage.
2. From the project root, inspect the available modules:

   ```bash
   module avail igmm/apps/nextflow
   module avail singularity
   module avail python
   ```

   On 2026-09-10 the user's Eddie account listed Nextflow 24.04.4, Singularity
   4.3.4 and Python 3.12.9. These exact modules are now selected by default.
   The user's subsequent terminal output confirmed successful version checks
   for all three; EPI2ME workflow execution remains pending.
   If your group uses other modules or versions, create
   `hpc/site-setup.local.sh` containing your working `module load` commands.
   Python must be at least 3.10. The upstream manifest requires Nextflow at
   least 23.04.2; actual runtime versions are captured in the run receipt.
   The selected Nextflow version meets the upstream minimum.
3. On a node permitted for downloads and container preparation, run:

   ```bash
   bash scripts/prepare-runtime.sh
   ```

   This retrieves pinned source, three upstream containers and the demo if
   absent. It verifies the archive checksum, extracts only six selected inputs
   and records their hashes. It preserves those originals in `data/demo` and
   creates `data/baseline` with the documented one-read quarantine. It does
   not submit a job. Site network policies
   may require a transfer/interactive node; do not assume compute-node egress.
4. Submit from the project root:

   ```bash
   qsub hpc/eddie.qsub
   ```

   The script requests **16 sharedmem slots, 4G h_vmem per slot (64G total),
   and four hours**. These are project choices, not measured requirements.
   Nextflow executes locally *inside* this allocation with a smaller resource
   budget, so it does not attempt nested qsub submissions. Singularity uses
   local prepared images. Queue wait, downloads and setup are additional time.
5. Inspect `runs/<ID>/console.log`, `run.json` and
   `verification/report.md`. A run receipt is written before execution and
   updated only after the process exits; a killed job cannot acquire a success
   receipt. An exit status of **2** from the runner means manual/benchmark
   evidence is still incomplete. It is not a claim that all checks passed.

## Second day: failure cases and your interpretation

After a successful baseline, submit these separately:

```bash
qsub -v AAV_CASE=missing-input hpc/eddie.qsub
qsub -v AAV_CASE=unknown-parameter hpc/eddie.qsub
```

Review each actual error using `docs/manual-review.md`. A nonzero exit is not
enough to count as a passed negative test. Complete the biological review,
link evidence in `docs/traceability.csv`, and write a short case study. Keep
the generated report unchanged and add your signed/date-stamped review beside
it. No signatures, reviews, defects or successful runs are prefilled.

The full test design is in [docs/test-plan.md](docs/test-plan.md). The
[project scope](docs/project-scope.md) identifies coverage and remaining gaps.

## Local checks (no HPC or paid services)

```bash
python -B -m unittest discover -s tests -v
python verify_aav.py prepare --archive data/wf-aav-qc-demo.tar.gz --destination data/demo
python verify_aav.py derive-baseline --source data/demo --destination data/baseline
python verify_aav.py preflight --demo data/baseline --report evidence/my-preflight
```

Skip preparation/derivation when their destination already exists. The original
demo intentionally remains unchanged and fails the documented FASTQ check.
Evidence directories must
be new; the tool refuses to overwrite previous reports. The harness uses only
Python's standard library. BAM/VCF tools execute inside the upstream container
on Eddie using the wrappers in `scripts/`. CI tests the harness and shell
syntax; it does not run the EPI2ME pipeline.

## Accuracy extension: explicit truth and abstentions

Use an independently labelled controlled dataset, define the positive class
(for example contaminant origin), document how predictions are obtained from
alignment/classification outputs, and produce two CSVs:

```text
read_id,label
read001,positive
read002,negative
```

Predictions permit `positive`, `negative`, or `unclassified`. Every truth ID
must appear exactly once in predictions; missing IDs are an error, not silent
exclusions. Then run:

```bash
python verify_aav.py metrics --truth truth.csv --predictions predictions.csv > metrics.json
```

Report the confusion counts, classification coverage, conditional sensitivity
and specificity, and all-read correct-detection rates together. Undefined
metrics are null. Hand-calculated synthetic fixtures test the calculator;
these are not measured workflow accuracy. Do not use the transgene-only
structure table as if it contained every contaminant read. Do not infer truth
from the same workflow being evaluated. The optional controlled dataset and
its biological benchmark are not supplied or executed in this first version.

## Evidence retention

- Technical overview and requirement-to-test links.
- Actual baseline report and command evidence, with HPC usernames/paths
  redacted in the public copy where needed.
- One genuinely investigated observation or defect; an intentional failure
  must be labelled a controlled test.
- Manual biological interpretation and limitations.
- Small tests and source code. Do not upload the whole work directory, caches,
  raw datasets or unrelated private documents. Keep new execution results in
  separately dated directories and retain their original status.

## Sources and attribution

- [Pinned workflow source](https://github.com/epi2me-labs/wf-aav-qc/tree/43a4266fc30a131c9e2b49654a97a3fd59e41d94)
- [EPI2ME documentation](https://epi2me.nanoporetech.com/epi2me-docs/workflows/wf-aav-qc/)
- [nf-core Eddie configuration guidance](https://nf-co.re/configs/eddie/)
- [University of Edinburgh Eddie resource](https://digitalresearchservices.ed.ac.uk/resources/eddie)

The nf-core page includes historical guidance; the setup here uses only its
documented SGE/Singularity and module-name conventions. It does not import the
nf-core profile into EPI2ME. Confirm current module availability with Eddie.
Files in `upstream/` are unmodified inspection snapshots under the included
Oxford Nanopore licence, not locally authored code. Container SIF hashes are
recorded on first download; upstream image tags themselves are not immutable
registry digests. The downloaded runtime and full workflow need HPC validation.
