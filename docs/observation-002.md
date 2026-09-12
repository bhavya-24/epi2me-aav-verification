# OBS-002: inconsistent read totals produce impossible summary values

Observed on 2026-09-11 in the unmodified pinned EPI2ME contamination component.
Classification: **confirmed component behaviour under inconsistent metadata**.
Full-workflow reachability and user impact are not established. No issue has
been submitted upstream, and no upstream source has been changed.

## Reproduction and evidence

Run `python run_component.py --case X03 --report evidence/my-x03-reproduction`
after following LOCAL_START.md. The command creates 95 distinct mapped IDs but
supplies n_reads=94. This is a deliberately inconsistent input, not an observed
production sample. Original evidence:

- `evidence/component-20260911-01/X03/inputs/alignments.tsv`
- `evidence/component-20260911-01/X03/expectation.json`
- `evidence/component-20260911-01/X03/receipt.json`
- `evidence/component-20260911-01/X03/output.tsv`

Actual component exit: 0. Mapped=95 (101.06382978723404%); unmapped=-1
(-1.0638297872340425%). A successful exit alone therefore does not imply a
semantically valid summary when the supplied count is inconsistent.

## Explanation

The source calculates n_mapped_reads from distinct Read values, then subtracts
it from the externally supplied n_reads. It performs no local comparison that
would reject n_reads < n_mapped_reads. The negative subtraction feeds directly
into the percentage calculation. This explains the observation in this test
environment; it does not prove that upstream processes can supply such inputs.

## Proposed control and follow-up

Proposed component precondition: n_reads must be positive and no smaller than
the number of distinct mapped IDs. Reject inconsistent inputs with an explicit
diagnostic before writing the summary. Independently check output counts are
nonnegative and read percentages lie between 0 and 100.

These controls are proposed, not implemented or verified by this version.
Before changing upstream behaviour, inspect its ingress/count metadata and
empty-sample handling, agree the valid input domain, then add a regression test
for this specific condition. Do not silently clamp an impossible value to zero.

Separate observations X01/X02 raise ZeroDivisionError for an empty alignment
table/zero total reads. X04 includes an unlisted reference in the denominator
without emitting a corresponding named category. Those require separate
contract and reachability review; they are not automatically critical bugs.

## Technical review

Explain the input inconsistency, reproduce the exact values, trace the
calculation, distinguish exit-code success from output correctness, and state
what evidence is still needed before classifying this as a workflow defect.
Independent technical review is pending.
