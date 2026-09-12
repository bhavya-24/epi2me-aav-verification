# EPI2ME AAV verification evidence

Scope: **INPUT CHECKS ONLY - no EPI2ME execution**

This report records the checks below. It is not a clinical validation or regulatory approval.

| Check | Requirement | Status | Evidence / limitation |
|---|---|---|---|
| IN-01 | REQ-01 | PASS | All six selected input files match the prepared SHA256 manifest |
| IN-02:sample_1 | REQ-02 | PASS | 10439 unique valid reads |
| IN-02:sample_2 | REQ-02 | PASS | 10440 unique valid reads |
| IN-03:transgene.fasta | REQ-03 | PASS | 1 nonempty reference sequences |
| IN-03:helper.fasta | REQ-03 | PASS | 1 nonempty reference sequences |
| IN-03:repcap.fasta | REQ-03 | PASS | 1 nonempty reference sequences |
| IN-03:cell_line.fasta.gz | REQ-03 | PASS | 1 nonempty reference sequences |
| IN-04 | REQ-03 | PASS | Reviewed demo coordinates fit; reference identifiers are unique. Coordinate convention inherited from upstream demo. |
