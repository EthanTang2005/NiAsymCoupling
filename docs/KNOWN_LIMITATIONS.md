# Known limitations

- The archive is broader than nickel asymmetric C(sp²)–C(sp³) main scope. Use `in_main_scope=1` or the supplied main-scope views and state any additional filters.
- Result rows, author observations, dataset memberships, repeated statements and physical experiments are different units. Some outcomes are reported aggregates; some cross-source duplicates remain unresolved.
- A missing open duplicate flag is not independent proof that a record is novel or statistically independent. `duplicate_pairs`, `dedup_status`, `mapping_status` and quality flags should inform grouped splitting and deduplication.
- Original measurement and method references can be ambiguous. Public author compilations may contain unresolved attribution, source-graph conflicts or numerical inconsistencies; these rows are retained with their status.
- `structure_completeness` is a legacy broad field. Prefer the dedicated required-substrate table and molecular status columns. Empty role slots, named roles, whole-stock definitions, stereochemical ambiguity and source conflicts matter separately.
- Required-substrate completeness does not validate ligand identity, product absolute configuration, catalysts, solvent, condition mapping, target labels or training eligibility. Inherited independently-source-verified flags describe the frozen database's prior evidence, not an independent audit of every original SI in this release.
- Original author SMILES can differ from later curated molecular representations. The author fields are literal observations; assigning R/S from their product SMILES without corroborating evidence is unsafe scientifically.
- ee magnitude, signed source ee, ER, author energy labels and derived absolute energy labels are distinct. Sign conventions vary across sources. Qualitative racemic or no-reaction statements are not automatically numerical zero ee. Values at 100% ee need special treatment in logarithmic energy transforms.
- Temperatures and conditions can be missing, bounded or given as text. No fixed numeric room temperature was introduced during export. Existing frozen source values are carried through rather than recomputed.
- Historical source-file accessibility is not a current URL-health check. Source terms vary, and most record-level redistribution rights have not been verified; see LICENSING.md.
- This package contains no trained model or cross-source generalization claim. Numeric and structural subsets are candidates for an explicitly designed analysis, not certified modeling benchmarks.
- Build verification covers source identity, transformation, references, counts and privacy markers. It does not parse SMILES chemically or repeat the original experimental and source audits.
