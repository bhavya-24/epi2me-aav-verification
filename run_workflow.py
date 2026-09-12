"""Execute the pinned workflow in an Eddie allocation and retain run evidence."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from verify_aav import REVISION, preflight, sha256, verify_outputs, write_report


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=['baseline', 'missing-input', 'unknown-parameter'], default='baseline')
    args = parser.parse_args()
    if not os.environ.get('JOB_ID') or int(os.environ.get('NSLOTS', '0')) != 16:
        parser.error('Run via hpc/eddie.qsub in a 16-slot allocation; do not run analysis on a login node')
    root = Path(__file__).resolve().parent
    if Path.cwd() != root:
        parser.error('Run from the project root')
    if any(c.isspace() for c in str(root)):
        parser.error('Use an HPC project path without spaces for Nextflow/container staging')
    source, demo = root/'cache/wf-aav-qc', root/'data/baseline'
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain'], text=True).strip()
    if revision != REVISION or dirty:
        parser.error('Cached source must be clean and match the pinned revision')
    hashes = json.loads((root/'cache/container-hashes.json').read_text())
    for name in ('aav', 'common', 'medaka'):
        if sha256(root/'cache/containers'/f'{name}.sif') != hashes[name]:
            parser.error(f'Container changed since preparation: {name}')
    run = root/'runs'/f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{os.environ['JOB_ID']}-{args.case}"
    run.mkdir(parents=True, exist_ok=False)
    if write_report(preflight(demo), run/'preflight', 'INPUT CHECKS ONLY - no EPI2ME execution'):
        parser.exit(1, f'Input checks failed; see {run}/preflight\n')
    output = run/'output'
    command = [
        'nextflow', '-log', str(run/'nextflow.log'), 'run', str(source),
        '-profile', 'singularity', '-c', str(root/'hpc/eddie.config'),
        '-work-dir', str(run/'work'), '-ansi-log', 'false',
        '--fastq', str(demo/'fastq'), '--itr1_start', '11', '--itr1_end', '156',
        '--itr2_start', '2156', '--itr2_end', '2286',
        '--ref_helper', str(demo/'helper.fasta'), '--ref_host', str(demo/'cell_line.fasta.gz'),
        '--ref_rep_cap', str(demo/'repcap.fasta'), '--ref_transgene_plasmid', str(demo/'transgene.fasta'),
        '--threads', '8', '--out_dir', str(output), '--disable_ping',
    ]
    if args.case == 'missing-input':
        command[command.index('--fastq')+1] = str(run/'deliberately-absent.fastq')
    elif args.case == 'unknown-parameter':
        command += ['--verification_deliberately_unknown_parameter', 'true']
    versions = {}
    for name, arguments in [('nextflow',['nextflow','-version']), ('singularity',['singularity','--version']),
                            ('python',[sys.executable,'--version'])]:
        result = subprocess.run(arguments, capture_output=True, text=True)
        if result.returncode:
            parser.error(f'Unable to determine {name} version: {result.stderr}')
        versions[name] = result.stdout + result.stderr
    receipt = {'case': args.case, 'revision': revision, 'started_at': utcnow(), 'finished_at': None,
               'exit_code': None, 'job_id': os.environ['JOB_ID'], 'argv': command, 'versions': versions,
               'containers_sha256': hashes, 'demo_manifest_sha256': sha256(demo/'manifest.json'),
               'output': str(output), 'hpc_config_sha256': sha256(root/'hpc/eddie.config')}
    receipt_file = run/'run.json'
    receipt_file.write_text(json.dumps(receipt,indent=2)+'\n')
    with (run/'console.log').open('w') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    receipt.update(exit_code=result.returncode, finished_at=utcnow())
    receipt_file.write_text(json.dumps(receipt,indent=2)+'\n')
    if args.case != 'baseline':
        (run/'REVIEW_REQUIRED.md').write_text(
            '# Controlled negative test: review required\n\n'
            f'Case: {args.case}. Observed exit code: {result.returncode}.\n\n'
            'A nonzero exit alone is not a pass. Confirm the intended input/parameter error caused the failure, '
            'rather than a missing container, scheduler termination, or unrelated exception. '
            'Record the diagnostic and your decision in docs/manual-review.md.\n')
        print(f'Negative case recorded; manual diagnostic review required: {run}')
        return 2 if result.returncode else 1
    if result.returncode:
        print(f'Workflow failed; preserved actual exit code {result.returncode}: {run}', file=sys.stderr)
        return 1
    checks, evidence = verify_outputs(demo, output, run)
    status = write_report(checks, run/'verification', 'HPC OUTPUT CHECKS - manual review and benchmarking separate', evidence)
    print(f'Evidence: {run}/verification/report.md; 2 means incomplete review, not complete success')
    return status


if __name__ == '__main__':
    raise SystemExit(main())
