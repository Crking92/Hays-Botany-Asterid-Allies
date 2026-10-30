# Hays Botany — Asterid Allies

**Existing-source migration: COMPLETE. Public family learner: ACTIVE (existing rights-filtered photos). Botanical/photo enrichment: DEFERRED.**

[Open the Asterid Allies Visual Learner](https://crking92.github.io/Hays-Botany-Asterid-Allies/site/) · [Original read-only hub](https://crking92.github.io/Hays-County-Botany/) · [Active family routing registry](https://github.com/Crking92/Hays-County-Botany/blob/main/workflow/ACTIVE_NEW_PLANT_WRITE_ROUTING_20261028.json)

This collection contains **118 original species lessons in 10 assigned families**: Apocynaceae, Boraginaceae, Campanulaceae, Convolvulaceae, Gelsemiaceae, Gentianaceae, Loganiaceae, Polemoniaceae, Rubiaceae, Solanaceae.

## Existing source preservation — October 30, 2026

- **693/693 source files** match the original transfer manifest's Git blob hashes in branch [`staging/original-source-transfer`](https://github.com/Crking92/Hays-Botany-Asterid-Allies/tree/staging/original-source-transfer).
- That includes **387 scientific/credit text files and 306 original photo files**; no original source file is missing or altered.
- The existing public `main/site` contains **118 species lessons** and **64 approved hosted photos across 30 species**. Its photo-publication report preserves **248 held source-image references** as a separate status, not missing file transfers.
- Source and website release are separate: photos can be preserved but not licensed for public display. The repo itself is PUBLIC, including its historical staging/hold files; a Pages filter does not privatize held images in Git history. Do not add new license-uncertain photo bytes or bypass source-rights checks.
- The older text-only publishing workflow deliberately rejects overwriting the photo-backed learner. Do not force it to pass or restart obsolete automation.
- Last inspected pre-audit successful Pages deployment: [run 40910210121](https://github.com/Crking92/Hays-Botany-Asterid-Allies/actions/runs/40910210121).

[Original source transfer manifest](https://github.com/Crking92/Hays-Botany-Asterid-Allies/blob/staging/original-source-transfer/migration/original-source-transfer-manifest.json) · [Public photo release report](site/photo-source-migration-report.json) · [Migration checkpoint](migration/ASTERID_ALLIES_TRANSFER_QA_20261030.md)

## Ongoing guardrails

`python3 scripts/verify_existing_site.py` checks every published lesson JSON, photo attribution, linked file and original Git blob hash. The [site verification action](.github/workflows/verify-existing-site-gallery.yml) additionally compares all published Pages JSON and images against committed bytes.

All NEW plant data and anatomy/credit changes for these families are assigned to this family's `staging/original-source-transfer` branch under the active hub routing registry. The original hub stays read-only; no new photos/taxa, production cutover, visibility changes or automation restarts are part of the migration check. Future botanical refinements do not block source-transfer completion.
