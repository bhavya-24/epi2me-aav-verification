# Manual review record

Status: NOT_RUN. Complete using actual run evidence; do not invent results.

- Reviewer:
- Date:
- Run directory / job ID:
- Workflow revision:
- Input manifest SHA256:

## Biological interpretation

1. What do the transgene, host, helper and rep-cap references represent?
2. How many reads entered each sample, and which output counts include only
   aligned or transgene-assigned subsets? Cite filenames and fields.
3. What is the reported contamination composition? Explain its denominator.
4. Inspect at least one transgene and one non-transgene alignment in IGV or
   samtools view. Record reference, coordinates, flags and classification.
5. Explain one coverage feature or reported variant; distinguish observation
   from interpretation. Do not make clinical conclusions from this demo.
6. State what cannot be concluded from these simulated samples.

## Controlled failure cases

For each negative run record: intended failure, command, actual exit code,
diagnostic excerpt, whether the diagnostic matches the intended condition,
and PASS / FAIL / BLOCKED with a reason. Avoid marking a network or module error
as successful detection of a malformed input.

## Deviation / defect template

- Identifier and severity rationale:
- Expected behaviour and source requirement:
- Reproduction steps and exact inputs:
- Actual behaviour and logs:
- Impact / scope:
- Root cause (or explicitly unknown):
- Proposed change, if any:
- Regression test and observed result:
- Review status:

## Reproduction walkthrough

Identify the workflow question, follow one requirement-to-test link, reproduce
the check, and explain the observation and its limits. Distinguish behaviour
of the verification harness from behaviour of the upstream component.
