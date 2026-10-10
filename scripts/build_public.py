#!/usr/bin/env python3
"""Build the literature-only public derivative from the exact frozen v2 (stdlib)."""
import argparse
import csv
import hashlib
import json
import re
import sqlite3
from pathlib import Path

SOURCE_SHA256 = 'ada489cddda9bb948f044e0a558df82de5a4eb2340b1910c07a04606fab07c9d'
SOURCE_RELATIVE_PATH = 'deliverables/NiAsymCoupling_v2_2026-10-07/NiAsymCoupling_v2.sqlite'
RELEASE = 'v2.0.0'
SOURCE_CANDIDATE_SHA256 = '046b69e1e7592b5810390de17c644e9cad66dfde463c66170ce62e7937d13eb8'
REPOSITORY = 'https://github.com/EthanTang2005/NiAsymCoupling'
ROOT = Path(__file__).resolve().parents[1]

# Explicit allowlists. Original free-text notes, raw JSON and local paths never enter
# the public schema. Original computed views are read before their backing JSON is omitted.
RECORD_FIELDS = '''record_id paper_id original_paper_id method_paper_id reaction_family
catalyst_scope catalyst_metal bond_type experiment_type measurement_kind reaction_key
sp2_partner_class sp3_partner_type ligand_id ligand_source_label sp2_molecule_id
sp3_molecule_id product_molecule_id ni_precursor ni_loading_mol_percent
ligand_loading_mol_percent solvent solvent_ratio temperature_text temperature_C
temperature_K reaction_time_h result_class ee_raw ee_magnitude_percent
ee_signed_source_percent ee_direction_convention er_raw er_major er_minor
ddg_reported_kcal_mol ddg_reported_convention ddg_abs_derived_kcal_mol target_status
yield_percent yield_raw yield_type major_enantiomer measurement_method mechanism_status
structure_completeness review_status source_file_id source_locator source_row_key
dedup_status duplicate_group is_preferred curation_doi original_doi method_doi
ligand_label ligand_smiles ligand_inchikey ligand_structure_status sp2_smiles sp3_smiles
reactant_1_smiles reactant_2_smiles product_smiles scope_status selectivity_label_status
experimental_role outcome_status scope_evidence_level individual_original_SI_entry_verified
individual_catalyst_conditions_verified has_open_duplicate_candidate'''.split()
REQUIRED_FIELDS = '''record_id required_substrate_count substrate_structures_present
declared_extra_substrates extra_substrate_structures_present missing_extra_roles extra_smiles
source_verified_substrate_roles open_actual_input_structure_conflicts arity_basis arity_conflict
all_required_substrate_structures_present required_structure_slots_nonempty both_primary_SMILES_present
named_role_layout role_declaration_guard named_substrate_roles missing_named_roles named_substrate_smiles
role_layout_error_count required_substrate_arity_verified verified_required_substrate_count
verified_arity_all_required_structures_complete strict_input_structure_status
all_required_input_roles_independently_source_verified'''.split()
MOLECULE_FIELDS = '''molecule_id canonical_smiles source_smiles inchikey structure_status stereo_status
donor_atom_indices denticity coordination_status'''.split()
OBS_FIELDS = '''observation_id record_id dataset_id source_file_id source_row_key author_num excel_row
data_type author_doi author_reaction_type author_ligand_type ligand_id product_molecule_id temperature_K
ee_signed_author_percent ddg_author_kcal_mol ddg_abs_derived_kcal_mol mapping_status'''.split()
AUTHOR_FIELDS = {'author_ligand_smiles':'Ligand_SMILES','author_product_smiles':'Product_SMILES',
                 'author_ligand_label':'L_Num','author_product_label':'P_Num','author_reference':'Ref'}
PAPER_FIELDS = 'paper_id doi title journal year url source_kind si_url si_access_status checked_date extraction_status'.split()
COMPONENT_FIELDS = 'record_id ordinal role name molecule_id amount_value amount_unit ratio_value'.split()
SOURCE_FIELDS = 'file_id paper_id role original_url sha256 access_status'.split()
MEMBERSHIP_FIELDS = 'record_id dataset_id source_row_key source_locator'.split()
DATASET_FIELDS = 'dataset_id name reported_size extracted_size paper_id source_locator'.split()
INPUT_FIELDS = '''record_id partner_role molecule_id physical_substrate_count source_file_id
source_sha256 source_doi connectivity_status stereo_status formula'''.split()
FLOAT_FIELDS = set('''ni_loading_mol_percent ligand_loading_mol_percent temperature_C temperature_K reaction_time_h
ee_magnitude_percent ee_signed_source_percent er_major er_minor ddg_reported_kcal_mol ddg_abs_derived_kcal_mol
yield_percent ee_signed_author_percent ddg_author_kcal_mol amount_value ee_percent delta_delta_g_kcal_mol'''.split())
INT_FIELDS = set('''year is_preferred ordinal author_num excel_row denticity reported_size extracted_size
public_membership_count individual_original_SI_entry_verified individual_catalyst_conditions_verified
has_open_duplicate_candidate in_main_scope required_substrate_count substrate_structures_present
declared_extra_substrates extra_substrate_structures_present source_verified_substrate_roles
open_actual_input_structure_conflicts arity_conflict all_required_substrate_structures_present
required_structure_slots_nonempty both_primary_SMILES_present role_declaration_guard role_layout_error_count
required_substrate_arity_verified verified_required_substrate_count verified_arity_all_required_structures_complete
all_required_input_roles_independently_source_verified physical_substrate_count ordinal observation_preferred
replicate_count value_variant_count source_locator_compacted physical_stock_count strict_completion_credit
original_reference_unidentified'''.split())
INT_FIELDS.update(['review_status_public_sanitized','stereo_status_public_summarized'])
TABLES = {
 'metadata': (['key','value'], ['PRIMARY KEY(key)']),
 'papers': (PAPER_FIELDS+['license_status','license_evidence_url'], ['PRIMARY KEY(paper_id)']),
 'source_files': (SOURCE_FIELDS+['license_status'], ['PRIMARY KEY(file_id)','FOREIGN KEY(paper_id) REFERENCES papers(paper_id)']),
 'molecules': (MOLECULE_FIELDS+['stereo_status_public_summarized'], ['PRIMARY KEY(molecule_id)']),
 'datasets': (DATASET_FIELDS+['public_membership_count'], ['PRIMARY KEY(dataset_id)','FOREIGN KEY(paper_id) REFERENCES papers(paper_id)']),
 'records': (RECORD_FIELDS+['in_main_scope','replicate_count','value_variant_count','original_reference_unidentified','review_status_public_sanitized'],
  ['PRIMARY KEY(record_id)'] + [f'FOREIGN KEY({f}) REFERENCES papers(paper_id)' for f in ['paper_id','original_paper_id','method_paper_id']]
  + [f'FOREIGN KEY({f}) REFERENCES molecules(molecule_id)' for f in ['ligand_id','sp2_molecule_id','sp3_molecule_id','product_molecule_id']]
  + ['FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)']),
 'required_substrate_status': (REQUIRED_FIELDS, ['PRIMARY KEY(record_id)','FOREIGN KEY(record_id) REFERENCES records(record_id)']),
 'experiment_components': (COMPONENT_FIELDS, ['PRIMARY KEY(record_id,ordinal)','FOREIGN KEY(record_id) REFERENCES records(record_id)','FOREIGN KEY(molecule_id) REFERENCES molecules(molecule_id)']),
 'dataset_memberships': (MEMBERSHIP_FIELDS, ['PRIMARY KEY(record_id,dataset_id,source_row_key)','FOREIGN KEY(record_id) REFERENCES records(record_id)','FOREIGN KEY(dataset_id) REFERENCES datasets(dataset_id)']),
 'source_observations': (OBS_FIELDS+list(AUTHOR_FIELDS)+['observation_preferred'], ['PRIMARY KEY(observation_id)','FOREIGN KEY(record_id) REFERENCES records(record_id)','FOREIGN KEY(dataset_id) REFERENCES datasets(dataset_id)','FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)','FOREIGN KEY(ligand_id) REFERENCES molecules(molecule_id)','FOREIGN KEY(product_molecule_id) REFERENCES molecules(molecule_id)']),
 'observation_quality_flags': (['observation_id','flag'], ['PRIMARY KEY(observation_id,flag)','FOREIGN KEY(observation_id) REFERENCES source_observations(observation_id)']),
 'record_quality_flags': (['record_id','flag_origin','flag'], ['PRIMARY KEY(record_id,flag_origin,flag)','FOREIGN KEY(record_id) REFERENCES records(record_id)']),
 'open_quality_issues': (['issue_id','record_id','molecule_id','paper_id','issue_type','severity'], ['PRIMARY KEY(issue_id)','FOREIGN KEY(record_id) REFERENCES records(record_id)','FOREIGN KEY(molecule_id) REFERENCES molecules(molecule_id)','FOREIGN KEY(paper_id) REFERENCES papers(paper_id)']),
 'duplicate_pairs': (['pair_id','record_id_a','record_id_b','status','canonical_id'], ['PRIMARY KEY(pair_id)']+[f'FOREIGN KEY({f}) REFERENCES records(record_id)' for f in ['record_id_a','record_id_b','canonical_id']]),
 'input_structure_evidence': (['evidence_id']+INPUT_FIELDS+['source_locator_anchor','source_locator_compacted','stereo_status_public_summarized'], ['PRIMARY KEY(evidence_id)','FOREIGN KEY(record_id) REFERENCES records(record_id)','FOREIGN KEY(molecule_id) REFERENCES molecules(molecule_id)','FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)']),
 'stock_representation_caveats': (['record_id','partner_role','source_stock_label','physical_stock_count','physical_substrate_count','representation','review_status','strict_completion_credit','source_file_id','source_doi'], ['PRIMARY KEY(record_id,partner_role)','FOREIGN KEY(record_id) REFERENCES records(record_id)','FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)']),
 'reported_value_details': (['record_id','detail_kind','ordinal','ee_percent','yield_percent','delta_delta_g_kcal_mol','source_locator','source_url','source_sha256'], ['PRIMARY KEY(record_id,detail_kind,ordinal)','FOREIGN KEY(record_id) REFERENCES records(record_id)']),
}
VIEWS = '''CREATE VIEW main_scope_records AS SELECT * FROM records WHERE in_main_scope=1;
CREATE VIEW main_scope_numeric_ee AS SELECT * FROM main_scope_records WHERE ee_magnitude_percent IS NOT NULL;
CREATE VIEW main_scope_without_open_duplicate_flags AS SELECT * FROM main_scope_records WHERE has_open_duplicate_candidate=0;
CREATE VIEW archive_records AS SELECT * FROM records WHERE in_main_scope=0;
CREATE VIEW numeric_ee_with_required_structures AS
 SELECT r.*, s.strict_input_structure_status FROM main_scope_numeric_ee r
 JOIN required_substrate_status s USING(record_id)
 WHERE s.all_required_substrate_structures_present=1 AND length(trim(r.ligand_smiles))>0;
'''

def sha(path):
    with open(path,'rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def readonly(path):
    c=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA query_only=ON')
    return c

def read(c, table, fields=None):
    fs=','.join(fields) if fields else '*'
    return [dict(r) for r in c.execute(f'SELECT {fs} FROM {table}')]

def project(row,fields):
    return {k:row.get(k) for k in fields}

def compact_locator(value):
    """Keep filename + short page/table anchors, never narrative SI quotations."""
    if not value:
        return None
    file_match=re.search(r'([\w.-]+\.(?:pdf|xlsx|csv))',value,re.I)
    anchors=re.findall(r'(?:physical\s*)?PDF\s*(?:pages?\s*)?[\[\d][\d\s,–−\-\]]*|\bS\d+(?:[–−\-]S?\d+)?\b|\b(?:Table|Figure)\s*S?\d+[\w\-]*',value,re.I)
    bits=([file_match.group(1)] if file_match else [])+list(dict.fromkeys(a.strip() for a in anchors))
    return ' / '.join(bits)[:240] or 'See record source_locator and source DOI'

def detail_locator(loc):
    return ' / '.join(f'{k}={loc[k]}' for k in ['source_file','sheet','excel_row','pdf_page','printed_page','table','data_row','run'] if loc.get(k) is not None)

def public_review_status(value):
    if value is None: return None
    # Remove only a complete private-comparison token, preserving all unrelated bytes.
    value=re.sub(r'(?:;\s*)?not_exact_G0_[A-Za-z0-9_]+(?=;|$)', '', value)
    return value.replace('photoredox_Ni_expanded_scope_not_exact_G0', 'photoredox_Ni_expanded_scope')

def public_stereo_status(value):
    # Two individually inspected exceptions, not a length-based or semantic rewrite.
    if value and value.startswith('single constitutional isomer, supplied as a GEOMETRIC (E/Z) MIXTURE.'):
        return ('source_reported_geometric_mixture_E:Z_93:7; stock_not_assigned_as_pure_E; '
                'source_1e_drawing_represents_major_E_component_only; '
                'input_configuration_not_inferred_from_product; source_SI_PDF21_S21')
    if value and value.startswith('Actual using spells N-Boc-leucine without L/D/R/S,'):
        return ('source_named_N_Boc_leucine_without_absolute_stereodescriptor; neutral_free_COOH_NHBoc_isobutyl_graph; '
                'alpha_configuration_unassigned; racemic_or_enantiopure_stock_not_asserted; '
                'bottle_lot_and_product_CIP_unknown; graph_contains_no_at_stereo_tag')
    return value

def schema():
    parts=['PRAGMA foreign_keys=ON;']
    for table,(fields,constraints) in TABLES.items():
        cols=[f'  {f} '+('REAL' if f in FLOAT_FIELDS else 'INTEGER' if f in INT_FIELDS else 'TEXT') for f in fields]
        parts.append(f'CREATE TABLE {table} (\n'+',\n'.join(cols+['  '+c for c in constraints])+'\n);')
    return '\n\n'.join(parts)+'\n\n'+VIEWS

def extract(c):
    source_papers={p['paper_id']:p for p in read(c,'papers')}
    private_papers={p['paper_id'] for p in source_papers.values() if p['source_kind']=='local_experiment'}|{'P_LOCAL_G0'}
    all_records=read(c,'v_scope_assessment')
    records=[r for r in all_records if not any(r[k] in private_papers for k in ['paper_id','original_paper_id','method_paper_id'])]
    ids={r['record_id'] for r in records}
    target_ids={r['record_id'] for r in read(c,'v_scope_target_records',['record_id'])}
    components=[r for r in read(c,'experiment_components') if r['record_id'] in ids]
    memberships=[r for r in read(c,'dataset_memberships') if r['record_id'] in ids]
    observations=[r for r in read(c,'source_observations') if r['record_id'] in ids]
    inputs=[r for r in read(c,'substrate_structure_evidence') if r['record_id'] in ids]
    stocks=[r for r in read(c,'substrate_stock_ensemble_candidates') if r['record_id'] in ids]
    dataset_ids={r['dataset_id'] for r in memberships+observations}
    datasets=[r for r in read(c,'datasets') if r['dataset_id'] in dataset_ids and r['paper_id'] not in private_papers]
    assert dataset_ids=={r['dataset_id'] for r in datasets}
    file_ids={r['source_file_id'] for r in records+observations+inputs+stocks if r.get('source_file_id')}
    files=[r for r in read(c,'source_files') if r['file_id'] in file_ids and r['paper_id'] not in private_papers]
    assert file_ids=={r['file_id'] for r in files}
    paper_ids={r[k] for r in records for k in ['paper_id','original_paper_id','method_paper_id'] if r[k]}
    paper_ids|={r['paper_id'] for r in files+datasets}
    molecule_ids={r[k] for r in records for k in ['ligand_id','sp2_molecule_id','sp3_molecule_id','product_molecule_id'] if r[k]}
    molecule_ids|={r['molecule_id'] for r in components+inputs if r['molecule_id']}
    molecule_ids|={r[k] for r in observations for k in ['ligand_id','product_molecule_id']}
    out={t:[] for t in TABLES}
    metadata={'release_id':RELEASE,'release_status':'prepared_for_public_release','schema_version':'1.0',
      'dataset_identity':'literature-only public derivative; NOT the frozen user-designated v2',
      'baseline_relative_path':SOURCE_RELATIVE_PATH,'baseline_sha256':SOURCE_SHA256,
      'baseline_metadata_version':'1.4.66','baseline_metadata_as_of':'2026-10-07',
      'statistical_unit':'source-result row; not a proven independent physical experiment',
      'license_status':'MIT: original code; CC-BY-4.0: curator-controlled original documentation/curation rights only; third-party applicability unverified',
      'filter':'exclude local_experiment papers in curation/original/method references; retain other archive and scope-pending rows',
      'flag_origin':'materialized frozen v2 views; no new primary-source audit'}
    out['metadata']=[{'key':k,'value':v} for k,v in metadata.items()]
    out['papers']=[dict(project(source_papers[k],PAPER_FIELDS),license_status='not_verified_for_redistribution',license_evidence_url=None) for k in paper_ids]
    out['source_files']=[dict(project(r,SOURCE_FIELDS),license_status='not_verified_for_redistribution') for r in files]
    for r in read(c,'molecules'):
        if r['molecule_id'] not in molecule_ids: continue
        row=project(r,MOLECULE_FIELDS)
        row['stereo_status']=public_stereo_status(r['stereo_status'])
        row['stereo_status_public_summarized']=int(row['stereo_status']!=r['stereo_status'])
        out['molecules'].append(row)
    for r in datasets:
        row=project(r,DATASET_FIELDS)
        row['public_membership_count']=sum(m['dataset_id']==r['dataset_id'] for m in memberships)
        out['datasets'].append(row)
    for r in records:
        raw=json.loads(r['raw_record_json'])
        row=project(r,RECORD_FIELDS)
        row['review_status']=public_review_status(r['review_status'])
        row['review_status_public_sanitized']=int(row['review_status']!=r['review_status'])
        unidentified=not r['original_paper_id'] or source_papers[r['original_paper_id']]['source_kind']=='unidentified_reference'
        row.update(in_main_scope=int(r['record_id'] in target_ids),replicate_count=len(raw.get('replicate_results',[])),
                   value_variant_count=len(raw.get('reported_value_variants',[])),original_reference_unidentified=int(unidentified))
        out['records'].append(row)
        for origin in ['quality_flags','review_flags']:
            for flag in raw.get(origin,[]):
                assert isinstance(flag,str)
                out['record_quality_flags'].append({'record_id':r['record_id'],'flag_origin':origin,'flag':flag})
        for kind,key in [('reported_replicate','replicate_results'),('reported_variant','reported_value_variants')]:
            for ordinal,d in enumerate(raw.get(key,[]),1):
                loc=d.get('locator',{})
                out['reported_value_details'].append(dict(record_id=r['record_id'],detail_kind=kind,ordinal=ordinal,
                  ee_percent=d.get('ee_percent'),yield_percent=d.get('yield_percent'),delta_delta_g_kcal_mol=d.get('delta_delta_g_kcal_mol'),
                  source_locator=detail_locator(loc),source_url=loc.get('source_url'),source_sha256=loc.get('source_file_sha256')))
    out['required_substrate_status']=[project(r,REQUIRED_FIELDS) for r in read(c,'v_verified_required_substrate_status') if r['record_id'] in ids]
    out['experiment_components']=[project(r,COMPONENT_FIELDS) for r in components]
    out['dataset_memberships']=[project(r,MEMBERSHIP_FIELDS) for r in memberships]
    for r in observations:
        preferred=min(o['author_num'] for o in observations if o['record_id']==r['record_id'] and o['dataset_id']==r['dataset_id'])==r['author_num']
        row=dict(project(r,OBS_FIELDS),observation_preferred=int(preferred))
        raw=json.loads(r['raw_record_json'])
        row.update({public:raw.get(original) for public,original in AUTHOR_FIELDS.items()})
        out['source_observations'].append(row)
        out['observation_quality_flags'] += [{'observation_id':r['observation_id'],'flag':f} for f in json.loads(r['quality_flags_json'])]
    for r in read(c,'review_queue'):
        if r['status']!='open': continue
        if any(r[k] is not None and r[k] not in allowed for k,allowed in [('record_id',ids),('molecule_id',molecule_ids),('paper_id',paper_ids)]): continue
        if not any(r[k] is not None for k in ['record_id','molecule_id','paper_id']): continue
        out['open_quality_issues'].append(project(r,TABLES['open_quality_issues'][0]))
    for r in read(c,'duplicate_audit_pairs'):
        if r['record_id_a'] in ids and r['record_id_b'] in ids and (r['canonical_id'] is None or r['canonical_id'] in ids):
            out['duplicate_pairs'].append(project(r,TABLES['duplicate_pairs'][0]))
    for r in inputs:
        row=dict(project(r,INPUT_FIELDS),source_locator_anchor=compact_locator(r['source_locator']),source_locator_compacted=1)
        row['stereo_status']=public_stereo_status(r['stereo_status'])
        row['stereo_status_public_summarized']=int(row['stereo_status']!=r['stereo_status'])
        row['evidence_id']='E_'+hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()[:24]
        out['input_structure_evidence'].append(row)
    for r in stocks:
        row=project(r,TABLES['stock_representation_caveats'][0]);row['representation']=json.loads(r['definition_json']).get('representation')
        out['stock_representation_caveats'].append(row)
    for table, rows in out.items():
        fields=TABLES[table][0]
        # Deduplicate identical flags/evidence across internal batch histories; no numeric aggregation.
        unique={tuple(r[f] for f in fields):r for r in rows}
        out[table]=sorted(unique.values(),key=lambda r:json.dumps([r[f] for f in fields],ensure_ascii=False))
    return out

def counts(c):
    result={t:c.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in TABLES}
    result.update({t:c.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in ['main_scope_records','main_scope_numeric_ee','archive_records','numeric_ee_with_required_structures','main_scope_without_open_duplicate_flags']})
    return result

def write_checksums(root):
    ignored={'SHA256SUMS'}
    paths=[p for p in root.rglob('*') if p.is_file() and p.name not in ignored and '.git' not in p.parts and '__pycache__' not in p.parts]
    (root/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in sorted(paths)),encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT)
    args=parser.parse_args()
    if sha(args.source)!=SOURCE_SHA256: raise SystemExit('REFUSED: source SHA-256 differs from frozen v2')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);(out/'data').mkdir(exist_ok=True)
    db=out/'data'/'NiAsymCoupling_v2_public.sqlite'
    if args.source.resolve()==db: raise SystemExit('REFUSED: input equals output')
    if db.exists(): raise SystemExit('REFUSED: output database exists; choose a new output directory')
    src=readonly(args.source)
    if dict(src.execute("SELECT key,value FROM metadata WHERE key IN ('version','as_of')"))!={'version':'1.4.66','as_of':'2026-10-07'}:
        raise SystemExit('REFUSED: unexpected baseline metadata')
    tables=extract(src)
    src.close()
    ddl=schema();(out/'schema.sql').write_text(ddl,encoding='utf-8')
    conn=sqlite3.connect(db);conn.executescript(ddl)
    with conn:
        for table,(fields,_) in TABLES.items():
            conn.executemany(f'INSERT INTO {table} VALUES ('+','.join('?' for _ in fields)+')',[[r[f] for f in fields] for r in tables[table]])
    assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    metrics=counts(conn)
    for table in ['papers','source_files','datasets','records','source_observations','required_substrate_status','dataset_memberships']:
        fields=TABLES[table][0]
        with (out/'data'/f'{table}.csv').open('w',encoding='utf-8',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(fields)
            writer.writerows(conn.execute(f'SELECT * FROM {table} ORDER BY '+','.join(fields[:1])))
    conn.close()
    assert sha(args.source)==SOURCE_SHA256
    manifest={'release_id':RELEASE,'status':'prepared_for_public_release','created_on':'2026-10-10',
      'version':'2.0.0','repository':REPOSITORY,
      'download_url':REPOSITORY+'/releases/download/v2.0.0/NiAsymCoupling-v2.0.0.zip',
      'source_candidate':{'release_id':'v2-public-literature-2026-10-08-candidate','database_sha256':SOURCE_CANDIDATE_SHA256},
      'release_transition':'Scientific tables and seven CSV files unchanged from the reviewed 2026-10-08 public candidate; release metadata, documentation and scoped licenses updated',
      'baseline':{'relative_path':SOURCE_RELATIVE_PATH,'sha256':SOURCE_SHA256,'metadata_version':'1.4.66','metadata_as_of':'2026-10-07'},
      'database':{'path':'data/NiAsymCoupling_v2_public.sqlite','sha256':sha(db)},'counts':metrics,
      'exclusion':{'local_experiment_result_rows':36,'all_linked_local_only_material':'excluded'},
      'statistical_unit':'source-result rows and separate source observations; do not sum the two',
      'rights_review':'Scoped grants cover only curator-controlled rights; original upstream status fields remain not_verified_for_redistribution; no blanket relicense of facts or third-party protected material',
      'reproducibility':'logical rows and allowlisted projections are deterministic; SQLite file bytes may vary across SQLite versions'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    write_checksums(out)
    print(json.dumps(metrics,indent=2))

if __name__=='__main__': main()
