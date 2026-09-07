# LLM Forecast Archive

Original forecast records and timestamp evidence for **Evaluating LLM Forecasts on Future Sport Events**, by Jia Li, Andrew Patton, and Jiezheng Wei.

This repository makes the recorded prompts, model responses, and OpenTimestamps proof files available for inspection. It is a growing archive of forecast batches; it is **not the final estimation sample or a complete replication package**.

## Start here

- [Browse by sport, competition, and season or year](docs/forecast_catalog.md)
- [Download the file index](metadata/forecast_index.csv) (dates, model-label counts, SHA-256 hashes, and proof status)
- [See archive coverage and validation status](docs/archive_snapshot.md)
- [Verify a forecast file](docs/verification.md)
- [Understand fields, historical model labels, and sample scope](docs/data_notes.md)
- [Download this repository as a ZIP](https://github.com/jiezhengwei/LLM_forecast/archive/refs/heads/main.zip)

## What is included

Each forecast batch consists of an original `.json` file and its companion `.json.ots` proof. The public archive organizes them by **sport → competition → season or tournament year**. Files sit directly in the season or year folder. Filenames and file contents remain unchanged, and each proof stays beside its JSON.

The archive includes NBA, six European club-football competitions, the World Cup, Wimbledon, and the US Open. F1, policy predictions, World Cup pilot runs, temporary files, and timestamp backup files are excluded.

| Sport | Competitions |
| --- | --- |
| [Basketball](forecasts/basketball/) | [NBA](forecasts/basketball/nba/) |
| [Football](forecasts/football/) | [Premier League](forecasts/football/premier-league/), [La Liga](forecasts/football/la-liga/), [Bundesliga](forecasts/football/bundesliga/), [Serie A](forecasts/football/serie-a/), [Ligue 1](forecasts/football/ligue-1/), [Champions League](forecasts/football/champions-league/), [World Cup](forecasts/football/world-cup/) |
| [Tennis](forecasts/tennis/) | [Wimbledon](forecasts/tennis/wimbledon/), [US Open](forecasts/tennis/us-open/) |

```text
forecasts/
  basketball/nba/2025-26/                JSON + OTS pairs
  football/premier-league/2025-26/       JSON + OTS pairs
  football/premier-league/2026-27/       JSON + OTS pairs
  football/world-cup/2026/              JSON + OTS pairs
  tennis/wimbledon/2026/                JSON + OTS pairs
  tennis/us-open/2026/                  JSON + OTS pairs
metadata/forecast_index.csv   One row per forecast batch
metadata/SHA256SUMS           Checksums of every archived JSON and OTS file
docs/                        Coverage, data notes, and verification instructions
scripts/                     Local import and integrity checks
```

The tree above shows examples. The [catalog](docs/forecast_catalog.md) lists every included competition and season or year with file counts. Seasons are explicit, including `2025-26` for legacy NBA and European club-football records and `2026-27` for the new club-football records. Forecast and target dates remain in the original filenames and file index. The index also records the original source-relative path for traceability.

## Timing and integrity

The research workflow records forecast-file SHA-256 hashes through the [project X account](https://x.com/ForecastLl70035) and creates [OpenTimestamps](https://opentimestamps.org/) proofs. The [Google Drive archive](https://drive.google.com/drive/folders/1APOSgHyfWBig4ScDf2i7RhE2BiGfrtZA) is an additional access point.

**A GitHub upload date is not the original forecast time.** Historical files are being imported with their existing evidence. The index distinguishes dates in the source filename from the time the file was first imported here. Git commit dates alone do not establish that a forecast preceded an event.

The import checks that every OTS proof is parseable and commits to the exact SHA-256 digest of its JSON file. Some saved proofs contain Bitcoin attestations; others contain only pending calendar attestations. Neither state is reported here as independently verified against the Bitcoin chain. Establishing a pre-event forecast requires verification of the external timestamp and comparison with the relevant event start time. See the [verification guide](docs/verification.md).

## Updating the archive

The [maintainer guide](docs/maintenance.md) describes how to import additional completed forecast batches. Imports refuse to overwrite an existing JSON or OTS file with different bytes. Corrections and model-label interpretations belong in separate documentation or derived data.

## Reuse

Please acknowledge the authors and cite the repository URL together with the commit used. A formal paper citation and reuse license will be added when finalized. Third-party material embedded in retrieved context remains subject to its original terms.
