# Local verification performed 2026-09-09

| Check | Actual result | Scope |
|---|---|---|
| Python harness tests | 20 passed | Small fictional fixtures; see harness-tests.txt |
| Bash syntax | Five scripts passed individually | Git for Windows bash -n; see bash-syntax.txt |
| Original public demo preflight | Seven checks passed; one failed | Invalid q in sample_1; see demo-preflight/report.md |
| Derived baseline preflight | Eight checks passed | One documented read quarantined; see baseline-preflight/report.md |
| Existing workspace regression suite | 50 tests passed | Required workspace checks; unrelated to EPI2ME performance |
| Python entry-point syntax | Parsed successfully | verify_aav.py and run_workflow.py |
| EPI2ME execution on Eddie | NOT_RUN | Requires upload, actual account modules and batch execution |
| samtools / bcftools output checks | NOT_RUN | Require actual workflow outputs |
| Negative workflow cases | NOT_RUN | Require execution and diagnostic review |
| Biological interpretation | NOT_RUN | Applicant must inspect the results |
| Clinical or accuracy validation | NOT_RUN | No independent workflow benchmark completed |

Python runtime used for local checks: 3.12.14. Baseline read counts are 10,439
and 10,440. The original files remain unchanged. Both input manifests and the
failed original report are retained as evidence.

These results demonstrate the harness and input investigation only. They do
not establish that the HPC configuration, containers or complete EPI2ME
workflow have run successfully. The scripts are prepared for Eddie's documented
SGE conventions but need validation in the user's account.
