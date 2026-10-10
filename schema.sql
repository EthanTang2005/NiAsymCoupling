PRAGMA foreign_keys=ON;

CREATE TABLE metadata (
  key TEXT,
  value TEXT,
  PRIMARY KEY(key)
);

CREATE TABLE papers (
  paper_id TEXT,
  doi TEXT,
  title TEXT,
  journal TEXT,
  year INTEGER,
  url TEXT,
  source_kind TEXT,
  si_url TEXT,
  si_access_status TEXT,
  checked_date TEXT,
  extraction_status TEXT,
  license_status TEXT,
  license_evidence_url TEXT,
  PRIMARY KEY(paper_id)
);

CREATE TABLE source_files (
  file_id TEXT,
  paper_id TEXT,
  role TEXT,
  original_url TEXT,
  sha256 TEXT,
  access_status TEXT,
  license_status TEXT,
  PRIMARY KEY(file_id),
  FOREIGN KEY(paper_id) REFERENCES papers(paper_id)
);

CREATE TABLE molecules (
  molecule_id TEXT,
  canonical_smiles TEXT,
  source_smiles TEXT,
  inchikey TEXT,
  structure_status TEXT,
  stereo_status TEXT,
  donor_atom_indices TEXT,
  denticity INTEGER,
  coordination_status TEXT,
  stereo_status_public_summarized INTEGER,
  PRIMARY KEY(molecule_id)
);

CREATE TABLE datasets (
  dataset_id TEXT,
  name TEXT,
  reported_size INTEGER,
  extracted_size INTEGER,
  paper_id TEXT,
  source_locator TEXT,
  public_membership_count INTEGER,
  PRIMARY KEY(dataset_id),
  FOREIGN KEY(paper_id) REFERENCES papers(paper_id)
);

CREATE TABLE records (
  record_id TEXT,
  paper_id TEXT,
  original_paper_id TEXT,
  method_paper_id TEXT,
  reaction_family TEXT,
  catalyst_scope TEXT,
  catalyst_metal TEXT,
  bond_type TEXT,
  experiment_type TEXT,
  measurement_kind TEXT,
  reaction_key TEXT,
  sp2_partner_class TEXT,
  sp3_partner_type TEXT,
  ligand_id TEXT,
  ligand_source_label TEXT,
  sp2_molecule_id TEXT,
  sp3_molecule_id TEXT,
  product_molecule_id TEXT,
  ni_precursor TEXT,
  ni_loading_mol_percent REAL,
  ligand_loading_mol_percent REAL,
  solvent TEXT,
  solvent_ratio TEXT,
  temperature_text TEXT,
  temperature_C REAL,
  temperature_K REAL,
  reaction_time_h REAL,
  result_class TEXT,
  ee_raw TEXT,
  ee_magnitude_percent REAL,
  ee_signed_source_percent REAL,
  ee_direction_convention TEXT,
  er_raw TEXT,
  er_major REAL,
  er_minor REAL,
  ddg_reported_kcal_mol REAL,
  ddg_reported_convention TEXT,
  ddg_abs_derived_kcal_mol REAL,
  target_status TEXT,
  yield_percent REAL,
  yield_raw TEXT,
  yield_type TEXT,
  major_enantiomer TEXT,
  measurement_method TEXT,
  mechanism_status TEXT,
  structure_completeness TEXT,
  review_status TEXT,
  source_file_id TEXT,
  source_locator TEXT,
  source_row_key TEXT,
  dedup_status TEXT,
  duplicate_group TEXT,
  is_preferred INTEGER,
  curation_doi TEXT,
  original_doi TEXT,
  method_doi TEXT,
  ligand_label TEXT,
  ligand_smiles TEXT,
  ligand_inchikey TEXT,
  ligand_structure_status TEXT,
  sp2_smiles TEXT,
  sp3_smiles TEXT,
  reactant_1_smiles TEXT,
  reactant_2_smiles TEXT,
  product_smiles TEXT,
  scope_status TEXT,
  selectivity_label_status TEXT,
  experimental_role TEXT,
  outcome_status TEXT,
  scope_evidence_level TEXT,
  individual_original_SI_entry_verified INTEGER,
  individual_catalyst_conditions_verified INTEGER,
  has_open_duplicate_candidate INTEGER,
  in_main_scope INTEGER,
  replicate_count INTEGER,
  value_variant_count INTEGER,
  original_reference_unidentified INTEGER,
  review_status_public_sanitized INTEGER,
  PRIMARY KEY(record_id),
  FOREIGN KEY(paper_id) REFERENCES papers(paper_id),
  FOREIGN KEY(original_paper_id) REFERENCES papers(paper_id),
  FOREIGN KEY(method_paper_id) REFERENCES papers(paper_id),
  FOREIGN KEY(ligand_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(sp2_molecule_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(sp3_molecule_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(product_molecule_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)
);

CREATE TABLE required_substrate_status (
  record_id TEXT,
  required_substrate_count INTEGER,
  substrate_structures_present INTEGER,
  declared_extra_substrates INTEGER,
  extra_substrate_structures_present INTEGER,
  missing_extra_roles TEXT,
  extra_smiles TEXT,
  source_verified_substrate_roles INTEGER,
  open_actual_input_structure_conflicts INTEGER,
  arity_basis TEXT,
  arity_conflict INTEGER,
  all_required_substrate_structures_present INTEGER,
  required_structure_slots_nonempty INTEGER,
  both_primary_SMILES_present INTEGER,
  named_role_layout TEXT,
  role_declaration_guard INTEGER,
  named_substrate_roles TEXT,
  missing_named_roles TEXT,
  named_substrate_smiles TEXT,
  role_layout_error_count INTEGER,
  required_substrate_arity_verified INTEGER,
  verified_required_substrate_count INTEGER,
  verified_arity_all_required_structures_complete INTEGER,
  strict_input_structure_status TEXT,
  all_required_input_roles_independently_source_verified INTEGER,
  PRIMARY KEY(record_id),
  FOREIGN KEY(record_id) REFERENCES records(record_id)
);

CREATE TABLE experiment_components (
  record_id TEXT,
  ordinal INTEGER,
  role TEXT,
  name TEXT,
  molecule_id TEXT,
  amount_value REAL,
  amount_unit TEXT,
  ratio_value TEXT,
  PRIMARY KEY(record_id,ordinal),
  FOREIGN KEY(record_id) REFERENCES records(record_id),
  FOREIGN KEY(molecule_id) REFERENCES molecules(molecule_id)
);

CREATE TABLE dataset_memberships (
  record_id TEXT,
  dataset_id TEXT,
  source_row_key TEXT,
  source_locator TEXT,
  PRIMARY KEY(record_id,dataset_id,source_row_key),
  FOREIGN KEY(record_id) REFERENCES records(record_id),
  FOREIGN KEY(dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE source_observations (
  observation_id TEXT,
  record_id TEXT,
  dataset_id TEXT,
  source_file_id TEXT,
  source_row_key TEXT,
  author_num INTEGER,
  excel_row INTEGER,
  data_type TEXT,
  author_doi TEXT,
  author_reaction_type TEXT,
  author_ligand_type TEXT,
  ligand_id TEXT,
  product_molecule_id TEXT,
  temperature_K REAL,
  ee_signed_author_percent REAL,
  ddg_author_kcal_mol REAL,
  ddg_abs_derived_kcal_mol REAL,
  mapping_status TEXT,
  author_ligand_smiles TEXT,
  author_product_smiles TEXT,
  author_ligand_label TEXT,
  author_product_label TEXT,
  author_reference TEXT,
  observation_preferred INTEGER,
  PRIMARY KEY(observation_id),
  FOREIGN KEY(record_id) REFERENCES records(record_id),
  FOREIGN KEY(dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY(source_file_id) REFERENCES source_files(file_id),
  FOREIGN KEY(ligand_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(product_molecule_id) REFERENCES molecules(molecule_id)
);

CREATE TABLE observation_quality_flags (
  observation_id TEXT,
  flag TEXT,
  PRIMARY KEY(observation_id,flag),
  FOREIGN KEY(observation_id) REFERENCES source_observations(observation_id)
);

CREATE TABLE record_quality_flags (
  record_id TEXT,
  flag_origin TEXT,
  flag TEXT,
  PRIMARY KEY(record_id,flag_origin,flag),
  FOREIGN KEY(record_id) REFERENCES records(record_id)
);

CREATE TABLE open_quality_issues (
  issue_id TEXT,
  record_id TEXT,
  molecule_id TEXT,
  paper_id TEXT,
  issue_type TEXT,
  severity TEXT,
  PRIMARY KEY(issue_id),
  FOREIGN KEY(record_id) REFERENCES records(record_id),
  FOREIGN KEY(molecule_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(paper_id) REFERENCES papers(paper_id)
);

CREATE TABLE duplicate_pairs (
  pair_id TEXT,
  record_id_a TEXT,
  record_id_b TEXT,
  status TEXT,
  canonical_id TEXT,
  PRIMARY KEY(pair_id),
  FOREIGN KEY(record_id_a) REFERENCES records(record_id),
  FOREIGN KEY(record_id_b) REFERENCES records(record_id),
  FOREIGN KEY(canonical_id) REFERENCES records(record_id)
);

CREATE TABLE input_structure_evidence (
  evidence_id TEXT,
  record_id TEXT,
  partner_role TEXT,
  molecule_id TEXT,
  physical_substrate_count INTEGER,
  source_file_id TEXT,
  source_sha256 TEXT,
  source_doi TEXT,
  connectivity_status TEXT,
  stereo_status TEXT,
  formula TEXT,
  source_locator_anchor TEXT,
  source_locator_compacted INTEGER,
  stereo_status_public_summarized INTEGER,
  PRIMARY KEY(evidence_id),
  FOREIGN KEY(record_id) REFERENCES records(record_id),
  FOREIGN KEY(molecule_id) REFERENCES molecules(molecule_id),
  FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)
);

CREATE TABLE stock_representation_caveats (
  record_id TEXT,
  partner_role TEXT,
  source_stock_label TEXT,
  physical_stock_count INTEGER,
  physical_substrate_count INTEGER,
  representation TEXT,
  review_status TEXT,
  strict_completion_credit INTEGER,
  source_file_id TEXT,
  source_doi TEXT,
  PRIMARY KEY(record_id,partner_role),
  FOREIGN KEY(record_id) REFERENCES records(record_id),
  FOREIGN KEY(source_file_id) REFERENCES source_files(file_id)
);

CREATE TABLE reported_value_details (
  record_id TEXT,
  detail_kind TEXT,
  ordinal INTEGER,
  ee_percent REAL,
  yield_percent REAL,
  delta_delta_g_kcal_mol REAL,
  source_locator TEXT,
  source_url TEXT,
  source_sha256 TEXT,
  PRIMARY KEY(record_id,detail_kind,ordinal),
  FOREIGN KEY(record_id) REFERENCES records(record_id)
);

CREATE VIEW main_scope_records AS SELECT * FROM records WHERE in_main_scope=1;
CREATE VIEW main_scope_numeric_ee AS SELECT * FROM main_scope_records WHERE ee_magnitude_percent IS NOT NULL;
CREATE VIEW main_scope_without_open_duplicate_flags AS SELECT * FROM main_scope_records WHERE has_open_duplicate_candidate=0;
CREATE VIEW archive_records AS SELECT * FROM records WHERE in_main_scope=0;
CREATE VIEW numeric_ee_with_required_structures AS
 SELECT r.*, s.strict_input_structure_status FROM main_scope_numeric_ee r
 JOIN required_substrate_status s USING(record_id)
 WHERE s.all_required_substrate_structures_present=1 AND length(trim(r.ligand_smiles))>0;
