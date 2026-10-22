# Message for the next AI

Copy the following message into your AI assistant. Give it access to a local
clone of this public repository. The links below also work without signing in.

---

Continue the sprite-art pipeline in
[ACSKamloops/sprite-art-pipeline](https://github.com/ACSKamloops/sprite-art-pipeline).
Our goal is consistent, editable game characters with useful directional
animations and a repeatable production/review process. The whole-library 9/10
quality target remains open; technical checks are not visual approval.

If the repository is not already available, clone it:

```bash
git clone https://github.com/ACSKamloops/sprite-art-pipeline.git
cd sprite-art-pipeline
```

1. Read [AGENTS.md](../AGENTS.md), [the full AI handoff](AI-HANDOFF.md),
   [requirements](REQUIREMENTS.md) and [current status](STATUS.md). Check Git
   status and preserve existing changes before editing. Follow linked research
   only as needed; do not load every historical experiment into context.
2. Use the four complete skills under [skills/](../skills/README.md):
   `reference-art-production`, `imagegen-sprite-animation`,
   `sprite-construction-editing` and `sprite-animation-pipeline`. Read the
   relevant `SKILL.md` before using its workflow. For Codex, install with:

   ```bash
   python3 scripts/install_skills.py --destination "$HOME/.codex/skills"
   ```

   The installer skips identical copies and refuses to overwrite differing
   existing skills. Other clients can read the Markdown directly or install
   the folders in their supported skill location. Keep Windows and WSL Codex
   homes separate. Skills do not install an image generator or editor.
3. Begin with [examples/current-hero](../examples/current-hero/README.md).
   Preserve its preferred southeast Hybrid walk as an immutable control.
   The snapshot has 17 states across eight directions, with 136 selected
   bindings and 561 exposures. Some states reuse art; southeast run is a
   faster-walk alias, not a separately authored run. These counts do not mean
   every animation has passed visual review.
4. Follow [setup](SETUP.md) for dependencies (`uv` is required), then verify
   the files and replay the saved source study without generating new art:

   ```bash
   bash scripts/setup.sh
   .venv/bin/python scripts/verify_selected_hero.py
   .venv/bin/python examples/current-hero/replay_recovery.py \
     --output output/my-recovery-replay
   ```

   Use fresh output names for subsequent runs. The full handoff provides the
   Godot inspector build and engine checks; Godot 4.7.2 is the tested baseline.
   For immediate browser inspection, run:

   ```bash
   python3 -m http.server 8910 --bind 127.0.0.1
   ```

   Open `http://127.0.0.1:8910/examples/current-hero/package/` on that machine.
5. For new paint, use built-in **OpenAI ImageGen** plus explicit source-part
   and pixel repairs. The user's name "imagen" refers to that tool, not Google
   Imagen. Do not enable H3/MiniMax or local generative models. If image
   generation is unavailable, report the missing capability and continue work
   that does not require it. Setup, replay and verification must not submit
   provider jobs. Never commit credentials or private browser captures.
6. Build a fresh Godot inspector before changing art. Improve one demonstrated
   defect at a time, starting from the priorities in the full handoff. Freeze
   input hashes, reference roles, camera, pivot and rational timing. Preserve
   raw generations, actual prompts, editable sources, ownership maps and pixel
   edit journals. Keep experiments separate and retain rejected trials.
7. Compare the candidate against the frozen control at native size and normal
   playback speed. Check each frame, adjacent pair, loop seam and action
   transition. Obtain independent adversarial review when authorized; separate
   agents need separate worktrees and exclusive file ownership. Request human
   normal-speed review for art acceptance. One action's acceptance does not
   approve other directions or the library.
8. Report what changed, reproduction commands, remaining visible defects and
   the next useful step. Separate file/editor/runtime evidence from visual
   judgments. Update the methods, relevant skills and status when a technique
   proves useful. Do not claim provider internals were recovered: private
   PixelLab/PixelEngine weights, hidden prompts and complete server algorithms
   remain unavailable.

The [full handoff](AI-HANDOFF.md) is the detailed continuation guide. The
[skills-only ZIP](https://github.com/ACSKamloops/sprite-art-pipeline/releases/download/handoff-2026-10-22/sprite-pipeline-skills.zip)
is available separately, but a normal clone includes the current character,
tools and examples as well as the skills.
