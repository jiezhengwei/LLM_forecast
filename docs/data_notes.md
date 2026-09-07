# Data notes

## Unit of observation

An archive file is a forecast **batch**, not a match. A JSON can contain multiple matches and model responses. Tennis batches can contain multiple events, with separate response records for the same model. File counts, model-response-record counts, and unique model-label counts must not be interpreted as match counts or as balanced-panel sample sizes.

The original schema varies over time. Files contain `meta_info` and `model_predictions`. Prompts, retrieved context, errors, retries, probabilities, and model identifiers are retained as originally recorded. No missing forecast is filled in during import.

## Folder classification

Public paths follow `forecasts/<sport>/<competition>/<season-or-year>/<original-filename>`.

- Sports are `basketball`, `football`, and `tennis`.
- Each league or tournament has its own folder with a stable lowercase name.
- Legacy NBA and European club-football records are assigned to `2025-26`; source `2026_27` folders map to `2026-27`. The importer checks that the target date falls within the assigned July-to-June season window. New seasonal source folders must be explicit, so later files are not silently added to a legacy season.
- World Cup, Wimbledon, and US Open records use their tournament year, `2026`.
- The last folder is the season or tournament year. Forecast dates remain in the original filenames and index.
- The JSON filename and its companion `.json.ots` filename are unchanged. `source_relative_path` records the path under the original production folder, allowing every public file to be traced back to its source.

See the [forecast catalog](forecast_catalog.md) for season/year links and counts. Source folders are not reorganized by the archive importer.

## Dates

For names such as `nba_pred_on_2026-06-02_for_2026-06-03_persona-pro.json`, the index copies the forecast and target dates from the filename. The intended sports-pipeline date convention is U.S. Eastern Time (`America/New_York`, including daylight saving time). A date in a filename is descriptive metadata, not an independent timestamp.

`generated_at_raw` preserves the top-level recorded value without timezone conversion. Some historical timestamps lack an explicit offset; do not silently reinterpret these as UTC. Missing generation timestamps remain blank.

`first_imported_at_utc` records when a file was first copied into this archive. It does not describe the original forecast time or first public availability elsewhere.

## Model identity

`model_name` is a recorded display label. Where present, `api_model` records the requested API model identifier. Labels and actual API identifiers are not always equivalent; provider routing and fallback behavior also matter. The archive preserves both without relabeling historical data.

Project records document a historical Gemini label mismatch: in early club-football files, the label `Gemini 3.0` could refer to calls made to `gemini-2.0-flash`; the documented correction date is 2026-04-23. This differs from the contemporary NBA pipeline. Later fallback behavior is reflected in `api_model` where available. Consequently, historical labels alone should not be used to assign model capabilities. This note summarizes project provenance records, not an independent reconstruction of all historical API calls.

Model panels also change over time. In particular, the US Open and the 2026-27 club-football panels introduce successor Kimi series in late August / early September 2026. New series should not be spliced into retired series without an explicit evaluation rule.

## Archive scope versus analysis scope

The archive retains completed production batches, including imperfect or incomplete model responses. The published analysis may restrict dates, select among repeated runs, exclude deprecated models, join outcomes, or require common model coverage. Those choices belong in a separate replication package.

- F1 and policy predictions are excluded from the public archive and future imports. Their original production files remain in the source folder.
- The four World Cup `pilot_smoke*` directories are test runs and are excluded.
- `.ots.bak`, temporary files, and operating-system metadata are excluded. Existing JSON and `.ots` source files are not modified or deleted.
- Probability parsing, duplicate-event handling, match identity, and pre-event timing have not been re-evaluated by the archive import.

## Index fields

`metadata/forecast_index.csv` has one row per original JSON:

| Field | Meaning |
| --- | --- |
| `sport`, `competition`, `competition_label` | Public sport, competition folder name, and readable competition name |
| `season_or_year` | Explicit season or tournament year used in the public folder structure |
| `source_collection`, `source_relative_path` | Original collection name and relative JSON path under the production forecast folder |
| `json_path`, `ots_path` | Repository-relative paths |
| `forecast_date_from_filename`, `target_date`, `target_date_source` | Descriptive dates and their source; blanks mean unavailable |
| `generated_at_raw` | Unmodified top-level generation timestamp, if present |
| `model_record_count`, `model_label_count` | Response records and distinct recorded model labels, not event counts |
| `json_bytes`, `ots_bytes` | Exact file lengths |
| `json_sha256`, `ots_sha256` | Checksums of the original bytes |
| `ots_digest_matches_json` | Whether the parsed proof's committed SHA-256 equals the JSON checksum |
| `ots_attestation_state` | `bitcoin_attestation_present_unverified`, `pending_only`, or `other_unverified` |
| `bitcoin_block_heights` | Heights named in existing proofs, not independently verified block inclusion |
| `first_imported_at_utc` | First import into this archive |
| `x_post_url` | Exact supporting post if documented; blank means not yet indexed, not necessarily absent |

The `SHA256SUMS` file covers both the JSONs and their OTS companions. The verification script also checks that no archive files are omitted from the index or checksum list.
