# Asterid Allies — complete source transfer / existing public photo learner (2026-10-30)

## Verified original source — PASS

Checked `migration/original-source-transfer-manifest.json` against the staging branch's full Git tree `5fd89e7cdbf98bf43ecfbe769a9d054ba3af9a2d`. Source snapshot is from original hub commit `515387cbc23b8bf8931141ead9c44c92a7793699`.

| Metric | Result |
|---|---:|
| Assigned families | 10 |
| Species | 118 |
| Original files copied / hash matching | **693 / 693** |
| Botanical, source, credit files | 387 |
| Original photo binary files | 306 |
| Missing source files | **0** |
| Wrong source hashes | **0** |

## Existing public learner

Pre-audit public main tree `42bf177a787d1be9e0efb0df9dbfd2d75cb5f136` contained **118 species JSON lesson files** and **64 original approved hosted photo assets**. The existing published gallery index reports **64 photographs across 30 species**, and the source photo migration report holds **248 of 312 photo references** for rights/origin review. No media was added or deleted in this QA pass.

[Previous successful Pages deployment](https://github.com/Crking92/Hays-Botany-Asterid-Allies/actions/runs/40910210121) establishes that a photo-backed website was deployed, but not independently verified every HTTP asset. The new `scripts/verify_existing_site.py` and `verify-existing-site-gallery.yml` verify every local JSON/photo SHA and live Pages JSON/media file; claim live end-to-end PASS **only after its workflow succeeds**.

## Completion boundary

- This is **existing source-file transfer completion** plus public learner verification, not complete diagnostic photography or final botanical peer review.
- Metadata and photo source bytes remain preserved; held photo references are not a reason to redo source migration.
- Original GitHub hub unchanged; all new family botanical writes route to family staging; legacy automations remain paused.
- All repositories and historic staging/hold branches are public, meaning held photo bytes can be accessed in Git history independently of the rights-filtered gallery; note this for separate provenance remediation, with no automatic history rewrite or deletion.
- The obsolete text-only workflow is intentionally blocked from overwriting the photo site; do not rerun/bypass it.
- Next grouped collection in existing-data QA: **Cacti & Buttercups**.
