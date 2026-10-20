# Reference inputs and art brief

Use the minimum references that resolve the task, rather than collecting a large unrelated image folder.

| Task | Useful input | What to establish |
|---|---|---|
| Faithful portrait, object or sprite | Clear identity photo; full subject when silhouette matters | Actual variant, geometry, proportions, appendages, visible accessories, palette |
| Consistent series | An approved style image plus each subject's identity input | Medium, detail density, edge treatment, lighting, view, contrast and framing |
| New original art | Specific written brief; optional mood/style images | Intended use, subject, style, composition, constraints and areas open to invention |
| New pose | Identity plus pose/sketch reference where useful | Body orientation, contact points, occlusion and accessories; unseen surfaces remain authored |
| Animation | Identity/style plus action specification and preferably pose sequence or suitable rig | Directions, frame count/timing, pivot, gait, firing origin and loop continuity |
| Texture/material | Surface photos or material brief and destination UV/tile requirements | Scale, orientation, seams, channels, colour-space expectations; generated shading is not a validated PBR map |
| Exact lettering or product detail | Legible close-up or user-provided text | Verbatim spelling, typography/layout and critical details |
| Editing existing art | Existing image or editable document | Exact target and invariants; which other inputs are only references |

Record each reference's role and any conflict. Identity photos govern the subject; style references govern rendering. A pose reference must not accidentally replace the subject or its equipment. Multiple identity photos may show different variants: choose the intended build rather than combining them silently.

For archives/catalogues, decode and inspect the supplied files. Check for duplicate hashes, generic faction/category art, placeholders, incorrect labels, tiny thumbnails and mismatched variants. Keep source IDs even when multiple entries share one image. Deduplication is a candidate for review, not an automatic decision to share the final asset.

For supplemental downloads, retain page URL, image URL, credit, date if available, original bytes and SHA-256. Prefer an authoritative depiction for identity questions. Check whether an image is a photograph, a drawing, an older variant, a conversion or a proxy. A source title alone does not establish correctness. Use browsing when researching external references or verifying unfamiliar details, and cite those sources in the delivered notes.

For full-body work, inspect hands/feet, wing tips, wheels/tracks, tails, antennae and weapon ends. If a source crops them, find a full-subject photo before inventing important geometry. If only reconstruction is possible, state what is authored and preserve what the source does establish. User corrections supersede uncertain visual guesses: transcribe exact text rather than confidently interpreting an illegible banner.

Keep the brief compact. A practical record is:

```text
Use: [game portrait / illustration / texture / UI asset / other]
Subjects and IDs: [...]
Identity input: [path or original-design brief]
Style input: [approved image or explicit style description]
Pose/view: [...]
Must retain: [silhouette, equipment, colours, exact text, ...]
Open to design: [...]
Export: [canvas, background/alpha, scale variants, native format]
Delivery: [local folder or other requested destination]
```

Do not require a 3D model for a 2D-generation route. If choosing Blender rendering, explain the actual need for geometry, materials, lighting and a camera, plus a rig for articulated animation. A source photograph and a generated portrait do not become reusable 3D geometry merely through conversion.
