# Explicit unknown greave-surface material comparator

Unapproved paired comparator to `captain-greave-mass-calibration-v1/artifacts/calibrated-long110`. That earlier pack restored shaft bulk but visibly created a large flat black sidewall, especially far frame0, because nearest-source extrusion propagated outline pixels into newly exposed geometry. It remains unchanged and is not accepted art.

This package preserves every local vertex, triangle, UV, ring profile, bone, pose, camera and clock. Only shin texture coordinates outside the source-owned shaft alpha mask change. Inside that mask the original RGBA is exact, including observed outlines and motifs. Outside it, a once-selected source-interior armor red replaces nearest-edge extrusion. Selection uses owned opaque pixels with R65..180/G<55/B<55/R>2G and chooses the actual palette entry closest to their median RGB. The resulting new per-leg extended-UV PNG is the authoritative authored unknown-surface material master. It is not recovered unseen armor paint. A first uniform-red control also looked like a flat side panel, so the preferred comparator uses three source-palette reds and a fixed local-shell side shade. Triangle local centroid radial direction determines the level against local light [1,-.35,0]; this is authored material shading, not recovered physical illumination. Source-owned UV remains untouched even on these triangles. No convincing rear ornament or dynamic physical relighting is claimed.

There is no per-frame recoloring, silhouette fitting or camera-dependent material remapping. Boot/cap textures and all original unrelated layers retain their previous implementation. Geometry and palette checks cannot demonstrate finished appearance.

```sh
python pilot/captain-greave-hidden-material-v1/build.py --poses pilot/captain-greave-hidden-material-v1/source/poses-long-110.json --output /new/pack
python pilot/captain-greave-hidden-material-v1/check.py
```

Python/NumPy/SciPy/Pillow required. Archived sources and packet are copied locally; another worktree is never written. The check script targets committed `artifacts/shaded-long110`. Full256RGBA integration layers keep the prior naming and shin owns its cap. Use the same thigh underlap; do not duplicate legacy knee imagery. All eight native/2x keys are a visual diagnostic, not a scored approval or gameplay-contact proof.

I personally viewed all eight fullbody keys at2x. The large black wall is removed, and the palette/material is less disruptive. The new side remains restrained, somewhat flat red; it does not reconstruct unseen armor craft. Explicit source/authored-material masters and material-definition.json record the new texture ownership and shade palette. Original baseline bytes are unchanged.

Paired checks confirm exact local vertices/UV/triangles, identical pose packet,1152 unrelated layer PNGs byte-exact, source-owned UV paint exact, unchanged fullframe alpha and no changed composite pixels outside the shaft-owner silhouette. A fresh504PNG repeat build is exact. Actual72-frame joints remain gap0, all lower colors belong to the original palette, alpha is0/255 and no canvas edge is clipped. These are localization/construction checks, not artistic approval.
