# Final H3 / PixelLab controls review

Bounded review on 2026-10-14 of the four requested script sources in `/home/astra/projects/pixellab-local-workbench/scripts`. No actual credentials, provider/model/agent calls, artifact transformations or writes in that checkout were made. One fake-token counterexample ran entirely offline using a mocked opener and a temporary local directory. The response-scrubbing correction and tests were implemented only in the reviewer's isolated worktree.

## Findings and disposition

1. **Escaped credential echoes could bypass PixelLab response scrubbing. Fixed in reviewer commit `88e826a`; matching corrected bytes are now visible in the parent checkout.** The reviewed `pixellab_h3_comparison.py` replaced literal token text before JSON parsing. A JSON string or key containing the same fake token through `\uXXXX` escapes survived that replacement, then decoded to the token in the returned receipt body. HAR response text also retained a reconstructable escaped token. This was demonstrated with `FAKE_TOKEN`, not real credentials. The correction parses JSON, recursively scrubs string keys and values, and marks sanitized canonical response text with `content.text_redacted=true`. It preserves exact original text when no redaction is needed and retains the untouched response-byte SHA before scrubbing. Non-JSON literal token echoes are also scrubbed. The isolated comparison suite passed **16 offline tests**, including this counterexample, original-text preservation, paid-submit guards, final-only extraction and HAR omission.

2. **Initial verifier counted selected REA records rather than all captured HAR calls. Parent correction observed in source.** The initial `verify_h3_pixellab_comparison.py` checked equality for selected records but did not establish that a second POST or completed GET had not been omitted from that selection. The updated source at lines 80–88 rejects duplicate REA ordinals, scans the entire HAR for POST/completed-GET cardinality, and requires those entries in the REA selection. This closes the identified subset-counting gap for the retained capture. The review did not rerun the parent's artifact verification or tests.

3. **Initial verifier did not bind the full frozen contract. Parent correction observed in source.** The initial checks compared local PNG/prompt values and the PixelLab submission HAR, but omitted native case/pair hash pins, native resolution/ratio and exact request-field sets. Updated lines 51–73 verify native prepared hashes and pair pins, literal prompt hash, exact top-level control fields, native `768P`/`adaptive`, four seconds and PixelLab's declared frame/seed/background/enhancement values. This strengthens the retained local binding; it is still not independent authentication of a remote deployment or proof of a private checkpoint/conversion method.

4. **Native JSON key scrubbing was incomplete. Parent correction observed in source.** `minimax_h3_pilot.py` already scrubbed decoded string values; its initial dictionary branch left keys unchanged. Updated line 134 scrubs keys and values. No actual credential leak in the retained results was established by this review.

## Paid submission and credential limits

Both scripts check prior state and make an exclusive persistent `.submission.lock` claim before a paid POST. Neither automatically retries a paid POST. Under ordinary concurrent invocations of the same run directory, this prevents two submitters from proceeding. An ambiguous response leaves the run non-resubmittable; operators must inspect retained evidence and must not delete the marker to retry.

**`O_EXCL` is not a crash/power-loss durability or provider idempotency guarantee.** The native pilot's `write_json` uses write/replace without `fsync` (`minimax_h3_pilot.py:35–38`); its “Durable marker” comment at line 174 overstates what that implementation establishes. The PixelLab script additionally syncs its lock, state file and directory before POST (`pixellab_h3_comparison.py`, submit/write_json), but the claim remains local and filesystem-dependent. Neither script obtains a remote idempotency key, prevents another run directory from submitting the same request, or makes a charged job and its local receipt atomic. A successful POST followed by lost response/receipt can leave an orphaned remote job. Normal-process duplicate prevention must not be reported as universal exactly-once execution.

Credential sources are read in-process and are not command arguments. API destinations are fixed HTTPS origins with restricted paths; redirects are blocked. Native downloads create a fresh request without API Authorization/cookies and do not invoke the credential resolver (`minimax_h3_pilot.py:218–246`). Signed output URLs remain in private task-response evidence by design; they are not proof that the API credential was forwarded to the CDN. This source review establishes intended request construction, not an independent packet capture or a scan of real credential contents.

## Matched inputs and proof boundaries

PixelLab preparation verifies the native case's source/request hash pins and the actual data-URI PNG bytes, then copies the identical PNG and literal motion text. It records the new generic RPG subject separately from the historical PixelLab method-reference case. PixelLab's 16 requested generated frames, seed 123 and alpha/background contract remain distinct from native H3's four seconds and 768P video. No absent native seed, sprite count, alpha guarantee or private caption processing is invented.

Extraction admits only final completed `last_response.images`, retains every returned slot in order, preserves duplicate frames, and reports slot-zero byte and decoded identity as observed facts. Slot zero is shown separately; nominal two-second PNG playback is a local inspection clock. Native video review retains all decoded frames and PTS and explicitly labels eight-frame selection, whole-canvas nearest resizing and 125-ms GIF holds as local derivatives (`review_h3_video.py:39–62` and its manifest). If the final frame lacks a duration, the last observed PTS delta is a declared local fallback, not recovered provider timing.

The offline verifier binds local files, producer HAR/REA records, ordered PNG bytes and native media hashes. REA parsing is not independent remote authentication. Native frame hashes bind retained decoded PNGs; this verifier does not independently re-decode the video or reconstruct the private PixelLab video-to-sprite process. Its negative artistic/private-conversion flags are appropriate. No temporal/aesthetic acceptance or causal model ranking follows from these checks.

## Reviewed source identities

Hashes below identify the source snapshot read after the parent's verifier/native scrubbing corrections became visible. These files were still being prepared in the parent checkout; subsequent changes require their own review.

| Script | SHA-256 |
| --- | --- |
| `minimax_h3_pilot.py` | `fc1c152f4a9cbd8ed3a0d92adb83625acac8513fb668777ff4dd7362acc79bfe` |
| `review_h3_video.py` | `3cabf21149f988932f9d047ba5de01bf184e826d6bd2379d6bec2ee73ff49c30` |
| `verify_h3_pixellab_comparison.py` | `e26cdef5d679c1472a3d3ce0c9516d8eaeb22c97230642ecbb2d6b12183c90ba` |
| PixelLab comparison before reviewer fix (`ec1282a`) | `184c67d0172d63121bed8c64c3460a45f4d8d1928d4125260b8678e4ec2300cf` |
| PixelLab comparison after reviewer fix (`88e826a`) | `58de1fe2b232d376f3f1b951966a0bc3e82bef48513c8f278b4a0a3e9f9fe7e8` |

The separately committed correction `88e826a` supersedes the initial PixelLab script for future calls; its corrected bytes were observed in the parent checkout during the final read. No replay or new paid request is needed to apply this local response-retention fix.
