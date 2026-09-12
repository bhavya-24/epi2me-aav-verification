#!/bin/bash
# Run on an Eddie node approved for downloads/container preparation.
# Does not submit jobs or launch the EPI2ME analysis.
set -euo pipefail
[[ -f workflow.lock.json ]] || { echo 'Run from the project root.' >&2; exit 1; }
source hpc/site-setup.sh
mkdir -p data cache/containers
revision=$(python3 -c 'import json; print(json.load(open("workflow.lock.json"))["revision"])')
repository=$(python3 -c 'import json; print(json.load(open("workflow.lock.json"))["repository"])')
if [[ ! -d cache/wf-aav-qc/.git ]]; then
    git clone --no-checkout "$repository" cache/wf-aav-qc
fi
git -C cache/wf-aav-qc fetch origin "$revision"
git -C cache/wf-aav-qc checkout --detach "$revision"
for name in aav common medaka; do
    uri=$(python3 -c 'import json,sys; print(json.load(open("workflow.lock.json"))["containers"][sys.argv[1]])' "$name")
    if [[ ! -f "cache/containers/$name.sif" ]]; then
        singularity pull "cache/containers/$name.sif" "$uri"
    fi
done
python3 - <<'PY'
import json, pathlib, urllib.request
from verify_aav import prepare, derive_baseline, sha256
lock=json.load(open('workflow.lock.json'))
archive=pathlib.Path('data/wf-aav-qc-demo.tar.gz')
if not archive.exists():
    partial=archive.with_suffix('.download')
    urllib.request.urlretrieve(lock['demo_url'], partial)
    if sha256(partial) != lock['demo_sha256']:
        raise SystemExit('Unexpected demo checksum; retain download for investigation')
    partial.rename(archive)
if sha256(archive) != lock['demo_sha256']:
    raise SystemExit('Existing demo archive checksum differs')
if not pathlib.Path('data/demo').exists():
    prepare(archive, 'data/demo')
if not pathlib.Path('data/baseline').exists():
    derive_baseline('data/demo', 'data/baseline')
containers={name:sha256(pathlib.Path('cache/containers')/(name+'.sif')) for name in lock['containers']}
pathlib.Path('cache/container-hashes.json').write_text(json.dumps(containers,indent=2)+'\n')
PY
chmod u+x scripts/samtools scripts/bcftools
nextflow -version
singularity --version
python3 --version
printf '%s\n' 'Preparation finished. Review versions, then submit: qsub hpc/eddie.qsub'
