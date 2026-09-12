# OBS-001: invalid nucleotide in the public demo FASTQ

Observed locally on 2026-09-09. Classification: **confirmed input-data anomaly**.
This is not evidence of a defect in the workflow implementation. The reason
the upstream archive contains this record has not been established.

## Evidence

- Archive SHA256: `7a62b511c2cfaece8a64312858ae60200354c3d55f9329a21031d279d81c1d53`
- Selected file: `fastq/sample_1/simulated_reads.fq`
- File SHA256: `6e1cc0fbe4851ddf3d90211363e57c4eaff217a307c79846a9e57ca4d24c331f`
- Read identifier: `transgene_cassette_3`
- Sequence length: 2,327; quality length: 2,327.
- Invalid character: lowercase `q`, at one-based sequence position **413**.
- One affected record among 10,440 sample_1 records. The second sample's
  10,440 reads passed the same FASTQ check.
- Original detection: `evidence/demo-preflight/report.json`, check
  `IN-02:sample_1`, status FAIL. The failed evidence remains unchanged.

Expected behaviour of this project's preflight: reject a sequence containing
a non-nucleotide character before starting an expensive analysis. It did so.
The effect on wf-aav-qc itself has not been tested.

## Reproduction

```bash
python verify_aav.py preflight --demo data/demo --report evidence/reproduced-original
```

The command exits 1. Its evidence identifies the malformed record. To inspect
the original manually, read its four-line FASTQ record and count to position
413 in the sequence line; do not count the header or quality line.

## Baseline decision

Preserve the original demo and quarantined record. Produce `data/baseline` by
excluding exactly the observed record, with no guessed replacement nucleotide.
The derivation fails if the record does not match the observed anomaly.
Remaining counts are 10,439 in sample_1 and 10,440 in sample_2. The new manifest
links original hashes, the excluded read and the derived input hashes.

```bash
python verify_aav.py derive-baseline --source data/demo --destination data/baseline
python verify_aav.py preflight --demo data/baseline --report evidence/baseline-preflight
```

This changes the dataset and must be disclosed in comparisons and reports.
It is an analysis-preparation decision, not a repair of Oxford Nanopore's
software. Do not submit an upstream defect allegation without investigating
whether this malformed record was intentionally included as a test fixture.

## Review considerations

Explain the independent input check, the observation, why the original was
preserved, why no replacement base was guessed, how the derivation is tracked,
and what remains unknown about downstream behaviour.
