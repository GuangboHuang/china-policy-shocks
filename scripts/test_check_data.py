"""Regression checks: demonstrate that the validator rejects data drift."""
import contextlib
import csv
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from check_data import check, ROOT


class ConsistencyRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('data', 'cards'):
            shutil.copytree(ROOT / name, self.root / name)
        for name in ('database.qmd', 'appendix_policy_list.md'):
            shutil.copy(ROOT / name, self.root / name)

    def rewrite(self, name, mutate):
        path = self.root / 'data' / name
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        mutate(rows)
        with path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_baseline(self):
        with contextlib.redirect_stdout(io.StringIO()):
            check(self.root)

    def test_csv_drift(self):
        self.rewrite('policy_shock_library_v0_1.csv', lambda rows: rows[0].update(rating='C'))
        with self.assertRaisesRegex(AssertionError, 'Excel/CSV'):
            check(self.root)

    def test_audit_omission(self):
        self.rewrite('official_source_audit.csv', lambda rows: rows.pop())
        with self.assertRaisesRegex(AssertionError, 'coverage'):
            check(self.root)

    def test_stale_appendix(self):
        (self.root / 'appendix_policy_list.md').write_text('stale')
        with self.assertRaisesRegex(AssertionError, 'Stale appendix'):
            check(self.root)

    def test_wrong_stata_field(self):
        p = self.root / 'database.qmd'
        p.write_text(p.read_text().replace('tab domain rating', 'tab 领域 rating'))
        with self.assertRaisesRegex(AssertionError, 'Stata example'):
            check(self.root)


if __name__ == '__main__':
    unittest.main()
