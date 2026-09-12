# Eddie environment observation, 2026-09-10

Source: terminal output supplied by the user. No remote session was opened by
Codex and no workflow was submitted.

| Observation | Reported value |
|---|---|
| Available Nextflow module | igmm/apps/nextflow/24.04.4 |
| Available Singularity modules | singularity/4.1.3, singularity/4.1.3_old, singularity/4.3.4 |
| Available Python module | python/3.12.9 |
| Python before loading project modules | Python 3.11.7 |
| Scheduler command | qsub present in Grid Engine 2024.1.0 |

Default setup now selects Nextflow 24.04.4, Singularity 4.3.4 and Python 3.12.9.

## Successful module check supplied by the user

The follow-up terminal output on 2026-09-10 confirms:

- Nextflow 24.04.4 build 5917 started successfully after dependency downloads.
- Singularity-CE 4.3.4 reported its version.
- Python 3.12.9 reported its version.
- The user's Eddie scratch directory exists and is owned by the user, with
  owner read/write/execute permissions. Free space and quota were not measured.

Subsequent user output confirms project transfer and 20 harness tests passing
on Eddie. df reported 157T free on the shared filesystem; personal quota was
not measured. Singularity container preparation failed during SquashFS creation
with `Out of memory (cache_alloc)`, exit 255. No successful workflow run follows
from these observations. On 2026-09-11 the user reported that module searches
showed neither samtools nor bcftools. A project-local Micromamba installer has
been prepared as an alternative, but has not been run in the user's account.

Successful container preparation and batch analysis remain pending.
These are observations from the user's session, not a remote session opened
by Codex or evidence that the EPI2ME workflow has run.
