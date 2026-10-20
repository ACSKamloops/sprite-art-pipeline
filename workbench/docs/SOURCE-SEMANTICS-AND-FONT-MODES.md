# Explicit request admission and local font modes

`CapabilityRegistry.validate_request` continues to validate the unchanged frozen JSON schema. `validate_source_request` adds a separately identified `source-derived` layer for captured outfit-transfer limits and observed shared-palette dimension admission; it never invokes a vendor handler. Frozen-schema failures and source-rule failures carry `validation_layer` in structured errors. Other vendor requests report source semantics `not-covered`, not an implied full validation.

```
sprite-workbench validate-source-request public:POST:/transfer-outfit-v2 request.json
```

The HTTP `/api/invoke` and JSON Lines channel expose `local.requests.validate_source` with `{"capability":"public:POST:/transfer-outfit-v2","request":{...}}`. This is an offline local service, even when its subject is a vendor capability. Vendor invocation remains unsupported.

Outfit transfer allows2–15frames at32–64px,2–8 at65–80px and2–3 at81–256px. These branches are documented in the frozen public operation description and MCP description and independently implemented by shipped Lua `generate-transfer-outfit-pro.lua:53–66`; the Lua largest-input check also appears at122–160. Public v2 describes the cap by output `image_size`, so that is this public adapter's authority. Lua raw RGBA and public PNG grammars remain separate. The MCP adapter validates mutually exclusive frame/reference sources and reports `incomplete` if output dimensions require unavailable image metadata. It does not fetch URLs or assume default dimensions. Automatic chunking, remote generation and cross-chunk visual consistency are not implemented.

Font pipeline steps accept an optional `mode`, defaulting to `pillow`. Existing Pillow pixels, glyph metrics and receipt format are preserved. Explicit `freetype-no-hinting` uses uniform `FT_LOAD_RENDER | FT_LOAD_NO_HINTING | FT_LOAD_NO_AUTOHINT` (32774) for every glyph:

```json
{"version":1,"steps":[{"id":"font","action":"font","path":"source.ttf","characters":"Ag ij ","size":16,"mode":"freetype-no-hinting","timeout":10}]}
```

Use this JSON through the existing CLI `run`, HTTP `/api/plan`, or local pipeline job. The atlas retains the original immutable font-byte snapshot and rasterization receipt. The optional receipt records FreeType version, flags, helper source hash, wall budget, glyph bounds/bearings/advances, alpha values, RGBA hashes and pixel counts. `pillow` remains the default; absence of native tooling never silently changes it.

The optional mode requires a local `cc`, `pkg-config`, FreeType headers and library. It compiles a packaged, small C helper into a temporary directory and executes against the byte snapshot. It uses public FreeType headers instead of hand-maintained ABI layouts. No package is installed or downloaded, no shell is invoked and no native font code executes inside the web/controller process. Missing native tooling returns structured `unsupported`. Malformed fonts or resource failures return structured `validation_error`.

Bounds:32MiB font input;1–4096requested scalar code points;1–512px size;16,777,216aggregate raster pixels;4096px glyph dimension;0.05–15second total native wall budget including compilation;512MiB native address space;10seconds native CPU. Temporary source/font/codepoint/executable files are removed after the call. This optional Linux subprocess adapter does not promise availability on other platforms.

A captured16px TTF and atlas supply an optional external81glyph test. Uniform no-hinting reproduces all81translation-normalized shapes and81advances; the existing default has the known i/j shape difference. Translation-normalized matching does not establish absolute baseline placement, typography, other sizes, private font generation or readability. No glyph-specific correction table or private generation handler is introduced.


The source layer also checks equal PNG dimensions for public `/reduce-colors`. This rule is prose in the frozen request schema and is independently bound to the retained actual422 receipt `runtime/context-bw-2x2/000-response.json` SHA256 `0054ccf02bc84fbcecccc7ffaaa60c5acf8a7e4944ec74cc864f4f767ec7259d`:94x46 versus95x47 frames were rejected by the server. The same request remains valid under raw JSON Schema and fails `source-derived` rule `reduce-colors-equal-dimensions`.

Inspection validates bounded base64 syntax and PNG signature/IHDR/checksum without decompressing pixels, fetching URLs or changing input bytes. Local inspection budgets are256images,64MiB aggregate envelopes,32MiB per encoded image,8192px per side and16,777,216pixels per image. Those budgets are explicitly `local-resource` failures, not claims about vendor size limits. Non-PNG headers report structured unsupported inspection; matching headers do not establish complete PNG validity or reducer behavior.
