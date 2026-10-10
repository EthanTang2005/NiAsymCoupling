# NiAsymCoupling v2.0.0

Release package prepared on 2026-10-10 for [EthanTang2005/NiAsymCoupling](https://github.com/EthanTang2005/NiAsymCoupling).

- Literature-only public derivative of the frozen project v2 (internal metadata 1.4.66, 2026-10-07); 36 local laboratory rows and their local-only material are excluded.
- 7,935 source-result rows; 4,596 main-scope rows; 4,416 main-scope numeric-ee rows; 6,567 separate author-table observations. These counts are not independent physical-experiment counts.
- Scientific tables and seven CSV exports are unchanged from the reviewed 2026-10-08 public candidate. This release changes identification metadata, documentation, citation metadata and the scoped license grants.
- Original code is MIT-licensed. CC BY 4.0 applies only to curator-controlled original documentation, curation/annotation and compilation rights. Facts are not newly restricted and third-party protected material is not relicensed. Upstream evidence and unresolved applicability remain explicit.

Download **[NiAsymCoupling-v2.0.0.zip](https://github.com/EthanTang2005/NiAsymCoupling/releases/download/v2.0.0/NiAsymCoupling-v2.0.0.zip)** and its **.sha256** sidecar from this release. The asset contains the complete SQLite/CSV data, documentation, code, manifest and internal SHA256SUMS. GitHub's automatic source-code ZIP/TAR files contain the repository files and omit the data asset. Extract the data asset and run `python3 -B scripts/verify_public.py` from its extracted root.

Verification covers package hashes, SQLite integrity/foreign keys, exact source projection, CSV consistency and exclusion markers. It does not newly audit every original SI, validate every molecular graph, prove experimental independence or establish universal prediction performance. See the provenance and limitations documents.
