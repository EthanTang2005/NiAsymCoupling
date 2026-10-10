# NiAsymCoupling v2.0.0 — literature-only public derivative

[中文说明](README.zh-CN.md)

A curated collection of source-reported reaction results for nickel asymmetric coupling, with molecular representations, conditions, selectivity labels, source locators, and explicit quality flags. The main scope is nickel-reported C(sp²)–C(sp³) bond formation; an archive preserves other and unresolved source rows.

**[Download the complete v2.0.0 data package](https://github.com/EthanTang2005/NiAsymCoupling/releases/download/v2.0.0/NiAsymCoupling-v2.0.0.zip)** · [ZIP SHA-256](https://github.com/EthanTang2005/NiAsymCoupling/releases/download/v2.0.0/NiAsymCoupling-v2.0.0.zip.sha256)

Version **2.0.0**, release package prepared **2026-10-10**, for [EthanTang2005/NiAsymCoupling](https://github.com/EthanTang2005/NiAsymCoupling). The data package contains SQLite, seven CSV exports, and the complete accompanying code/documentation. GitHub's automatic **Source code (zip/tar.gz)** downloads contain repository files only and omit the data.

Original code in `scripts/`, `examples/`, and `schema.sql` is licensed under MIT. CC BY 4.0 covers only curator-controlled original documentation, curation/annotations and compilation rights. These grants do not relicense third-party protected material or impose new restrictions on facts. Source-level rights applicability remains explicitly unverified where applicable; see [LICENSING.md](LICENSING.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). No dataset DOI or associated project publication is claimed.

This public derivative was built from the user-designated frozen v2, internal metadata version **1.4.66**, dated **2026-10-07**, SHA-256 `ada489cddda9bb948f044e0a558df82de5a4eb2340b1910c07a04606fab07c9d`. It has a simplified public schema and is **not the full frozen v2 database**. Local laboratory data and their linked source material are excluded.

| Population | Count | Unit |
|---|---:|---|
| All literature-derived result rows | 7,935 | Source-result rows |
| Main-scope result rows | 4,596 | Preferred rows under the original v2 scope predicate |
| Main scope with numeric ee magnitude | 4,416 | Source-result rows |
| Other / scope-pending archive | 3,339 | Source-result rows |
| Numeric main scope + required substrate structures present + ligand SMILES nonempty | 3,608 | Structural selection, not training eligibility |
| Linked author-table observations | 6,567 | Source observations; do not add to result-row counts |
| Referenced papers / datasets / molecules | 137 / 34 / 6,080 | Relational entities, not independent experiments |

Rows may represent reported means, repeated source statements, or secondary compilations. Neither the database size nor a lack of duplicate flags proves that the rows are independent physical experiments. Original source mapping, structure completeness, and missing values remain explicit.

## Download and use

Extract `NiAsymCoupling-v2.0.0.zip` and work inside its `NiAsymCoupling-v2.0.0/` directory. If you cloned the repository, first download this release asset, then merge the **contents** of that extracted directory into the clone root. `data/` must be beside `scripts/`, `examples/` and `manifest.json` before running the examples or verifier. A clone alone contains the code and documentation.

The release ZIP has an external `.sha256` sidecar; after extraction, `SHA256SUMS` verifies the individual package files.

- `data/NiAsymCoupling_v2_public.sqlite` (inside the release asset): complete public derivative, including normalized quality and evidence tables.
- `data/records.csv` (inside the release asset): all result rows; use `in_main_scope=1` for the main scope. Other CSVs provide papers, source files, datasets, memberships, source observations, and required-substrate status.
- [`schema.sql`](schema.sql), [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md), [`manifest.json`](manifest.json), and [`SHA256SUMS`](SHA256SUMS): schema, definitions, provenance/counts, and integrity.
- [`docs/PROVENANCE.md`](docs/PROVENANCE.md) and [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md): source meanings and scientific limitations.

Python **3.11+** and SQLite with JSON functions are sufficient. No third-party Python packages are needed to query, build, or validate the package.

```bash
python3 -B examples/query.py
python3 -B scripts/verify_public.py
```

```sql
SELECT record_id, original_doi, ee_magnitude_percent,
       ligand_smiles, has_open_duplicate_candidate
FROM main_scope_numeric_ee;
```

`numeric_ee_with_required_structures` adds the original required-substrate predicate and a nonempty ligand SMILES. It does **not** require every ligand structure, condition, absolute configuration, source mapping, or duplicate concern to be resolved. Use the relevant quality tables for your own stated selection criteria. Avoid row-random evaluation that can mix related source or reaction groups across splits.

## Rebuild and verify provenance

The private frozen source is intentionally not redistributed. Maintainers with that exact source can rebuild into a **new** directory:

The public package alone can be queried and validated. It cannot reconstruct the full frozen database from original SI: the private source snapshot and the earlier extraction/audit workflow are not included. The build script reproduces the public projection only for a holder of the exact source checksum.

```bash
python3 -B scripts/build_public.py --source /path/to/NiAsymCoupling_v2.sqlite --output /path/to/new-public-build
python3 -B scripts/verify_public.py --root /path/to/new-public-build --source /path/to/NiAsymCoupling_v2.sqlite
```

The builder refuses a different source hash and an existing output database. It reads the source in read-only mode and rechecks its hash afterward. Rebuilding reproduces the schema and data; README/license documentation remains versioned separately. Logical values are deterministic; SQLite file bytes can differ across SQLite versions.

For attribution, retain record IDs, source DOIs and locators, cite the original publications and data providers relevant to the subset used, and identify the exact derivative release and database checksum. Version-specific project citation metadata is in [CITATION.cff](CITATION.cff): Yichen Tang, *NiAsymCoupling: literature-only public derivative*, version 2.0.0 (2026-10-10).
