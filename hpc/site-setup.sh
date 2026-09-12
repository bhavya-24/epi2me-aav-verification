#!/bin/bash
# Module versions confirmed by the user's Eddie output on 2026-09-10.
# Use site-setup.local.sh if the account's working environment changes.
set +u
if [[ -f /etc/profile.d/modules.sh ]]; then
    source /etc/profile.d/modules.sh
fi
if [[ -f hpc/site-setup.local.sh ]]; then
    source hpc/site-setup.local.sh
else
    module load igmm/apps/nextflow/24.04.4
    module load singularity/4.3.4
    module load python/3.12.9
fi
set -u
for tool in nextflow singularity python3 git; do
    command -v "$tool" >/dev/null || { echo "Missing: $tool. Configure hpc/site-setup.local.sh." >&2; exit 1; }
done
python3 -c 'import sys; assert sys.version_info >= (3,10), "Load Python 3.10 or later"'
export AAV_PROJECT_ROOT="$PWD"
export NXF_HOME="$PWD/cache/nextflow-home"
export NXF_SINGULARITY_CACHEDIR="$PWD/cache/nextflow-images"
export SINGULARITY_CACHEDIR="$PWD/cache/singularity"
export SINGULARITY_TMPDIR="${TMPDIR:-$PWD/cache/tmp}"
export NXF_OPTS='-Xms512m -Xmx4g'
export NXF_SYNTAX_PARSER=v1
export PATH="$PWD/scripts:$PATH"
mkdir -p "$NXF_HOME" "$NXF_SINGULARITY_CACHEDIR" "$SINGULARITY_CACHEDIR" "$SINGULARITY_TMPDIR"
