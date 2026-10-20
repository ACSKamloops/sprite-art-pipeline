# Independent effect clocks

Body pose doesn't necessarily determine weapon color, projectile position, shadow, status flash or spell lifetime. Preserve separate state, clocks, coordinate spaces and termination. Declare whether an effect follows actor, hand, target or world space.

assets/weapon_palette_cycle.gd is a source-specific configurable example, tested against Mana native observations. It isn't a general shader/full renderer. Initialize configure(initial_state, entries, initial_buffer, fps). State fields: flags/start/end/phase/timer. Entries have decimal phase keys and five BGR555 words; the buffer is independent of the phase register.

Use video_tick(event) or advance_wall_clock(delta, events), choosing one clock owner. The latter retains fractions and returns every intermediate tick. palette_buffer and displayed_colors differ by the observed one-video-tick presentation delay. Explicit script resets are supplied events, not independently predicted action semantics.

The original helper tests Sword range24..25, held geometry, staged timer20hex and ping-pong range24..27.400 native ticks match buffers/display;314 enabled transitions are predicted and86 disabled records use native reset events.1600 fractional calls match these same observations. It deliberately rejects flag20hex rotation.

Use assets/weapon_palette_cycle_v2.gd for the expanded contract. It additionally implements native flag20hex palette-buffer rotation, including15-color and2..8 subranges and the staged timer.300 new state/buffer/presented-CGRAM comparisons and fractional-clock variants pass alongside the original400ticks and190 invalid-input checks. The five-color lookup bank remains separate from the rotation buffer; rotation endpoints must be ascending and within that buffer. Original helper behavior is preserved rather than silently changed. Other source games/families/modes still need their own evidence.

Rendering needs separate layers or indexed palette textures/shaders. Recoloring fused body+weapon art by RGB can alter coincident body colors. The timer helper makes no composite-pixel/shader claim. Compare body/weapon geometry, source tiles and palettes independently. A capture renderer can directly use each video's presented palette without running a simulated clock; that proves playback of captured colors, while simulation equivalence is a separate test.

Native indexed OBJ playback was tested on ten capture routes/2,827videoframes with zero differences against an independent OAM/VRAM/CGRAM reconstruction. The routes include projectiles and spells with real caster slots. Hardware backgrounds/color math/scanline limits are excluded. Object priority and transparency are preserved; semantic ownership is kept unknown when the source does not prove it. Test the shader on actual rendered pixels, not only shader parameters.

Maintain a strict route schema: positive finite clock/holds, valid local texture paths and rectangles, bounded object counts, source hashes, actor slots, total-tick agreement and unchanged state on invalid loads/commands. Step/pause/replay/end and large-delta budgets need tests. Capturing a final sample for one extra tick is an export convention, not evidence of intrinsic lifetime.

`assets/indexed_sprite.gdshader` is the exact tested indexed-palette shader. Input texture red channels store integer indices 0..15 divided by 255, with nearest sampling; palette texture is 16 columns × 8 rows of RGBA colors. Index 0 and transparent encoded texels are transparent. `palette_row` chooses a bank. These dimensions are an explicit example contract, not an inferred format for arbitrary art; adapt and revalidate if your source uses another format. Keep palettes independent of geometry and assert their texture dimensions in the loader.
