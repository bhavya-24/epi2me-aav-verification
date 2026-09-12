# EPI2ME contamination component verification

Executed upstream Python component with real native SeqKit. Synthetic alignment tables; no full Nextflow run.

Contract checks are assessed against declared expectations. Exploratory probes record behaviour without declaring an upstream defect.

| Case | Requirement | Assessment | Detail |
|---|---|---|---|
| [C01](C01/receipt.json) | COMP-01 | PASS | Exact categories/counts, expected percentages and sample identity confirmed |
| [C02](C02/receipt.json) | COMP-02 | PASS | Exact categories/counts, expected percentages and sample identity confirmed |
| [C03](C03/receipt.json) | COMP-03 | PASS | Exact categories/counts, expected percentages and sample identity confirmed |
| [C04](C04/receipt.json) | COMP-01 | PASS | Exact categories/counts, expected percentages and sample identity confirmed |
| [C05](C05/receipt.json) | COMP-04 | PASS | Exact categories/counts, expected percentages and sample identity confirmed |
| [C06](C06/receipt.json) | COMP-05 | PASS | Exact categories/counts, expected percentages and sample identity confirmed |
| [C07](C07/receipt.json) | COMP-06 | PASS | Expected input failure and specific diagnostic observed; no output emitted |
| [C08](C08/receipt.json) | COMP-06 | PASS | Expected input failure and specific diagnostic observed; no output emitted |
| [X01](X01/receipt.json) | EXP-01 | OBSERVATION | All reads unmapped: inspect whether an empty alignment table produces a useful result or diagnostic. |
| [X02](X02/receipt.json) | EXP-01 | OBSERVATION | Zero total input reads: inspect the diagnostic; no upstream invalid-input contract asserted. |
| [X03](X03/receipt.json) | EXP-02 | OBSERVATION | Total input count below unique mapped count: inspect whether impossible percentages are rejected. |
| [X04](X04/receipt.json) | EXP-03 | OBSERVATION | A mapped reference absent from the category metadata: inspect category coverage and denominator. |

Each case contains its inputs, declared expectations, receipt, stdout/stderr and any component output.

Review status: technical review pending. These results are component verification in the recorded environment, not clinical accuracy or regulatory approval.
