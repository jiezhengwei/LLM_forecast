# Maintaining the archive

## Import completed forecasts

Run these commands from the repository root after completing and accepting the source forecasts and their original audit records:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/sync_forecasts.py --source "/path/to/forecast_results"
.venv/bin/python scripts/verify_archive.py --ots
git diff --stat
git status --short
```

The importer reads the original production layout and assigns each accepted batch to `forecasts/<sport>/<competition>/<season-or-year>/<forecast-month>/`. It accepts JSONs with matching, parseable SHA-256 OTS companions, always excludes F1, policy predictions and the `pilot_smoke*` directories, and checks for common credential patterns without printing their values. It completes preflight validation before copying new files. Unexpected layouts, missing proofs, digest mismatches, and changes to existing archived bytes stop the import.

Imports are additive. Removing a local source file does not remove its archived copy. Re-running without new files leaves the index and coverage unchanged. The script does not execute a forecasting notebook, call a model, create a timestamp, or upload anything.

After reviewing the changed files:

```sh
git add README.md .gitignore .gitattributes requirements.txt docs metadata scripts forecasts
git commit -m "Add completed forecast batches"
git push origin main
```

A push requires GitHub authentication with write access to this repository. Keep credentials outside the repository.

## Preserve source evidence

Do not reformat JSONs, normalize newlines, replace failed model responses, relabel historical data, or overwrite original proofs as part of an archive update. `.gitattributes` disables newline conversion under `forecasts/`. Moving a JSON and proof together to a different folder does not change either checksum. Production source files must remain untouched.

An intentional correction needs a separately documented artifact and a link to its original record. For OTS upgrades, retain the original proof and design an explicit supplementary-proof path before adding updated evidence. Do not use force-push to rewrite this archive's history.

## Extend coverage deliberately

Add new production collection names and their public classification to `COLLECTIONS` in `scripts/archive_layout.py` only after reviewing the source layout. The legacy seasonal folders map to `2025-26`; use explicit source folders such as `2026_27` for subsequent NBA and club-football seasons. Tournament folders map to their stated year. Keep pilot runs, cached inputs, API credentials, notebook outputs, logs, paper drafts, and derived analysis separate from raw forecast records. The exclusion list prevents F1 and policy files from being imported again.

The generated `docs/forecast_catalog.md`, `docs/archive_snapshot.md`, and `metadata/forecast_index.csv` describe stored batches, not event-level research coverage. Update the paper's data-availability statement separately when its public archive link is finalized.
