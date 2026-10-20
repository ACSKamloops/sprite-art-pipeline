# Local walk comparison player checks

These retained runs exercise direct-PNG rational clocks, selectors, mirroring, loop wrap and MP4 decode/playback. They are browser behavior evidence, not timed human animation approval. The four-variant midpoint/timing run passes12 assertions and verifies68 fetched source image hashes.

Both failed probes are retained: the first expected an optional video in a no-MP4 build; the second expected exact Canvas2D RGBA against a separately composed canvas. The corrected no-video scenario passes8 assertions. The timing diagnostic measured a maximum1RGB GPU-versus-CPU alpha-composition difference, zero bytes beyond1; corrected timing scenario passes13 assertions. Source PNG bytes/hashes remain exact.

Each JS scenario was executed using the installed Playwright CLI run-code facility against the owned local player session. Absolute paths and localhost URLs in these point-in-time scenarios describe the actual run, not a universal test runner. The reviewed PNG packet remains authoritative for sourceRGBA.
