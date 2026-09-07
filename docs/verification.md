# Verify an archived forecast

There are three different checks. Passing one does not automatically establish the others.

## 1. Check downloaded bytes

After downloading and extracting the repository, run from its root:

```sh
python3 scripts/verify_archive.py
```

This requires only the Python standard library. It recomputes every JSON and OTS checksum and checks the archive inventory against the index and `SHA256SUMS`. This establishes consistency with this repository snapshot, not a historical timestamp.

## 2. Check that the proof commits to this file

Install the official OpenTimestamps client in a virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_archive.py --ots
```

The additional check fully parses the existing proofs and compares their committed SHA-256 digests with the JSONs. It reports whether saved Bitcoin or pending attestations are present. It does **not** contact a calendar server or validate a Bitcoin block against the chain.

## 3. Verify the external timestamp and pre-event timing

Use the [OpenTimestamps verifier](https://opentimestamps.org/): select a `.json.ots` proof and then its original JSON. Follow the verifier's result and compare the verified time with the start time of the relevant event. Preserve timezone offsets when making that comparison.

For command-line verification with the official client:

```sh
ots verify "forecasts/basketball/nba/2025-26/nba_pred_on_2026-06-02_for_2026-06-03_persona-pro.json.ots"
```

Verification may require network access and a configured Bitcoin data source. A pending-only proof is incomplete evidence in its saved form. It may need upgrading from its original calendar servers. Work on a copy of the JSON/OTS pair outside the archive before running `ots upgrade`; keep the archived originals intact. Upgrading a proof retrieves additional evidence, whereas creating a new stamp today would not recover the original timestamp.

As a complementary check, calculate the JSON's SHA-256 and match it with the exact hash in the corresponding post on the [project X account](https://x.com/ForecastLl70035). Verify the post's time and compare it with the event start time. Exact per-file X links are not yet systematically indexed in this first import.

## Limits of the import checks

The import validates bytes, JSON syntax, proof parsing, and proof-to-file digest consistency. It does not establish that every record preceded its event, independently validate the blockchain, confirm every X post, or determine the paper's final sample. A proof containing a Bitcoin attestation is explicitly labeled **unverified** until that external check is performed.

GitHub's upload and commit timestamps are not used as the original forecast evidence. See [GitHub's commit metadata documentation](https://docs.github.com/en/rest/git/commits).
