#!/usr/bin/env python3
"""Validate public package integrity; optionally compare against the frozen v2."""
import argparse
import csv
import json
import re
import sqlite3
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from build_public import ROOT, SOURCE_SHA256, RECORD_FIELDS, OBS_FIELDS, REQUIRED_FIELDS, TABLES, counts, readonly, sha, public_review_status

FORBIDDEN = re.compile(r'/Users/|/home/|/private/|file://|P_LOCAL_G0|G0_LOCAL|G0_original|G0反应|G0_reaction|G0_ligand|not_exact_G0|oleObject|tmp/database|tmp/final|本课题|ROOT policy')

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--source',type=Path)
    p.add_argument('--skip-checksums',action='store_true',help='Only for maintainers before sealing SHA256SUMS')
    args=p.parse_args();root=args.root.resolve()
    manifest=json.loads((root/'manifest.json').read_text())
    db=root/manifest['database']['path']
    if not db.exists():
        raise SystemExit('Data asset missing. Download NiAsymCoupling-v2.0.0.zip from the v2.0.0 GitHub Release and extract its contents into the repository root before verification.')
    c=readonly(db)
    check(c.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity')
    check(not c.execute('PRAGMA foreign_key_check').fetchall(),'Foreign keys')
    check(sha(db)==manifest['database']['sha256'],'Database SHA-256')
    check(counts(c)==manifest['counts'],'Counts differ from manifest')
    check(c.execute("SELECT count(*) FROM records WHERE ee_magnitude_percent<0 OR ee_magnitude_percent>100 OR (result_class IN ('no_reaction','racemic_qualitative') AND ee_magnitude_percent IS NOT NULL)").fetchone()[0]==0,'Invalid numeric outcome')
    check(c.execute("SELECT count(*) FROM records WHERE in_main_scope IS NOT (scope_status='in_main_scope' AND catalyst_scope='nickel_reported' AND bond_type='C(sp2)-C(sp3)' AND is_preferred=1)").fetchone()[0]==0,'Main scope flag predicate')
    check(c.execute("SELECT count(*) FROM papers WHERE source_kind='local_experiment'").fetchone()[0]==0,'Local papers leaked')
    check(c.execute("SELECT count(*) FROM input_structure_evidence WHERE record_id='ACS2024-RAW-04299' AND partner_role='sp2' AND (stereo_status_public_summarized<>1 OR length(stereo_status)>250)").fetchone()[0]==0,'Mixed-stock source quotation was not summarized')
    check(set(TABLES)=={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")},'Unexpected table')
    for table in TABLES:
        columns=[r[1] for r in c.execute(f'PRAGMA table_info({table})')]
        check(columns==TABLES[table][0],f'Unexpected fields: {table}')
        for row in c.execute(f'SELECT * FROM {table}'):
            for value in row:
                check(not isinstance(value,str) or not FORBIDDEN.search(value),f'Private path/local-data marker in {table}')
        path=root/'data'/f'{table}.csv'
        if path.exists():
            with path.open(encoding='utf-8',newline='') as stream:
                reader=csv.reader(stream);check(next(reader)==columns,f'CSV header: {table}')
                actual=list(reader)
            expected=[[str(v) if v is not None else '' for v in r] for r in c.execute(f'SELECT * FROM {table} ORDER BY {columns[0]}')]
            check(actual==expected,f'CSV values: {table}')
    n_hashes=0
    if not args.skip_checksums:
        for line in (root/'SHA256SUMS').read_text().splitlines():
            expected,relative=line.split('  ',1);target=root/relative
            check(target.is_relative_to(root),f'Unsafe checksum path: {relative}')
            check(sha(target)==expected,f'Checksum: {relative}');n_hashes+=1
    compared=0
    if args.source:
        check(sha(args.source)==SOURCE_SHA256,'Frozen source SHA-256')
        src=readonly(args.source)
        excluded={r[0] for r in src.execute("SELECT paper_id FROM papers WHERE source_kind='local_experiment'")}|{'P_LOCAL_G0'}
        source_records={r['record_id']:r for r in src.execute('SELECT * FROM v_scope_assessment') if not any(r[k] in excluded for k in ['paper_id','original_paper_id','method_paper_id'])}
        check(set(source_records)=={r[0] for r in c.execute('SELECT record_id FROM records')},'Exact public record population')
        for row in c.execute('SELECT * FROM records'):
            expected=source_records[row['record_id']]
            check(all(row[f]==(public_review_status(expected[f]) if f=='review_status' else expected[f]) for f in RECORD_FIELDS),f'Record value mismatch: {row["record_id"]}')
            compared+=1
        for public_table,source_table,fields,key in [
          ('required_substrate_status','v_verified_required_substrate_status',REQUIRED_FIELDS,'record_id'),
          ('source_observations','source_observations',OBS_FIELDS,'observation_id')]:
            expected={r[key]:r for r in src.execute(f'SELECT * FROM {source_table}') if r['record_id'] in source_records}
            actual=list(c.execute(f'SELECT * FROM {public_table}'))
            check(set(expected)=={r[key] for r in actual},f'Population: {public_table}')
            for row in actual:
                check(all(row[f]==expected[row[key]][f] for f in fields),f'Value mismatch: {public_table}/{row[key]}')
        src.close();check(sha(args.source)==SOURCE_SHA256,'Frozen source modified')
    result={'status':'PASS','sqlite_integrity':'ok','foreign_keys':'ok','manifest_counts':'exact',
      'csv_exports':'exact','private_path_and_local_data_marker_scan':'clear',
      'checksummed_files_verified':n_hashes,'source_result_rows_compared':compared,
      'primary_source_reaudit_performed':False,'third_party_redistribution_rights_verified':False}
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
