# Provider and model boundaries

| Lane | Actual role | Current execution policy |
| --- | --- | --- |
| Built-in OpenAI ImageGen | Identity/key art, directional banks, semantic repair paint | Preferred current generative-art route |
| Historical Hermes/MiniMax “H3” | Native video generation followed by explicit offline frame extraction/editing | Retained methods/results only; no new H3 calls authorized now |
| PixelLab | Observed/recovered client workflows, public contracts, retained comparisons | No assertion of recovered private generators or weights |
| PixelEngine | Observed client/API behavior, exposed pixel processing and generated comparison references | Research and saved comparisons; no assertion of recovered private models or hidden server algorithms |
| Deterministic local tools | Parts, raster sampling, editing, exact timing, codecs, Godot tests | Available; these are not local generative models |
| Local generative model | Earlier discarded alternative | Excluded from current production requirements |

The user's term “imagen” refers to the built-in image tool used in these runs;
do not rename its outputs as a test of Google's Imagen model. Agent/orchestrator
names, executor labels, transport aliases and actual image/video-model identity
are distinct. Preserve observed metadata and unknowns instead of guessing.

Model Lab prepares instructions/ordered references and imports external results.
It does not launch built-in Codex image generation by itself. Motion generation
is a separate explicitly enabled workbench route. Setup, CI and repository tests
must not enable it or submit paid jobs.

Credentials stay in the user's existing external credential mechanism. No key,
account cookie, signed browser session or personalized extension is included.
This repository needs no model credential to replay bundled offline examples,
edit supplied art, run the local UI or play the Godot demo.

