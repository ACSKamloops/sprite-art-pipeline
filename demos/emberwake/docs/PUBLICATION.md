# Public test build

Play: https://emberwake-hollow-bell.astraithious.chatgpt.site

Public access requires no account. Use a desktop keyboard/mouse and **Choose emberkeeper** for Rowan, Lyra or Brann. Saves belong to the visitor's browser. Hosting runs independently of the local WSL preview servers.

Sites version 1 is deployed successfully. The deployment-only source checkout is `/home/astra/projects/emberwake-public-site`, pushed commit `797c3f1c35263c68269c69fb101998868cc055ad`. Its `.openai/hosting.json` retains the exact Site identity. Reuse that project and the Sites source/publishing helper for updates; do not create another Site for this URL.

The game content PCK is byte-identical to the tested local build: `382a06f7aa84d9532b5a4c1f3c901a004128161afabe30cb71a82ac97b8ed2ce`. The 39.5 MB raw engine is transported as a 10.1 MB gzip asset, decoded through a small same-origin streaming loader. Browser hashing verifies the reconstructed engine, generated engine JavaScript, PCK and compressed asset match their local authorities exactly. The game rules, artwork and canonical local export remain unchanged. This accommodates the host's [individual asset limit](https://developers.cloudflare.com/workers/platform/limits/).

The local archive contains nine files. Its physical gzip/raw-tar hashes and the native storage content hash are retained as distinct identifiers; they differ, so container identity is not asserted. The actual public game payload hashes match their local authorities. Only the static game distribution is published; research/editing work remains in the canonical project.

The actual public URL passed 21 ordinary-input assertions plus 8 cast samples in a fresh browser without credentials, authentication headers or login. Selection/new journeys, both new heroes' four facings/strikes/spells, visible frost, dodge, safe swaps and save/title/reload/Continue passed with `test_mode=false`. Public screenshots were viewed. Browser console has no game error. This is a focused release check, not another full-ending or human motion-quality review.

An anonymous Python `urllib` probe received 403 for static paths from this environment. That failed transport is preserved separately; it was not converted into a successful HTTP check. The fresh anonymous Chromium browser and its same-origin asset hash requests succeeded. Its only cookies were a generated Site visitor cookie and Cloudflare browser/bot cookies, with no account sign-in.

Exact Site/version/deployment IDs and native terminal success are in `evidence/public-site/publication.json`. The folder also contains `package-verification.json`, `browser-live.json`, `browser-asset-hashes.json`, the retained HTTP failure and selected live screenshots. No repository credential is stored in those files.
