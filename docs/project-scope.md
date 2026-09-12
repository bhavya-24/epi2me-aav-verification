# Project scope and architecture

This project verifies selected behaviours of the `wf-aav-qc` contamination-summary
component using small, controlled alignment tables. It checks counts,
denominators, reference categories, sample identity and failure diagnostics.

## Component boundary

The upstream workflow aligns sequencing reads before producing alignment
summaries. This test suite supplies those summaries directly to the pinned
`workflow_glue.contamination` CLI. NumPy, pandas and native SeqKit run normally;
the upstream component is not replaced by a mock.

The source is pinned to `wf-aav-qc` v1.3.1, commit
`43a4266fc30a131c9e2b49654a97a3fd59e41d94`. Source bytes, fixtures, declared
expectations, commands and outputs are linked through SHA256 manifests.

## Verification layers

| Layer | Purpose | Entry point / evidence |
|---|---|---|
| Harness unit tests | Check validators, metrics and result assessment | `tests/` |
| Component contracts | Compare the real component with declared expectations | `run_component.py`, C01–C08 |
| Exploratory inputs | Record behaviours where the valid-input contract needs review | `run_component.py`, X01–X04 |
| FASTQ validation benchmark | Classify 20 authored files with declared truth | `run_validator_benchmark.py` |
| SAM/BAM/VCF checks | Exercise real file tools using known synthetic records | `run_file_checks.py` |
| Full workflow extension | Run the pinned Nextflow workflow in an Eddie allocation | `run_workflow.py`, `hpc/eddie.qsub`; execution pending |

## Evidence model

Each run has its own directory. Expectations are declared before component
execution. Results include commands, exit codes, diagnostic output and hashes.
PASS, FAIL, BLOCKED and OBSERVATION represent different outcomes. Review records
are completed separately from machine-generated evidence.

Historical reports retain their original execution dates. See
[PUBLIC_EXPORT.md](../PUBLIC_EXPORT.md) for path anonymisation and editorial
changes in the distributed copy. Review-label changes do not change a test's
assessment or imply that a review took place.

## Limits

The component suite does not execute alignment, assembly, variant calling or
the complete Nextflow report. The 20-file benchmark evaluates a restricted
FASTQ dialect on authored examples; it does not estimate population-level or
clinical accuracy. Risk notes describe analysis failure modes and proposed
controls, not an approved medical-device risk file.

The [test plan](component-test-plan.md) defines the acceptance criteria and
traceability. [OBS-002](observation-002.md) records the main metadata
investigation. [LOCAL_START.md](../LOCAL_START.md) gives reproduction commands.
