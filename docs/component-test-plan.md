# Component verification plan and traceability

Version 1, 2026-09-11. Target: upstream `contamination.py`, wf-aav-qc v1.3.1,
commit `43a4266fc30a131c9e2b49654a97a3fd59e41d94`.

This plan describes a component contract inferred from the pinned source and
workflow documentation, not requirements supplied or approved by Oxford Nanopore.
Numeric expectations were recorded in `fixtures/component/cases.json` before
execution. Applicant review of these expectations remains pending.

## Architecture and scope

Full upstream workflow context:

```text
FASTQ -> reference alignment -> alignment summaries + input-read count
                                       |
                              main.nf: contamination
                                       |
                          workflow_glue.contamination.main
                                       |
                         contamination category summary -> report
```

This experiment supplies authored alignment summaries directly at that component
boundary. It runs the upstream CLI, pandas/NumPy operations and native SeqKit
FASTA identifier extraction. It does not mock those dependencies. It does not
run alignment, Medaka, the complete Nextflow workflow or its container.

Python 3.12.14, NumPy 2.2.6, pandas 2.2.3 and SeqKit 2.13.0 were used on Windows.
These are this experiment's dependencies, not a claim to reproduce every
dependency in the original container. Original source and run hashes are in
`upstream/SOURCE.json` and each run's `run.json`.

## Requirements, oracles and results

Evidence root: `evidence/component-20260911-01/`. Each case saves its declared
expectation, exact inputs, output if any, full command and diagnostic.

| Requirement | Acceptance criterion and source | Cases | Recorded result |
|---|---|---|---|
| COMP-01 Counts and denominators | The source counts distinct mapped Read IDs, subtracts from n_reads for unmapped reads, and counts alignment rows per reference category | C01, C04 | PASS |
| COMP-02 Multiple alignments | Adding an alignment for an existing read changes alignment counts but not unique mapped-read count; follows source nunique() | C02 | PASS |
| COMP-03 Order invariance | Reordering the same alignment rows preserves the summary values; project property requirement | C03 | PASS |
| COMP-04 Absent categories | A transgene-only input yields transgene plus mapped/unmapped summary rows; follows source value_counts() behaviour | C05 | PASS |
| COMP-05 Sample identity | Every result row retains the supplied sample_id; follows source assignment | C06 | PASS |
| COMP-06 Required inputs | Missing ReadLen column or missing reference FASTA produces a specific failure and no output | C07, C08 | PASS |
| EXP-01 Empty/zero inputs | Explore diagnostics for no alignments or zero total reads; no upstream acceptance contract asserted | X01, X02 | Both exit 1 with ZeroDivisionError |
| EXP-02 Inconsistent read totals | Explore n_reads below unique mapped count; proposed future guard would reject it | X03 | Exit 0; negative unmapped count and mapped percentage above 100 |
| EXP-03 Unknown reference | Explore an alignment reference absent from category metadata | X04 | Exit 0; extra alignment contributes to denominator but not a named category |

An exploratory observation is not a passed negative test or an established
workflow defect. Confirm upstream preconditions and reachability before any
defect escalation. A nonzero exit caused by environment failure cannot satisfy
an expected-input-failure test.

## Hand calculation to review

C01 has 100 input reads and 95 alignment rows, each with a unique ID: 80
transgene, 10 helper and 5 host. Therefore 95 reads are mapped and 5 unmapped.
The mapped/unmapped percentages use 100 as denominator. Category percentages
use 95: 84.21%, 10.53%, 5.26% after rounding.

C02 repeats an existing transgene alignment. There are now 96 alignment rows
but still 95 distinct IDs. Transgene is 81/96 = 84.375%, reported as 84.38%;
helper is 10/96 = 10.42%; host is 5/96 = 5.21%. Mapped/unmapped stay 95%/5%.
Rounded category percentages may sum to 100.01%; this is a rounding effect.

The upstream TSV labels both summary types with the same columns, including
`Number of alignments`. Explain that its Mapped and Unmapped rows contain read
counts; summing those rows together with reference categories double-counts.

## Validator benchmark

`fixtures/validator/cases.json` declares 20 cases and truth labels before
`fastq_ids` is executed. Positive means a malformed file under the project's
restricted four-line A/C/G/T/N, Phred+33 dialect. Negative means conforming.
One file is one classification unit, not one read or one patient.

Recorded result: TP=12, FN=0, TN=8, FP=0, abstentions=0. Sensitivity=12/12;
specificity=8/8; classification coverage=20/20. The metric API's `read_id` column
contains case IDs for this exercise. Labels are independent of the returned
prediction, but these are authored cases related to the unit-test suite, not a
held-out external benchmark. Do not report these numbers as EPI2ME or clinical
accuracy. Nonstandard FASTQ dialects are outside this benchmark.

## Sequencing-file tool extension

FILE-01: convert a known SAM to BAM, sort/index it, fully decode three records
and verify two mapped plus one unmapped. FILE-02: parse a known VCF and check
REF=A at position 17 against a 100-base reference. FILE-03: verify detection of
a removed BAM EOF marker and an incorrect VCF reference allele.

`run_file_checks.py` invokes the real samtools/bcftools executables and saves
versions and diagnostics. Both were unavailable in the current Windows PATH;
the local report honestly records BLOCKED. The synthetic SAM/VCF files are not
EPI2ME outputs, and no aligner or variant caller is being benchmarked. A BAM
quickcheck alone does not establish all internal records are uncorrupted.

## Evidence review and release

Run receipts are local provenance, not signed attestations. New runs require new
directories, preserving original results. Preserve environment errors, unusual
outputs and failed evidence. Review every non-pass and at least C01/C02/X03
before publishing a case study. CI is prepared but not executed remotely.
