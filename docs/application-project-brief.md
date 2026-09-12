# Project brief: EPI2ME AAV QC component verification

Prepared 2026-09-11 against the job description supplied by the applicant.
This is a proposed work sample, not a record of completed verification.

## Decision

Extend this existing project with direct verification of the pinned upstream
`wf-aav-qc` contamination-summary component. Pair it with small sequencing-file
checks and a documented verification report. Preserve the current harness,
input-data investigation and unexecuted HPC plan.

The application version starts with component execution on Windows using
Python, NumPy, pandas and a native SeqKit executable. It does not depend on
successfully building the full Singularity image. The complete Nextflow run is
a separate extension and must remain unexecuted in the evidence until it runs.

Upstream target: `bin/workflow_glue/contamination.py`, commit
`43a4266fc30a131c9e2b49654a97a3fd59e41d94` of
https://github.com/epi2me-labs/wf-aav-qc . Preserve upstream attribution, licence,
source hashes and actual dependency versions. Installing different dependencies
from the upstream container limits the conclusions to the recorded environment.

## Why this fits the advert

The essential criteria in the supplied advert are a relevant MSc or equivalent
background, communication/interpersonal skills, and willingness to learn.
Specialised SaMD, regulatory and genomic-analysis experience is desirable.
The project supplies evidence for selected duties and desirable skills; it does
not replace qualifications, work experience or employer assessment.

| Advert requirement | Work to perform | Reviewable evidence |
|---|---|---|
| EPI2ME manual and automated testing | Execute the actual component with small controlled inputs; manually calculate selected expected results | Source revision, input fixtures, expectations, tests and execution logs |
| Requirements-based test plans | Define requirements and normal, boundary and invalid-input cases before execution | Test plan with acceptance criteria and requirement sources |
| Verification reports and recorded testing | Record actual results, failures, blocked checks and versions | Machine-readable results and a concise reviewed report |
| Traceability to software and architecture | Connect each requirement to the Nextflow process, Python component, test and result | Architecture sketch and traceability matrix |
| Biopharma and long-read understanding | Explain transgene, helper, rep-cap and host references; distinguish reads from alignments | Biological interpretation with explicit denominators and limitations |
| FASTQ/BAM/VCF; samtools/bcftools | Run real tools on small known files and deliberately malformed copies | Commands, exit codes, output interpretation and provenance |
| Sensitivity/specificity calculations | Score the input validator on separately labelled valid/malformed challenge cases | Defined positive class and unit, truth, predictions, TP/FP/FN/TN and metrics |
| Risk-management support | Analyse plausible failure, consequence, proposed control and verifying test | Risk register, explicitly a portfolio exercise |
| Verification documents for DHFs | Organise versioned requirements, plan, architecture, results, issues and review | Indexed evidence bundle; no invented approvals or regulated status |
| Communication and collaboration | Explain one result and obtain an actual peer review if possible | Short demonstration and genuine review comments/response |
| Time-critical independent work | Record work performed, decisions and unresolved issues | Actual dated work log |

The validator benchmark demonstrates the metrics method for that tool. It is
not a measurement of EPI2ME contamination-classification, variant-calling or
clinical accuracy. The contamination-summary component produces aggregate
counts; do not reconstruct an invented per-read confusion matrix from them.

The samtools/bcftools stage needs a suitable environment. Check native Eddie
modules first; their availability has not been established. Use scheduled
compute for analyses. Windows WSL was not installed at the last observed check.

## First executable case

Specify 100 input reads: 80 distinct reads aligned to transgene, 10 to helper,
5 to host and 5 unmapped. Supply the component with the 95 mapped summaries,
the independently specified total input count, and reference-category metadata.

Expected mapped reads: 95; unmapped reads: 5. Their percentages are 95% and 5%.
Expected alignment-category percentages are 80/95, 10/95 and 5/95 times 100,
rounded according to the documented output format. They use a different
denominator from the mapped/unmapped read percentages.

Then add another alignment for an existing read. The number of alignment rows
changes, while the unique mapped-read count must remain 95. Define the new
category counts and percentages before execution.

Extend with all-mapped, all-unmapped, reordered input, absent categories, missing
columns and inconsistent total-read metadata. Establish the expected contract
for each case. When upstream documentation does not specify invalid-input
behaviour, record an exploratory observation or proposed requirement rather
than automatically declaring an upstream defect.

## Acceptance criteria for the application version

1. Actual pinned upstream component execution is recorded; mocks are clearly
   separated from integration evidence.
2. At least one nominal case and a duplicate-alignment case have independently
   calculated expected results and saved actual outputs.
3. Normal, boundary and invalid-input tests run and every non-pass is explained.
4. Existing FASTQ checks and any new BAM/VCF checks are labelled with their
   actual scope and execution status.
5. The input-validator benchmark has independent challenge labels, a defined
   positive class, complete truth/prediction pairing and explicit limitations.
6. Each claimed requirement links to inspectable evidence.
7. A two-page case study explains the biological context, one investigation,
   decisions, findings and limitations. A real defect is not required; do not
   invent one. The applicant reviews and can explain all AI-assisted work.

## Skills this project cannot establish alone

- Professional SaMD or clinical diagnostic experience; ISO accreditation or
  compliance. Study IEC 62304, ISO 14971, ISO 13485 and GAMP5 using authorised
  material and describe the resulting documents as learning exercises.
- MasterControl, Jama, Jira or Monday.com proficiency without actual access and
  use. A GitHub issue is not evidence of using those products. Record genuine
  Jira use if available; do not make obtaining every platform an application gate.
- Large genomic datasets and assembly through tiny fixtures. Use verified
  dissertation evidence for those areas.
- Real cross-functional collaboration through fictional review records.

## Final package

One repository containing the runnable tests, small inputs, dependency/source
provenance, expected results, actual reports, traceability and risk documents,
plus the two-page case study and a short demonstration. Keep large caches,
private research data and unrelated application documents out of the public copy.

The current 20 harness tests have passed locally and on Eddie according to the
recorded evidence and applicant terminal output. They do not yet constitute
tests of the upstream contamination component. The component exercise above,
samtools/bcftools checks and full workflow execution remain pending.
