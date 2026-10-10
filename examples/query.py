#!/usr/bin/env python3
"""Read the public derivative using only Python's standard library."""
import sqlite3
from pathlib import Path

db=Path(__file__).resolve().parents[1]/'data'/'NiAsymCoupling_v2_public.sqlite'
if not db.exists():
    raise SystemExit('Download the NiAsymCoupling-v2.0.0.zip Release data asset and extract its contents into the repository root first.')
connection=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
for row in connection.execute('''
 SELECT record_id, original_doi, ee_magnitude_percent, ligand_smiles,
        has_open_duplicate_candidate
 FROM main_scope_numeric_ee ORDER BY record_id LIMIT 5
'''):
    print(row)
connection.close()
