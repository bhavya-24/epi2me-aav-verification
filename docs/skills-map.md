# Evidence mapped to the Bioinformatics Software Test Engineer advert

Oxford Nanopore, job 3193. This map uses the advert supplied by the applicant;
it is not a statement that the role is currently open. Updated 2026-09-12.

The advert lists a relevant MSc/equivalent, communication and willingness to
learn as essential. Specialist technical and regulatory experience is desirable.
This portfolio supplies selected technical evidence; education and previous
experience should be supported separately in the application.

| Advert area | Evidence available in this project | Boundary / next evidence needed |
|---|---|---|
| Write and execute software test plans | [Component plan](component-test-plan.md), 8 passing contract checks, 4 exploratory probes | Criteria inferred from source/project properties, not approved product requirements |
| Automated EPI2ME testing | [Actual component report](../evidence/component-20260911-01/report.md), Python harness and 28 passing unit tests | Only the contamination component executed; full Nextflow run pending |
| Manual testing and review | Inputs, expectations, outputs and [review record](component-risk-review.md) | Applicant/peer review has not been completed |
| Record verification activities | JSON receipts, JUnit, Markdown reports, versions and hashes | Local provenance, not signed or externally audited evidence |
| Requirements / architecture / software-unit traceability | [COMP-01–COMP-06 matrix and component boundary](component-test-plan.md) | Portfolio traceability exercise; not a product DHF |
| Analytical insight and attention to detail | [C01/C02 denominator calculations](component-case-study.md), [X03 investigation](observation-002.md), original FASTQ anomaly | Applicant should reproduce and explain the findings |
| Sensitivity and specificity | [20-file validator challenge](../evidence/validator-20260911-01/report.md), declared truth and predictions | Authored FASTQ validation cases, not clinical or EPI2ME accuracy |
| Sequencing file formats / samtools / bcftools | FASTQ validation executed; known SAM/BAM/VCF exercise prepared | [Both external tools blocked locally](../evidence/file-tools-local-20260911-01/report.md); actual tool runs pending |
| Long-read / biopharma workflows | AAV QC context and pinned EPI2ME source inspection | Does not establish broad biopharma or clinical expertise |
| Programming and learning new tools | Python verification code and real NumPy/pandas/SeqKit execution | AI assistance disclosed; personal code walkthrough and reproduction still needed |
| Risk management / IEC 62304 / ISO 14971 / ISO 13485 | [Failure-control-verification relationships](component-risk-review.md) and versioned documentation | Educational exercise; no professional SaMD, accreditation or compliance claim |
| GAMP5 / clinical diagnostic environment | No direct completed evidence | Training or relevant experience needed; not inferred from the risk document |
| MasterControl / Jama / Jira / Monday.com | Not used | A GitHub repository is not proof of proficiency in these tools |
| Large genomic datasets / alignment / assembly | Not demonstrated by these small component fixtures | Separate project or previous experience needed |
| Communication and collaboration | Case study and reproducible investigation for review | Written artifacts support discussion; cross-functional collaboration is not yet demonstrated |
| Independent work in a time-critical environment | Dated work records and documented setup blockers | Explain actual personal decisions and learning; AI-generated material alone is insufficient |

The most useful next contribution is a dated personal review of C02 and X03:
reproduce each, explain the denominator difference, and describe what must be
checked before calling X03 a complete-workflow defect. Do not prefill the review
as completed or present pending tools as mastered.
