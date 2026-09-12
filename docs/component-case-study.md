# EPI2ME AAV QC component verification

Draft for applicant review. Prepared 2026-09-11 with Codex assistance.

## Problem and purpose

AAV preparation QC uses mapped reads to summarise transgene and non-transgene
material. An incorrect denominator or metadata mismatch can make a plausible
looking report misleading. This work sample tests selected behaviours of
Oxford Nanopore's actual `wf-aav-qc` contamination-summary component, focusing
on counts, denominators, sample identity and failure evidence.

The test target is v1.3.1, commit
`43a4266fc30a131c9e2b49654a97a3fd59e41d94`. The source was preserved unchanged
with its licence and SHA256 hashes. The component ran on Windows with Python
3.12.14, NumPy 2.2.6, pandas 2.2.3 and SeqKit 2.13.0. This environment is not a
reconstruction of the complete upstream container.

## Method and measured results

Small authored alignment tables and reference metadata exercised the upstream
CLI directly. Expected values were declared before execution. Eight contract
checks covered a known mixture, duplicate alignments, input order, all-mapped
and transgene-only inputs, sample identity, a missing column and a missing
FASTA. Four separate exploratory probes investigated empty inputs, zero read
counts, inconsistent totals and an unknown reference category.

All eight contract checks passed. Four probes produced saved observations.
The local test harness also passed 28 unit tests, including checks that prevent
an unrelated nonzero exit, a stale output or a non-finite percentage being
accepted as correct verification evidence.

| Measure | Baseline C01 | Repeat-alignment C02 |
|---|---:|---:|
| Total input reads | 100 | 100 |
| Alignment rows | 95 | 96 |
| Distinct mapped reads | 95 | 95 |
| Mapped / unmapped percentages | 95% / 5% | 95% / 5% |
| Transgene alignments | 80 | 81 |
| Transgene share of alignment rows | 84.21% | 84.38% |

The repeated alignment changes the alignment denominator but not the number
of mapped reads. Reference-category proportions therefore cannot be interpreted
as proportions of all input reads. The Mapped/Unmapped rows in the TSV contain
read counts despite sharing a column title with the alignment categories.

## Investigation: a successful exit with an impossible percentage

In X03, the supplied input count was deliberately set to 94 while the table
contained 95 distinct mapped reads. The component exited successfully and
reported -1 unmapped read, -1.0638297872340425% unmapped and
101.06382978723404% mapped. The calculation subtracts the distinct mapped
count from the supplied total without a local consistency guard.

This is confirmed component behaviour under inconsistent metadata. It is not
yet an established full-workflow bug: upstream count-generation and sample
filtering may prevent the condition. Proposed controls are to reject inconsistent
metadata with a clear diagnostic and verify nonnegative counts and read
percentages between zero and 100. Those controls are not implemented in this
version. No bug report or fix has been submitted upstream.

X01/X02 raised ZeroDivisionError for empty alignments/zero total reads. X04
counted an alignment to an unlisted reference in the denominator without a
matching named category. Their valid-input contracts and workflow reachability
also require review.

## Metrics, documentation and limits

A separate challenge benchmark assessed this project's FASTQ validator on
20 labelled files: 12 malformed and 8 valid under its four-line A/C/G/T/N,
Phred+33 dialect. It produced TP=12, FN=0, TN=8, FP=0 and no abstentions;
sensitivity 12/12 and specificity 8/8. These authored examples demonstrate
metric calculation and validator behaviour, not population-level accuracy,
EPI2ME accuracy or clinical performance.

The package includes a requirement-to-component-to-test matrix, a risk and
document-control learning exercise, source and input hashes, machine-readable
results and a proposed investigation follow-up. Real samtools/bcftools exercises
are prepared but locally BLOCKED; neither tool is available in the current
Windows PATH. A project-local Linux installer is provided for Eddie because
the user's module search found neither tool.

No full Nextflow workflow, external CI run, aligner/variant-caller benchmark,
clinical validation or regulatory approval has been completed. Professional
SaMD experience and named commercial-tool proficiency are not inferred from
these documents. Applicant and peer review remain pending.

## Evidence navigation

- `evidence/component-20260911-01/`: eight checks and four probes, with receipts.
- `evidence/validator-20260911-01/`: declared truth, predictions and metrics.
- `evidence/file-tools-local-20260911-01/`: explicit blocked tool status.
- `docs/component-test-plan.md`: architecture, calculations and traceability.
- `docs/observation-002.md`: reproduction and proposed follow-up.
- `docs/component-risk-review.md`: controls and an unfilled review record.

Upstream: https://github.com/epi2me-labs/wf-aav-qc/tree/43a4266fc30a131c9e2b49654a97a3fd59e41d94
