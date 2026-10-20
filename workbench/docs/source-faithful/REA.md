# REA analysis of the executed source functions

REA is connected in this session. The targeted source is the retained original
validator/control factory `47381` and renderer entry factory `39852`. The
production loader executes those unchanged functions. A separate reviewer
checked all 46 factory byte slices against their four original bundles and
executed a different loader over the complete original chunks.

The initial REA inventory of bare factory files could not parse their anonymous
function expressions as standalone JavaScript programs: 46 parse failures.
[The recorded limitation](evidence/REA-BARE-FACTORIES.json) is preserved; this is
not counted as successful semantic analysis.

The follow-up placed the two unchanged factory expressions inside an inert
webpack registration carrier. [Carrier source bindings](evidence/REA-CARRIER.json)
record original offsets/hashes and the wrapper's hash. No original function body
was rewritten. REA read the carrier statically; it did not execute its bootstrap.
It parsed 12,357 AST nodes, recovered both modules and reported zero syntax
failures or truncated scopes. The complete result exceeded the MCP transport
budget, so the same retained result was read through `inspect_analysis_view`;
the analysis was not repeated to obtain a smaller response.

[Retained summary Evidence](evidence/REA-CARRIER-SUMMARY.json):
`ev_be9789edbaaabd6844b2e7d265a6e30a136dedb21132ea9ac89d5f3e8adba8ca`.
Parent: `ev_17500eba5c378e167ab149e48ea6b961e5516d09dacda80bf2fe1e2b1f368a72`.

The semantic graph remains conservative: 2,150 unknowns and partial call/object
relationships. Syntax/module recovery is not complete semantic or runtime
proof. The source-bound tests and independent original-bundle oracle supply
the separate execution evidence for the selected normalization, control and
rendering cases. No private neural model, server handler or complete deployment
identity follows from either analysis.
