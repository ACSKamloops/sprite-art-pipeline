# Current public contract delta

Unauthenticated official OpenAPI was captured from
<https://api.pixellab.ai/v2/openapi.json> on 2026-10-14. The unchanged bytes are
packaged as `contracts/openapi-current-20261014.json`, SHA256
`8cb24ecdd26e9fe48639dc789e44f32b3c78c29e8da8c3121f23ab360ade5dad`.

The earlier frozen registry has 111 public operations and 101 captured MCP tool
definitions. The refreshed public document has **112 operations**, with one new
`POST /normal-map`. Five existing operation descriptions changed; no previously
captured operation disappeared. The frozen registry remains a historical
contract view, and the full current snapshot/delta are available from the
original-source catalog. This prevents silently representing 212 frozen
definitions as the complete current API.

This refresh is byte-identical to the already retained
`docs/readiness/ANALYSIS-public/openapi.json`. It confirms the earlier
[analysis reconciliation](../readiness/ANALYSIS-RECONCILIATION.md); normal maps
are not a new research discovery in this phase. The addition here makes that
current contract/delta available to the installed source-method controller.

The normal-map contract prose describes a sprite or horizontal animation strip,
up to 32 frames, each frame 8–512 pixels per side. Its `frames` JSON Schema has a
minimum of 1 and **no maximum**; the prose limit is not a schema-enforced bound.
It describes a same-size PNG
normal map and asynchronous background-job completion. These are documented
contract claims, **not an observed execution or a recovered implementation**.
There is no local private normal-map handler. Its algorithm, part inference,
training data and temporal construction remain unavailable from the public
schema. No paid request was submitted for this addition.

Machine-readable added/removed/changed operations and source hashes are in
`contracts/PUBLIC-DELTA-20261014.json`. This contract refresh changes no original
capture or previous verification receipt.
