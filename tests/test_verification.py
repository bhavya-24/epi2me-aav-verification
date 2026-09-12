"""Harness tests with deliberately tiny fictional fixtures; no EPI2ME execution."""
import csv
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import verify_aav as v


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, name, content):
        path = self.root / name
        path.write_text(content, encoding='utf-8')
        return path

    def labels(self, name, values):
        path = self.root/name
        with path.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['read_id','label'])
            writer.writerows(values)
        return path

    def test_valid_fastq_and_gzip(self):
        text = '@r1 model=synthetic\nACGTN\n+\nIIIII\n'
        self.assertEqual(v.fastq_ids(self.file('reads.fq', text)), {'r1'})
        path = self.root/'reads.fq.gz'
        with gzip.open(path, 'wt') as stream:
            stream.write(text)
        self.assertEqual(v.fastq_ids(path), {'r1'})

    def test_truncated_fastq_rejected(self):
        for text in ['@r1\nACGT\n+\nIII\n', '@r1\nACGT\n', '', '@\nA\n+\nI\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                v.fastq_ids(self.file('reads.fq', text))

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            v.fastq_ids(self.file('reads.fq', '@r1\nA\n+\nI\n' * 2))

    def test_bad_bases_quality_and_plus_rejected(self):
        for text in ['@r1\nAZ\n+\nII\n', '@r1\nAA\n+\nI \n', '@r1\nAA\n+r2\nII\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                v.fastq_ids(self.file('reads.fq', text))

    def test_multiline_fasta(self):
        records = v.fasta_records(self.file('ref.fa', '>one description\nAC\nGT\n>two\nNNN\n'))
        self.assertEqual(records, {'one':'ACGT', 'two':'NNN'})

    def test_bad_fasta(self):
        for text in ['>one\n', 'ACGT\n', '>one\nA\n>one\nG\n', '>\nA\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                v.fasta_records(self.file('ref.fa', text))

    def test_structure_table_is_subset_not_all_input(self):
        path = self.file('structures.tsv', 'Read\tAssigned_genome_type\nr1\tFull ssAAV\n')
        self.assertIn('1 unique', v.tsv_read_ids(path, {'r1','r2'}))

    def test_foreign_read_in_structure_table_rejected(self):
        path = self.file('structures.tsv', 'Read\tAssigned_genome_type\nwrong\tFull ssAAV\n')
        with self.assertRaisesRegex(ValueError, 'absent'):
            v.tsv_read_ids(path, {'r1'})

    def test_missing_structure_header_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Read'):
            v.tsv_read_ids(self.file('structures.tsv', 'other\na\n'), {'a'})

    def test_metrics_against_hand_calculated_confusion_matrix(self):
        truth = self.labels('truth.csv', [('a','positive'),('b','positive'),('c','negative'),('d','negative')])
        pred = self.labels('pred.csv', [('a','positive'),('b','negative'),('c','positive'),('d','negative')])
        result = v.metrics(truth,pred)
        for name in ['tp','tn','fp','fn']:
            self.assertEqual(result['counts'][name],1)
        for name in ['sensitivity_on_classified','specificity_on_classified','precision_on_classified']:
            self.assertEqual(result[name],0.5)

    def test_abstentions_are_reported_with_coverage(self):
        truth = self.labels('truth.csv', [('a','positive'),('b','positive'),('c','negative')])
        pred = self.labels('pred.csv', [('a','positive'),('b','unclassified'),('c','negative')])
        result = v.metrics(truth,pred)
        self.assertEqual(result['sensitivity_on_classified'],1)
        self.assertEqual(result['positive_detection_rate_all'],0.5)
        self.assertAlmostEqual(result['classification_coverage'],2/3)

    def test_undefined_metric_is_null(self):
        truth = self.labels('truth.csv', [('a','negative')])
        pred = self.labels('pred.csv', [('a','unclassified')])
        self.assertIsNone(v.metrics(truth,pred)['sensitivity_on_classified'])
        self.assertIsNone(v.metrics(truth,pred)['specificity_on_classified'])

    def test_missing_prediction_rejected(self):
        truth = self.labels('truth.csv', [('a','positive'),('b','negative')])
        pred = self.labels('pred.csv', [('a','positive')])
        with self.assertRaisesRegex(ValueError, 'match truth'):
            v.metrics(truth,pred)

    def test_duplicate_labels_rejected(self):
        truth = self.labels('truth.csv', [('a','positive'),('a','negative')])
        pred = self.labels('pred.csv', [('a','positive')])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            v.metrics(truth,pred)

    def test_missing_tool_is_blocked_not_passed(self):
        checks, evidence = [], []
        with patch('verify_aav.shutil.which',return_value=None):
            v.external_check(checks,'BAM-01','REQ-07',['samtools','quickcheck','missing.bam'],evidence)
        self.assertEqual(checks[0].status, 'BLOCKED')
        self.assertEqual(evidence, [])

    def test_nonzero_tool_exit_retained(self):
        import subprocess
        checks, evidence = [], []
        result = subprocess.CompletedProcess(['samtools'], 1, '', 'corrupt BAM')
        with patch('verify_aav.shutil.which',return_value='/usr/bin/samtools'), patch('verify_aav.subprocess.run',return_value=result):
            v.external_check(checks,'BAM-01','REQ-07',['samtools','quickcheck','bad.bam'],evidence)
        self.assertEqual(checks[0].status, 'FAIL')
        self.assertEqual(evidence[0]['stderr'], 'corrupt BAM')

    def test_manifest_missing_or_corrupt_is_a_failed_check(self):
        self.assertEqual(v.preflight(self.root)[0].status,'FAIL')
        self.file('manifest.json','{}')
        self.assertEqual(v.preflight(self.root)[0].status,'FAIL')

    def test_report_does_not_turn_skipped_into_success(self):
        checks = [v.Check('one','R1','PASS','ok'),v.Check('two','R2','NOT_RUN','Needs evidence')]
        directory = self.root/'report'
        self.assertEqual(v.write_report(checks,directory,'FICTIONAL TEST'),2)
        result = json.loads((directory/'report.json').read_text())
        self.assertFalse(result['all_checks_passed'])
        self.assertEqual(ET.parse(directory/'junit.xml').getroot().get('skipped'),'1')
        with self.assertRaises(FileExistsError):
            v.write_report(checks,directory,'FICTIONAL TEST')

    def test_archive_checksum_must_match(self):
        archive = self.file('wrong.tar.gz','not an archive')
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            v.prepare(archive,self.root/'destination')
        self.assertFalse((self.root/'destination').exists())

    def test_quarantine_preserves_original_and_tracks_derivation(self):
        source = self.root/'original'
        source.mkdir()
        malformed = '@transgene_cassette_3\n' + 'A'*412 + 'q\n+\n' + 'I'*413 + '\n'
        valid = '@valid\nACGT\n+\nIIII\n'
        for name in v.MEMBERS:
            path = source/name
            path.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith('.fq'):
                path.write_text((malformed if 'sample_1' in name else '') + valid)
            else:
                path.write_bytes(b'reference-fixture-not-used-by-this-test')
        manifest = {'source_archive_sha256':v.DEMO_SHA,'files':{name:v.sha256(source/name) for name in v.MEMBERS}}
        (source/'manifest.json').write_text(json.dumps(manifest))
        before = v.sha256(source/'fastq/sample_1/simulated_reads.fq')
        destination = self.root/'baseline'
        result = v.derive_baseline(source,destination)
        self.assertEqual(v.sha256(source/'fastq/sample_1/simulated_reads.fq'),before)
        self.assertEqual(result['derivation']['remaining_reads'],{'sample_1':1,'sample_2':1})
        self.assertEqual((destination/'quarantined-record.fastq').read_text(),malformed)
        self.assertEqual(v.fastq_ids(destination/'fastq/sample_1/simulated_reads.fq'),{'valid'})


if __name__ == '__main__':
    unittest.main()
