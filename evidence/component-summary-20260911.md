# Local component work completed 2026-09-11

| Activity | Actual outcome | Evidence |
|---|---|---|
| Pinned EPI2ME contamination CLI | Eight contract checks passed | component-20260911-01/run.json and junit.xml |
| Exploratory component probes | Four observed behaviours, not pass/fail contracts | component-20260911-01/X01 through X04 |
| Local FASTQ validator challenge set | TP=12, TN=8, FP=0, FN=0; no abstentions | validator-20260911-01/report.json |
| Verification harness unit tests | 28 passed | component-harness-tests-20260911.txt |
| Workspace-required regression suite | 50 passed; unrelated to scientific correctness | Terminal execution recorded by Codex |
| samtools/bcftools local exercise | BLOCKED: executables unavailable | file-tools-local-20260911-01/report.json |
| Full Nextflow/Eddie workflow | NOT_RUN; previous container preparation failed | eddie-environment.md |
| Applicant/peer review and external CI | NOT_RUN | No review or external execution claimed |

Real native SeqKit 2.13.0 was used; its archive was checked against the SHA256
digest from GitHub release-asset metadata. The component source subset was
retrieved from the pinned Oxford Nanopore commit, retained unchanged and hashed.
Python dependencies describe the experiment's local environment, not a claim
of identical dependencies to the upstream image.

The case study PDF was rendered and both pages visually checked. Code and
documents were prepared with Codex assistance; the applicant still needs to
reproduce selected cases, inspect the evidence and explain the results.

An isolated Linux Micromamba installer for samtools 1.22 and bcftools 1.22 is
prepared because the user reported no matching Eddie modules. The installer
has not been executed on Eddie and is not reported as a completed tool check.
