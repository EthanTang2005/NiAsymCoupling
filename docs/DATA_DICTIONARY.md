# Data dictionary

All tables use UTF-8 text. SQLite NULL means absent/unassigned, never numerical zero. CSV empty cells encode NULL; CSV cannot distinguish NULL from an empty source string. Binary flags use 1/0, and some inherited flags remain NULL where the source view does not assess that row. Source results are not proven independent physical experiments.

The schema has 17 tables and 5 convenience views. `schema.sql` is authoritative for keys and foreign keys. The public schema does not include the frozen database's raw JSON, source documents, audit histories or global molecule labels.

## Table meanings

| Table | Row unit and intended meaning |
|---|---|
| metadata | One release/baseline property. Values distinguish this derivative from frozen v2. |
| papers | A referenced curation, original-measurement or method publication. Access status is historical. |
| source_files | Metadata for a referenced source object; the source document is not bundled. |
| molecules | Molecular graph entity. Shared graph IDs do not imply shared experiments. |
| datasets | Source dataset definition; historical sizes are not current unique experiment counts. |
| records | One frozen-v2 source-result row after local-data exclusion. |
| required_substrate_status | Inherited required-input status, assessed only for main-scope rows. |
| experiment_components | Additional reactant roles, catalysts, solvents, additives and other components. |
| dataset_memberships | A source-row association; datasets overlap and membership counts must not be summed as experiments. |
| source_observations | An author-table observation linked to a result, retaining literal author values. |
| observation_quality_flags | A source-observation quality flag, including graph or provenance conflicts. |
| record_quality_flags | An inherited machine-readable quality/review flag for a result. |
| open_quality_issues | Open issue identifiers, type and severity, without internal narrative history. |
| duplicate_pairs | Two public result IDs and the inherited pair-assessment status. |
| input_structure_evidence | A deduplicated public projection of input graph evidence, without source quotations. |
| stock_representation_caveats | Source-defined unresolved stock representations; strict completion credit is zero. |
| reported_value_details | Reported replicate or value variant attached to a result; not a new result count. |

## Views and scope

- `main_scope_records`: `in_main_scope=1`, materialized from the exact frozen-v2 target view: scope status in_main_scope, nickel_reported catalyst scope, C(sp2)-C(sp3) bond type, and preferred result.
- `main_scope_numeric_ee`: main scope with non-NULL ee magnitude.
- `archive_records`: all other retained literature-derived rows.
- `main_scope_without_open_duplicate_flags`: main scope with no inherited open duplicate flag. Absence of a flag does not establish independence.
- `numeric_ee_with_required_structures`: numeric main scope, all_required_substrate_structures_present=1, and nonempty trimmed ligand SMILES. This is not a certified training set.

## Field definitions

Chemical graphs and inherited flags are reproduced from the frozen source; no chemical parser or new SI audit runs during export. Fields ending `_public_sanitized` or `_public_summarized` mark deliberate publication transformations documented in PROVENANCE.md.

### metadata

| Field | SQLite type | Meaning |
|---|---|---|
| `key` | TEXT | Metadata property name. |
| `value` | TEXT | Metadata property value. |

### papers

| Field | SQLite type | Meaning |
|---|---|---|
| `paper_id` | TEXT | Curation/compilation paper ID in records; the owning paper in other tables. |
| `doi` | TEXT | Publication DOI; retains the source spelling. |
| `title` | TEXT | Source publication title. |
| `journal` | TEXT | Journal or source publication venue. |
| `year` | INTEGER | Publication year when recorded. |
| `url` | TEXT | Publication landing/DOI URL. |
| `source_kind` | TEXT | Source category from the frozen bibliography; local_experiment is excluded. |
| `si_url` | TEXT | Source-paper supporting-information URL. |
| `si_access_status` | TEXT | Historical source-paper SI access state; not a fresh URL-health or rights check. |
| `checked_date` | TEXT | Historical bibliography/access check date. |
| `extraction_status` | TEXT | Historical extraction status; does not assert completeness. |
| `license_status` | TEXT | Redistribution applicability remains not_verified_for_redistribution; observed source terms are summarized in LICENSING.md. |
| `license_evidence_url` | TEXT | Reserved for a record-specific licensing assessment; currently NULL. |

### source_files

| Field | SQLite type | Meaning |
|---|---|---|
| `file_id` | TEXT | Stable source-file metadata ID. |
| `paper_id` | TEXT | Curation/compilation paper ID in records; the owning paper in other tables. |
| `role` | TEXT | Component or source-object role, according to its table. |
| `original_url` | TEXT | Source object URL carried from frozen v2. |
| `sha256` | TEXT | SHA-256 of the source object as recorded in frozen v2, not the public database. |
| `access_status` | TEXT | Historical source-file access state; local copies of public sources are not themselves redistributed. |
| `license_status` | TEXT | Redistribution applicability remains not_verified_for_redistribution; observed source terms are summarized in LICENSING.md. |

### molecules

| Field | SQLite type | Meaning |
|---|---|---|
| `molecule_id` | TEXT | Stable molecular graph ID. |
| `canonical_smiles` | TEXT | Curated canonical SMILES representation, as frozen; chemical validity not rechecked at export. |
| `source_smiles` | TEXT | Literal source molecular SMILES when present. |
| `inchikey` | TEXT | Stored InChIKey; not recomputed during export. |
| `structure_status` | TEXT | Inherited molecular structure quality/status. |
| `stereo_status` | TEXT | Inherited input/molecular stereochemistry status, with two explicit public-summary exceptions. |
| `donor_atom_indices` | TEXT | Stored donor-atom indexing convention; not a newly validated coordination model. |
| `denticity` | INTEGER | Stored ligand denticity. |
| `coordination_status` | TEXT | Coordination-model assignment/status; not a validated transition-state geometry. |
| `stereo_status_public_summarized` | INTEGER | 1 for either of the two individually documented stereo-description paraphrases. |

### datasets

| Field | SQLite type | Meaning |
|---|---|---|
| `dataset_id` | TEXT | Stable source dataset ID. |
| `name` | TEXT | Source dataset/component name; molecular global names are intentionally omitted. |
| `reported_size` | INTEGER | Historical source-declared dataset size. |
| `extracted_size` | INTEGER | Historical extraction metadata; can differ from current members. |
| `paper_id` | TEXT | Curation/compilation paper ID in records; the owning paper in other tables. |
| `source_locator` | TEXT | Result/dataset/value location in the source (file, page, table or row); some source filenames are aliases. |
| `public_membership_count` | INTEGER | Actual retained membership-row count in this public dataset; overlaps across datasets remain. |

### records

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `paper_id` | TEXT | Curation/compilation paper ID in records; the owning paper in other tables. |
| `original_paper_id` | TEXT | Assigned original measurement paper; NULL where unresolved. |
| `method_paper_id` | TEXT | Protocol/method paper reference; may differ from the original measurement paper. |
| `reaction_family` | TEXT | Curated reaction-family label. |
| `catalyst_scope` | TEXT | Inherited nickel/non-nickel/unresolved catalyst-scope assignment. |
| `catalyst_metal` | TEXT | Recorded catalyst metal label; NULL is not automatically non-nickel. |
| `bond_type` | TEXT | Curated formed-bond class, e.g. C(sp2)-C(sp3); archive includes other/unassigned classes. |
| `experiment_type` | TEXT | Source-result context/type (e.g. screen, preparative or author-curated result). |
| `measurement_kind` | TEXT | Measurement/aggregation granularity where known; may remain unspecified. |
| `reaction_key` | TEXT | Inherited reaction/group key; not guaranteed globally unique. |
| `sp2_partner_class` | TEXT | Source/curator class for sp2-role partner. |
| `sp3_partner_type` | TEXT | Source/curator class for sp3-role partner. |
| `ligand_id` | TEXT | Assigned ligand graph ID. |
| `ligand_source_label` | TEXT | Ligand source-row label. |
| `sp2_molecule_id` | TEXT | Legacy sp2 input-role graph ID; NULL does not by itself prove no input. |
| `sp3_molecule_id` | TEXT | Legacy sp3 input-role graph ID; named/multicomponent roles may be stored separately. |
| `product_molecule_id` | TEXT | Product graph ID; author observations can reference a different literal author representation. |
| `ni_precursor` | TEXT | Reported nickel precursor text. |
| `ni_loading_mol_percent` | REAL | Nickel loading in mol percent; NULL if absent/unassigned. |
| `ligand_loading_mol_percent` | REAL | Ligand loading in mol percent. |
| `solvent` | TEXT | Stored solvent text. |
| `solvent_ratio` | TEXT | Source solvent-ratio text; no implied unit conversion. |
| `temperature_text` | TEXT | Stored source temperature text; room temperature is not converted during export. |
| `temperature_C` | REAL | Recorded numeric degrees Celsius. |
| `temperature_K` | REAL | Recorded numeric kelvin; not imputed during export. |
| `reaction_time_h` | REAL | Reaction time in hours. |
| `result_class` | TEXT | Outcome label; distinguishes numeric outcomes from failure, qualitative racemic and missing outcomes. |
| `ee_raw` | TEXT | Stored ee label text, including nonnumeric source text. |
| `ee_magnitude_percent` | REAL | Absolute ee in percent, 0–100; not always a direct unrounded original measurement. |
| `ee_signed_source_percent` | REAL | Signed ee retained according to that source convention; cross-source R/S alignment is not implied. |
| `ee_direction_convention` | TEXT | Interpretation/limits of source ee sign. |
| `er_raw` | TEXT | Stored enantiomeric-ratio text; not diastereomeric ratio. |
| `er_major` | REAL | Stored major ER part. |
| `er_minor` | REAL | Stored minor ER part. |
| `ddg_reported_kcal_mol` | REAL | Reported energy-difference label in kcal/mol; not a computed transition-state barrier. |
| `ddg_reported_convention` | TEXT | Source convention/interpretation for reported energy label. |
| `ddg_abs_derived_kcal_mol` | REAL | Existing absolute energy difference derived from ee/temperature, kcal/mol; not recomputed here. |
| `target_status` | TEXT | Inherited availability/eligibility status for numeric targets. |
| `yield_percent` | REAL | Recorded yield (%); stage and basis require yield_type/source. |
| `yield_raw` | TEXT | Stored yield text, including bounded or nonnumeric labels. |
| `yield_type` | TEXT | Yield basis such as isolated or analytical. |
| `major_enantiomer` | TEXT | Recorded major-enantiomer assignment or unknown; no inference made from SMILES during export. |
| `measurement_method` | TEXT | Recorded analytical method. |
| `mechanism_status` | TEXT | Inherited mechanism assignment status, not a proof of mechanism. |
| `structure_completeness` | TEXT | Legacy broad completeness label; use dedicated required-substrate table for precise input checks. |
| `review_status` | TEXT | Inherited quality tokens after removing local-system comparison tokens; other tokens preserved. |
| `source_file_id` | TEXT | Foreign key to a referenced source object; no document bundled. |
| `source_locator` | TEXT | Result/dataset/value location in the source (file, page, table or row); some source filenames are aliases. |
| `source_row_key` | TEXT | Stable source-row key; its uniqueness is scoped by source/dataset/paper. |
| `dedup_status` | TEXT | Inherited record duplicate assessment. |
| `duplicate_group` | TEXT | Inherited duplicate grouping key, if assigned. |
| `is_preferred` | INTEGER | Inherited preferred-result selector; does not certify independent experiments. |
| `curation_doi` | TEXT | DOI of the curation/compilation source. |
| `original_doi` | TEXT | Assigned original measurement DOI; not inferred from method DOI. |
| `method_doi` | TEXT | Method/protocol DOI. |
| `ligand_label` | TEXT | Resolved source label or inherited name from v_records; not a cross-paper universal ligand name. |
| `ligand_smiles` | TEXT | Curated ligand graph materialized from original v_records. |
| `ligand_inchikey` | TEXT | Stored ligand InChIKey. |
| `ligand_structure_status` | TEXT | Inherited ligand graph quality status. |
| `sp2_smiles` | TEXT | Legacy sp2-role graph; use required-substrate status and named roles for complete input semantics. |
| `sp3_smiles` | TEXT | Legacy sp3-role graph; do not infer a missing physical input just from NULL. |
| `reactant_1_smiles` | TEXT | Original v_records result including its JSON-dependent no-fallback guard, materialized before JSON removal. |
| `reactant_2_smiles` | TEXT | Original v_records result including its JSON-dependent no-fallback guard, materialized before JSON removal. |
| `product_smiles` | TEXT | Curated product graph; does not alone prove experimental major absolute configuration. |
| `scope_status` | TEXT | Original assessment: in_main_scope, outside_main_scope, or pending_scope_verification. |
| `selectivity_label_status` | TEXT | Inherited numeric/qualitative/missing selectivity classification. |
| `experimental_role` | TEXT | Inherited experimental role in the scope assessment. |
| `outcome_status` | TEXT | Inherited scope-audit outcome status. |
| `scope_evidence_level` | TEXT | Inherited level of scope evidence. |
| `individual_original_SI_entry_verified` | INTEGER | Inherited 1/0 entry-verification flag; no fresh entry audit here. |
| `individual_catalyst_conditions_verified` | INTEGER | Inherited 1/0 catalyst/conditions verification flag. |
| `has_open_duplicate_candidate` | INTEGER | Inherited open duplicate/potential duplicate flag; zero does not prove independence. |
| `in_main_scope` | INTEGER | Exact membership of the original v2 target view after excluding local rows. |
| `replicate_count` | INTEGER | Number of nested reported replicate entries exported to reported_value_details. |
| `value_variant_count` | INTEGER | Number of nested reported value variants exported separately. |
| `original_reference_unidentified` | INTEGER | 1 if the assigned original measurement paper is absent or explicitly unidentified; public compilation provenance can still exist. |
| `review_status_public_sanitized` | INTEGER | 1 when a local-system comparison token was removed from review_status; unrelated bytes are preserved. |

### required_substrate_status

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `required_substrate_count` | INTEGER | Inherited required organic-input count; not number of all chemical components. |
| `substrate_structures_present` | INTEGER | Inherited count of present/source-supported substrate roles under that view. |
| `declared_extra_substrates` | INTEGER | Number of required roles additional to the legacy primary slots. |
| `extra_substrate_structures_present` | INTEGER | Number of additional role structures present. |
| `missing_extra_roles` | TEXT | Names of unresolved additional substrate roles. |
| `extra_smiles` | TEXT | Inherited extra-role SMILES summary. |
| `source_verified_substrate_roles` | INTEGER | Inherited number of source-verified substrate roles. |
| `open_actual_input_structure_conflicts` | INTEGER | Count of open actual-input graph conflicts under the original view. |
| `arity_basis` | TEXT | Evidence basis for required-input count. |
| `arity_conflict` | INTEGER | 1 where input-count/declaration conflicts exist. |
| `all_required_substrate_structures_present` | INTEGER | Original v2 required-role completeness predicate; not full record validity. |
| `required_structure_slots_nonempty` | INTEGER | Inherited role-slot availability predicate, separate from source verification. |
| `both_primary_SMILES_present` | INTEGER | Legacy two primary SMILES slots present; named layouts may legitimately yield 0. |
| `named_role_layout` | TEXT | Named required-input layout when primary sp2/sp3 roles are not sufficient. |
| `role_declaration_guard` | INTEGER | Inherited guard validating a named-role declaration. |
| `named_substrate_roles` | TEXT | Named physical-input role labels. |
| `missing_named_roles` | TEXT | Named roles still lacking required graphs. |
| `named_substrate_smiles` | TEXT | Named-role-to-SMILES summary. |
| `role_layout_error_count` | INTEGER | Inherited role-layout error count. |
| `required_substrate_arity_verified` | INTEGER | 1 when original view deems the physical input count verified. |
| `verified_required_substrate_count` | INTEGER | Verified required count, otherwise NULL. |
| `verified_arity_all_required_structures_complete` | INTEGER | Joint original arity/structure completeness predicate. |
| `strict_input_structure_status` | TEXT | Original strict input status: count pending, complete, or incomplete/conflicted. |
| `all_required_input_roles_independently_source_verified` | INTEGER | Inherited source-verification predicate; refers to prior frozen-db evidence, not this export review. |

### experiment_components

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `ordinal` | INTEGER | Stable order within the parent result. |
| `role` | TEXT | Component or source-object role, according to its table. |
| `name` | TEXT | Source dataset/component name; molecular global names are intentionally omitted. |
| `molecule_id` | TEXT | Stable molecular graph ID. |
| `amount_value` | REAL | Reported numerical component amount. |
| `amount_unit` | TEXT | Unit paired with amount_value. |
| `ratio_value` | TEXT | Stored component ratio text. |

### dataset_memberships

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `dataset_id` | TEXT | Stable source dataset ID. |
| `source_row_key` | TEXT | Stable source-row key; its uniqueness is scoped by source/dataset/paper. |
| `source_locator` | TEXT | Result/dataset/value location in the source (file, page, table or row); some source filenames are aliases. |

### source_observations

| Field | SQLite type | Meaning |
|---|---|---|
| `observation_id` | TEXT | Stable author-observation identifier; joins source_observations. |
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `dataset_id` | TEXT | Stable source dataset ID. |
| `source_file_id` | TEXT | Foreign key to a referenced source object; no document bundled. |
| `source_row_key` | TEXT | Stable source-row key; its uniqueness is scoped by source/dataset/paper. |
| `author_num` | INTEGER | Author table Num identifier, scoped to the dataset. |
| `excel_row` | INTEGER | One-based author workbook row index. |
| `data_type` | TEXT | Author table subgroup such as HTE or literature. |
| `author_doi` | TEXT | Literal DOI attributed by the author table; may differ from verified original source. |
| `author_reaction_type` | TEXT | Literal author reaction class. |
| `author_ligand_type` | TEXT | Literal author ligand class. |
| `ligand_id` | TEXT | Assigned ligand graph ID. |
| `product_molecule_id` | TEXT | Product graph ID; author observations can reference a different literal author representation. |
| `temperature_K` | REAL | Recorded numeric kelvin; not imputed during export. |
| `ee_signed_author_percent` | REAL | Literal signed author-table ee (%), separately preserved from selected result value. |
| `ddg_author_kcal_mol` | REAL | Literal author energy label in kcal/mol; author sign convention may differ from ee sign. |
| `ddg_abs_derived_kcal_mol` | REAL | Existing absolute energy difference derived from ee/temperature, kcal/mol; not recomputed here. |
| `mapping_status` | TEXT | Inherited mapping/duplicate/conflict status linking author observation to selected result. |
| `author_ligand_smiles` | TEXT | Literal author raw Ligand_SMILES; not overwritten by curated graphs. |
| `author_product_smiles` | TEXT | Literal author raw Product_SMILES; stereochemistry is not a verified major-enantiomer assignment. |
| `author_ligand_label` | TEXT | Literal author L_Num. |
| `author_product_label` | TEXT | Literal author P_Num. |
| `author_reference` | TEXT | Literal author reference citation text; attribution conflicts can remain. |
| `observation_preferred` | INTEGER | Minimum author Num for the record+dataset; selection convention, not evidence certification. |

### observation_quality_flags

| Field | SQLite type | Meaning |
|---|---|---|
| `observation_id` | TEXT | Stable author-observation identifier; joins source_observations. |
| `flag` | TEXT | Inherited quality/status text. |

### record_quality_flags

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `flag_origin` | TEXT | Source raw quality_flags or review_flags collection. |
| `flag` | TEXT | Inherited quality/status text. |

### open_quality_issues

| Field | SQLite type | Meaning |
|---|---|---|
| `issue_id` | TEXT | Inherited open issue ID. |
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `molecule_id` | TEXT | Stable molecular graph ID. |
| `paper_id` | TEXT | Curation/compilation paper ID in records; the owning paper in other tables. |
| `issue_type` | TEXT | Inherited open issue category, without internal free-text detail. |
| `severity` | TEXT | Inherited issue severity. |

### duplicate_pairs

| Field | SQLite type | Meaning |
|---|---|---|
| `pair_id` | TEXT | Inherited duplicate-pair ID. |
| `record_id_a` | TEXT | First result ID in a duplicate-assessment pair. |
| `record_id_b` | TEXT | Second result ID in a duplicate-assessment pair. |
| `status` | TEXT | Inherited duplicate-pair assessment status. |
| `canonical_id` | TEXT | Preferred canonical result ID if the source pair assessment assigns one. |

### input_structure_evidence

| Field | SQLite type | Meaning |
|---|---|---|
| `evidence_id` | TEXT | Deterministic hash ID of the public evidence projection; internal batch IDs omitted. |
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `partner_role` | TEXT | Physical-input/component role addressed by this evidence or stock caveat. |
| `molecule_id` | TEXT | Stable molecular graph ID. |
| `physical_substrate_count` | INTEGER | Recorded number of distinct physical organic substrates. |
| `source_file_id` | TEXT | Foreign key to a referenced source object; no document bundled. |
| `source_sha256` | TEXT | Recorded SHA-256 of the cited source object. |
| `source_doi` | TEXT | DOI anchoring the source-specific input evidence. |
| `connectivity_status` | TEXT | Inherited source-input connectivity assessment. |
| `stereo_status` | TEXT | Inherited input/molecular stereochemistry status, with two explicit public-summary exceptions. |
| `formula` | TEXT | Stored molecular formula for this evidence; no graph verification at export. |
| `source_locator_anchor` | TEXT | Compacted filename/page/table anchors only; consult record locator, source DOI and file metadata. |
| `source_locator_compacted` | INTEGER | 1: long internal evidence locator was projected to limited source anchors. |
| `stereo_status_public_summarized` | INTEGER | 1 for either of the two individually documented stereo-description paraphrases. |

### stock_representation_caveats

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `partner_role` | TEXT | Physical-input/component role addressed by this evidence or stock caveat. |
| `source_stock_label` | TEXT | Source-defined charged-stock label. |
| `physical_stock_count` | INTEGER | Number of charged stocks represented by this caveat. |
| `physical_substrate_count` | INTEGER | Recorded number of distinct physical organic substrates. |
| `representation` | TEXT | Source-bounded unresolved ensemble or stock representation category. |
| `review_status` | TEXT | Inherited quality tokens after removing local-system comparison tokens; other tokens preserved. |
| `strict_completion_credit` | INTEGER | Always 0 for stock candidate caveats; no strict completeness credit granted. |
| `source_file_id` | TEXT | Foreign key to a referenced source object; no document bundled. |
| `source_doi` | TEXT | DOI anchoring the source-specific input evidence. |

### reported_value_details

| Field | SQLite type | Meaning |
|---|---|---|
| `record_id` | TEXT | Stable result-row identifier retained from frozen v2. |
| `detail_kind` | TEXT | reported_replicate or reported_variant; never counted as an added result row. |
| `ordinal` | INTEGER | Stable order within the parent result. |
| `ee_percent` | REAL | Reported replicate/variant ee (%), preserving source sign. |
| `yield_percent` | REAL | Recorded yield (%); stage and basis require yield_type/source. |
| `delta_delta_g_kcal_mol` | REAL | Reported replicate/variant energy label in kcal/mol. |
| `source_locator` | TEXT | Result/dataset/value location in the source (file, page, table or row); some source filenames are aliases. |
| `source_url` | TEXT | URL associated with this particular reported value. |
| `source_sha256` | TEXT | Recorded SHA-256 of the cited source object. |
