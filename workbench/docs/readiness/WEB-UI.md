# Local web controls

This is a local control surface for the registered workbench services. It does
not call PixelLab, generate art, approve artwork, or complete missing source
analysis. The server's readiness record is authoritative. Setup verification
and permission to start original-art comparisons are displayed separately.

## Layout and scope

The interface uses a dark navigation rail, a light working surface, thin
dividers and one teal accent. The primary working areas are Readiness, Flows &
grammar, Workspace, Jobs and Methods. Each view puts its operative content
first; there is no marketing page or synthetic metric dashboard.

- **Readiness:** show actual prerequisite records, blockers and source-version
  setup verification. The verification action submits diagnostics, with the
  returned job identity available in Jobs. The comparison control has no
  implementation and remains unavailable.
- **Flows & grammar:** filter retained flows, commands, grammar, transport
  sequences, comparison recipes, interfaces and requirements; inspect the
  complete selected record. Grammar includes its boundary, the nine documented
  primitives, retained claims and declared conditionals. A separate notice shows
  current versus frozen public-operation drift. A record's status does not imply closure of its
  unrecorded branches or private implementation.
- **Workspace:** import PNG/APNG or editable project JSON, or load a project,
  sequence or history already in the configured Store. A sequence is explicitly
  converted by `local.construction.from_sequence`; unsupported conversions fail
  visibly. Edit existing unlocked cels with pencil/erase, choose exact palette
  indices, add RGBA colors, adjust frame ticks, undo/redo and render an animation
  to the Store.
- **Jobs:** edit or load a plan JSON declaration, validate/save it through
  `/api/plan` without execution, then load the stored declaration and submit its
  actual plan object through `local.pipeline`. The supplied-image example can
  refer to the last PNG/APNG uploaded in this session; it imports those existing
  bytes, constructs an editable project and renders supplied frames. It does
  not generate animation. Inspect job state and issue cancel/retry. Job state is
  refreshed every five seconds only while
  this view is visible; completion of dispatch is not job completion.
- **Methods:** inspect actual bound local schemas and frozen vendor contracts.
  Only a registered, implemented local method is invocable. Request and result
  JSON remain visible; there is no automatic alternate service on failure.

The frontend uses only same-origin HTML, CSS, JavaScript, API and raster
requests. It has no external fonts, assets, JavaScript dependencies or analytics.

## Editing and playback contracts

A pixel stroke becomes one guarded `sprite-edit-transaction/v1`, using the
current document's canonical `project_hash`. It is committed to the immutable
history service. The returned project is fetched again before the editor treats
the revision as committed. Native palette aliases and shared cel references are
retained by the construction service; painting a shared cel affects all frames
that refer to it. Locked layers are rejected, and a missing cel is not silently
created or borrowed from another frame.

The browser composite preview uses the construction toolkit's integer RGBA
compositing policy. In-project animation preview follows the selected
animation's ordered frame IDs, `duration_ticks / fps`, and finite/infinite loop
setting. It does not invent animation poses. The separate stored preview uses
the backend-rendered sequence's actual raster IDs and rational durations.
Rendered artifacts remain available by identity for external inspection.

The interactive canvas is limited to 1,048,576 pixels. Larger valid projects
remain accessible to Methods and external editor exchange, but the UI displays
the limit instead of downsampling or showing an inaccurate editable surface.
Palette buttons show the first 256 entries. A numeric palette-index control
selects entries beyond that range without changing their indices or colors.

Uploads are limited to 32 MiB for PNG/APNG and 16 MiB for JSON. The frontend's
limits are convenience checks; the backend must enforce its own admission and
finite JSON limits. A project loaded from an artifact ID is never inferred from
a short display hash.

## Keyboard and responsive controls

Navigation links are normal hash links with `aria-current`. All form controls
are labelled, failures use an alert region, and action status uses a live status
region. In Workspace, **B** selects pencil, **E** selects erase, **Space** toggles
animation playback, **Ctrl/Cmd+Z** undoes, and **Ctrl/Cmd+Shift+Z** redoes. These
shortcuts do not intercept text entry. Fine pixel edits can also be specified
without a pointer in the Methods transaction JSON editor.

At narrower widths navigation becomes a horizontal rail and inspectors follow
their working areas. Reduced-motion preferences suppress decorative entrance
transitions; playback is always explicitly requested by the operator.

## Verification boundary

Run `node --check sprite_workbench/web/app.js` for syntax. This is not a browser
functional proof. Integration verification must exercise the actual HTTP
server, upload/import, a guarded stroke, undo/redo, palette addition, frame
timing, rendering, plan submission and visible errors. Inspect the UI at desktop
and narrow viewport sizes, verify there are no external requests or page errors,
and compare browser composites to stored backend rasters on asymmetric
transparent fixtures. Retain the tested source fingerprint and exact artifacts.
Browser inspection establishes the controls' behaviour, not artistic quality.
