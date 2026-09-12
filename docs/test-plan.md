# Verification plan, version 0.1

Status: design prepared; HPC execution and manual review pending.

Purpose: evaluate selected observable behaviours of upstream wf-aav-qc v1.3.1
on the pinned public simulated demo. The harness is the portfolio contribution.
Oxford Nanopore authored the workflow. This is not a medical device or a
regulatory submission. Standards-related documents are learning exercises.

The sample set is sample_1 and sample_2, each with 10,440 simulated reads in the
reviewed archive. The read identifiers are reused across the two samples;
membership checks alone cannot detect swapping these similar samples. Inputs
are tracked per file with SHA256. A distinct, independently labelled sample
control is needed to extend identity assurance.

OBS-001 records one malformed sample_1 read found during local checks. The HPC
baseline uses a separate derived dataset after quarantining that exact record:
10,439 reads in sample_1 and 10,440 in sample_2. Original failed evidence is
preserved. See observation-001.md and data/baseline/manifest.json for provenance.

| Requirement | Acceptance criterion | Test / evidence | Initial status |
|---|---|---|---|
| REQ-01 Input provenance | Reviewed archive hash and every selected input hash match | IN-01, workflow.lock.json, data/demo/manifest.json | Local check available |
| REQ-02 FASTQ integrity | Nonempty four-line records, legal bases/qualities, equal lengths, unique IDs within sample | IN-02, harness corruption tests | Local check available |
| REQ-03 Reference consistency | Unique nonempty FASTA IDs; demo ITR bounds ordered and within sequence | IN-03, IN-04 | Local check available |
| REQ-04 Reproducible execution | Clean pinned source, recorded versions, container hashes and actual successful exit | RUN-01, run.json, console.log | NOT_RUN |
| REQ-05 Expected outputs | Report, references, trace, per-sample tables, consensus and VCF present; consensus readable | OUT-01, OUT-02, OUT-04 | NOT_RUN |
| REQ-06 Sample output membership | Each structure-table read belongs to its stated sample input | OUT-03; limited by shared input IDs | NOT_RUN |
| REQ-07 BAM integrity | Required index present; quickcheck, full record decoding and index-statistics commands exit zero | BAM-00 through BAM-03 | NOT_RUN |
| REQ-08 VCF integrity | bcftools stats parses the VCF and REF alleles agree with the unmasked transgene reference | VCF-01, VCF-02 | NOT_RUN |
| REQ-09 Biological interpretation | Explain coverage, classification, contaminants and selected alignments with cited output evidence | MAN-01, manual-review.md | NOT_RUN |
| REQ-10 Accuracy methodology | Independently labelled truth, defined positive class, complete ID join and explicit abstentions | PERF-01, metrics command | Calculator tested; workflow benchmark NOT_RUN |
| REQ-11 Invalid input handling | Missing input fails because the file is absent, with an informative diagnostic | missing-input case; manually inspect console.log | NOT_RUN |
| REQ-12 Unknown parameter handling | Deliberate unknown option is rejected for the intended reason | unknown-parameter case; manually inspect console.log | NOT_RUN |

## Test execution order

1. Execute harness tests and derived-baseline preflight. Preserve the original
   demo's known FAIL as OBS-001; resolve any new FAIL before submission.
2. Run the baseline on Eddie and preserve the complete runs/<ID> folder.
3. Review generated verification report and external-command evidence. Missing
   tools are BLOCKED; MAN-01 and PERF-01 remain NOT_RUN until evidence exists.
4. Submit missing-input and unknown-parameter cases separately. A nonzero exit
   is insufficient: confirm the diagnostic identifies the intended fault.
5. Perform manual review. Record deviations and link a real fix if warranted.
6. Write a final two-page case study using measured results, explaining any
   failed or unexecuted checks. Keep the original machine report unchanged.

## Scope boundaries

BAM checks are structural checks, not proof of biological correctness.
The AAV structure TSV contains transgene-assigned reads only; it is not a count
of all input reads and cannot alone provide contamination sensitivity or
specificity. No accuracy threshold is asserted for this unvalidated demo.
Zero variants in a VCF is not automatically a failure. No attempt is made to
prove clinical validity, large-cohort performance, de novo assembly accuracy,
ISO compliance, or hands-on Jama/MasterControl experience.

The upstream output definition is conditional: the combined BAM is expected
under this project's default output_genometype_bams=false. Optional per-type
BAMs and IGV configuration are not universally required.

## Negative input policy

Never modify the pinned demo to create a failure case. The runner uses a missing
path or an extra invalid parameter in a new run directory. Deliberate faults
are not reported as discovered defects. Timeouts, module failures and absent
containers are environment problems until evidence establishes otherwise.
