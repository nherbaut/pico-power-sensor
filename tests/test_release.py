"""A missing, stale or incomplete record must not pass a release gate."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/check-release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def records(self, gates=('fabrication',)):
        return [dict(board='interposer', gate=g, check_id=k, status='passed',
                     design_sha256='current', evidence='AGENTS.md', reviewer='test reviewer',
                     reviewed_on='2026-10-14', remaining='', requirement=k)
                for g in gates for k in release.REQUIRED['interposer'][g]]

    def test_complete_record(self):
        self.assertEqual(release.blockers(self.records(), 'interposer', 'fabrication', 'current'), [])

    def test_deleted_row_does_not_bypass_gate(self):
        rows = self.records()
        rows.pop()
        self.assertTrue(release.blockers(rows, 'interposer', 'fabrication', 'current'))

    def test_stale_evidence_does_not_pass(self):
        self.assertTrue(release.blockers(self.records(), 'interposer', 'fabrication', 'changed'))

    def test_pending_record_does_not_pass(self):
        rows = self.records()
        rows[0]['status'] = 'pending'
        self.assertTrue(release.blockers(rows, 'interposer', 'fabrication', 'current'))

    def test_missing_evidence_does_not_pass(self):
        rows = self.records()
        rows[0]['evidence'] = 'missing-test-evidence.txt'
        self.assertTrue(release.blockers(rows, 'interposer', 'fabrication', 'current'))

    def test_connection_requires_fabrication_and_bench_evidence(self):
        self.assertTrue(release.blockers(self.records(('connection',)), 'interposer', 'connection', 'current'))

    def test_duplicate_row_does_not_pass(self):
        rows = self.records()
        rows.append(rows[0])
        self.assertTrue(release.blockers(rows, 'interposer', 'fabrication', 'current'))

    def test_unresolved_work_does_not_pass(self):
        rows = self.records()
        rows[0]['remaining'] = 'Still need to check the pin numbering'
        self.assertTrue(release.blockers(rows, 'interposer', 'fabrication', 'current'))
