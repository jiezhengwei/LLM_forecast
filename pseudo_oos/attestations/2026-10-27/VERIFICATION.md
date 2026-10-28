# Verify the five retrospective timestamp proofs

## 1. Download exact bytes

Download and extract [proof_bundle.zip](proof_bundle.zip?raw=true), or download the files from a GitHub URL pinned to a full commit ID. Use GitHub's raw/download action for JSON and `.ots` files; do not copy formatted JSON from a browser and save it again. Do not reformat the manifests or change their line endings.

Each experiment folder contains `manifest.json` and its final `manifest.json.ots`. Earlier proof versions remain under `proof_history/`, with their stages and hashes recorded in [index.json](index.json). Initial and intermediate proofs can still be pending; that is expected. Use the final companion proof for verification.

## 2. Check download integrity

From the extracted `2026-10-27` folder on macOS:

```sh
shasum -a 256 -c SHA256SUMS
```

On Linux, `sha256sum -c SHA256SUMS` performs the same check. The checksum list covers all unpacked package files other than itself, the ZIP, and its separate checksum. To check the ZIP before extracting it, download its adjacent checksum and run `shasum -a 256 -c proof_bundle.zip.sha256` in the download directory.

These checks detect changed bytes relative to the downloaded checksum list. They do not independently establish a timestamp. Compare a manifest's SHA-256 to the full value on the pinned summary page and then verify its OTS proof.

## 3. Independently verify the timestamp

### Browser route

Open the official [OpenTimestamps verifier](https://opentimestamps.org/). Supply the final `manifest.json.ots` and its matching exact `manifest.json` when requested. Confirm the digest match and the Bitcoin attestation. This route uses the browser verifier's configured external Bitcoin sources; it does not turn our archived verification into a local full-node verification.

### Bitcoin Core route

With the official [OpenTimestamps client](https://github.com/opentimestamps/opentimestamps-client) installed and a Bitcoin Core node configured as its documentation describes, enter an experiment folder and run:

```sh
ots verify manifest.json.ots
```

The matching `manifest.json` must remain beside the proof. For these final proofs, the expected Bitcoin block is **973370**. Its saved block hash is:

```text
000000000000000000012a87e2ecbb303224a0de1e0b294b52246e166ee4675a
```

The block's recorded timestamp is **2026-10-27 08:07:16 UTC**. A missing node or connection failure is not successful verification. `ots info` and a digest match can inspect a proof but, by themselves, do not validate its chain anchor. No fresh `ots stamp` is needed; stamping today would create different evidence.

## 4. Inspect the recorded verification

Each `verification_public.json` contains a clearly labeled derived copy of the saved verification result: proof and manifest hashes, library versions, the block header, Merkle/PoW results, and responses observed from Blockstream and Mempool. Its wrapper identifies the original receipt by SHA-256 and names the removed local path fields. The receipt is an audit record, not a replacement for independently verifying the `.ots` file.

The saved method relies on **two public Bitcoin data sources for canonical-chain membership**. Header hashing and proof-of-work checks alone do not establish membership in the canonical chain. The saved eight-confirmation count describes the observation at verification time, not a live count.

## 5. Understand the scope

The five manifests cryptographically commit to per-file hashes. With the underlying local snapshot available, hash each `files` entry at its `snapshot_path`, check its size against `bytes`, and compare the digest to `sha256`; do the same for each `artifacts` entry at its `path`. Those underlying files are not distributed in this minimal package.

The evidence is **retrospective preservation**, not historical execution-time certification or preregistration. It does not show that a model lacked knowledge of a result, that its forecasts preceded the sporting event, or that the reported results are correct. The timestamps cover the exact five original manifests, not this later README, publication index, derived receipts, or ZIP.

For stable citations, use a [GitHub permalink containing the commit ID](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files).
