"""Offline consistency checks. Run from any working directory."""
from pathlib import Path
import csv
import re
from urllib.parse import urlsplit
from build_appendix import (COLUMN_ALIASES, read_policy_excel, normalize_dataframe,
                            sort_dataframe, build_markdown_appendix)

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    def read(name):
        with (root / 'data' / name).open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            return reader.fieldnames, list(reader)
    fields, rows = read('policy_shock_library_v0_1.csv')
    assert fields == list(COLUMN_ALIASES), 'CSV schema mismatch'
    names = [r['policy_name'] for r in rows]
    assert len(names) == len(set(names)) and all(names), 'Missing/duplicate policy name'
    for row in rows:
        assert all(row[k].strip() for k in fields if k not in ('official_source', 'notes')), row['policy_name']
        assert row['rating'] in ('A', 'B', 'C'), row['policy_name']
        assert re.fullmatch(r'\d{4}', row['year']), row['policy_name']
    expected = sort_dataframe(normalize_dataframe(read_policy_excel(root / 'data/policy_shock_library_v0_1.xlsx')))
    assert expected.to_dict('records') == rows, 'Excel/CSV mismatch: regenerate CSV'
    assert (root / 'appendix_policy_list.md').read_text() == build_markdown_appendix(expected), 'Stale appendix'
    _, audit = read('official_source_audit.csv')
    assert len(audit) == len(rows) and {r['policy_name'] for r in audit} == set(names), 'Audit coverage mismatch'
    by_name = {r['policy_name']: r for r in rows}
    for a in audit:
        assert a['status'] in ('pending', 'verified_partial')
        assert a['checked_on'] and a['evidence'] and a['next_step']
        assert a['official_source'] == by_name[a['policy_name']]['official_source'], 'Audit/source mismatch'
        if a['status'] == 'pending':
            assert not a['official_source'], 'Pending evidence must not be published as verified'
        else:
            assert a['official_source'] and a['source_title'] and a['source_record']
            card = (root / a['source_card']).read_text() if a['source_card'] else None
            for url in a['official_source'].split(';'):
                parsed = urlsplit(url)
                assert parsed.scheme == 'https' and parsed.netloc and not parsed.username
                assert card is None or url in card, 'Backfilled URL absent from source card'
    doc = (root / 'database.qmd').read_text()
    python = re.search(r'```python\n(.*?)```', doc, re.S)[1]
    import os
    original = Path.cwd()
    try:
        os.chdir(root)
        scope = {}
        exec(python, scope)
        assert 'rating' in scope['df'] and len(scope['df'].query("rating == 'A'")) > 0
    finally:
        os.chdir(original)
    stata = re.search(r'```stata\n(.*?)```', doc, re.S)[1]
    assert 'varnames(1)' in stata and 'encoding("utf-8")' in stata
    tab = re.search(r'^tab (.+)$', stata, re.M)[1].split()
    assert all(col in fields for col in tab), 'Stata example references unknown field'
    print(f'PASS: {len(rows)} records; {sum(bool(r["official_source"]) for r in rows)} sourced; '
          f'{sum(a["status"] == "pending" for a in audit)} pending. Stata checked statically only.')


if __name__ == '__main__':
    check()
