# Analysis risks and document control

Status: technical risk review; proposed controls require review in the intended
use context. This is not an approved medical-device risk file.
No clinical sample or release decision was made.

| Failure or misuse | Plausible consequence within the analysis | Control / evidence | Current status |
|---|---|---|---|
| Count alignments as unique reads | Misleading mapped-read percentage | Distinct-ID calculation; C02 challenges a repeat alignment | Verified at component boundary |
| Supply an inconsistent total-read count | Negative counts or percentages above 100 may be misinterpreted | Validate metadata and output ranges; OBS-002 | Proposed control; implementation pending |
| Ignore a missing reference category | An incomplete contamination breakdown may look complete | Validate reference-category coverage and examine X04 | Investigation pending |
| Treat any nonzero exit as a passed negative test | A missing dependency could be mistaken for correct input rejection | Check the specific diagnostic and absence of output; evidence-grader tests | Executed |
| Report mock/blocked work as execution | Unsupported execution or performance claim | Real subprocess receipts; explicit BLOCKED statuses | Used throughout this package |
| Present synthetic validator scores as clinical accuracy | Overstated applicability to patient or production data | Declare unit, truth, dialect and population limits with metrics | Documented; technical review pending |
| Modify source/inputs after testing | Results no longer describe the distributed files | Pinned source, hashes and new run directories | Recorded; unsigned local evidence |

Priorities should be reviewed in the intended use context. No patient-risk
probabilities, clinical severities or acceptability thresholds are invented here.

## Standards orientation

- [IEC 62304](https://webstore.iec.ch/en/publication/6792): medical-device
  software lifecycle processes. This project records links between a software
  item, requirements, verification and problem records.
- [ISO 14971](https://www.iso.org/standard/72704.html): medical-device risk
  management. The table records failure/consequence/control/evidence relationships.
- [ISO 13485](https://www.iso.org/standard/59752.html): quality-management-system
  requirements. The package records document versions, provenance and review
  status; a repository alone is not such a quality system.

These notes use public publisher descriptions, not a clause-by-clause standards
assessment. Full standards study, organisational procedures and professional
review are outside the executed evidence.

## Technical review record

- Reviewer and actual date:
- C01/C02 calculations independently checked:
- X03 reproduced and scope understood:
- Biological interpretation and limitations explained:
- Any peer feedback, exact changes and evidence:
- Evidence acceptance decision and excluded/private material:

Reviewer identity, review date, findings and acceptance decision are recorded
only after the review is performed. No approval is implied by an empty record.
