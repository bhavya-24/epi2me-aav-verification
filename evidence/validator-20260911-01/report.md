# FASTQ validator challenge-set benchmark

Four-line Phred+33 FASTQ dialect accepted by this project; A/C/G/T/N bases only. Unit = one file, positive = malformed. Authored challenge cases, not a held-out population sample.

TP=12; FN=0; TN=8; FP=0.
Sensitivity=1.0; specificity=1.0; coverage=1.0.

Small authored challenge set, related to existing unit tests. Not independent external validation, EPI2ME workflow accuracy or clinical performance.

| Case | Truth | Prediction | Reason / actual diagnostic |
|---|---|---|---|
| V01 | negative | negative | Ordinary record: Accepted 1 records |
| V02 | negative | negative | Lowercase bases and N: Accepted 1 records |
| V03 | negative | negative | Lowest allowed Phred+33 character: Accepted 1 records |
| V04 | negative | negative | Highest allowed Phred+33 character: Accepted 1 records |
| V05 | negative | negative | Repeated matching identifier and description: Accepted 1 records |
| V06 | negative | negative | Two distinct reads: Accepted 2 records |
| V07 | negative | negative | CRLF line endings: Accepted 1 records |
| V08 | negative | negative | Gzip-compressed record: Accepted 1 records |
| I01 | positive | positive | Header lacks @: FASTQ header must start with @ and contain a read ID |
| I02 | positive | positive | Empty identifier: FASTQ header must start with @ and contain a read ID |
| I03 | positive | positive | Invalid q in sequence: Empty/unsupported sequence for a |
| I04 | positive | positive | Missing plus marker: Truncated FASTQ or sequence/quality mismatch for a |
| I05 | positive | positive | Quality shorter than sequence: Truncated FASTQ or sequence/quality mismatch for a |
| I06 | positive | positive | Quality longer than sequence: Truncated FASTQ or sequence/quality mismatch for a |
| I07 | positive | positive | Truncated final record: Truncated FASTQ or sequence/quality mismatch for a |
| I08 | positive | positive | Duplicate read identifier: Duplicate read ID: a |
| I09 | positive | positive | Mismatched repeated identifier: Repeated identifier differs for a |
| I10 | positive | positive | Quality contains ASCII 32: Invalid Phred+33 character for a |
| I11 | positive | positive | Quality contains ASCII 127: Invalid Phred+33 character for a |
| I12 | positive | positive | Empty file: No FASTQ reads |
