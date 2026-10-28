# Five pseudo-OOS experiments: retrospective timestamp evidence

**Retrospective preservation dated 27 October 2026.** Five completed sports-forecasting experiments have existing OpenTimestamps proofs anchored in Bitcoin block **973370**, whose recorded block time is **2026-10-27 08:07:16 UTC** (16:07:16 in Asia/Singapore).

These proofs attest to the committed manifests' existence by their Bitcoin timestamp. **They do not establish historical execution dates, preregistration, pre-event forecasting, or model knowledge cutoffs.** A block timestamp is not an exact wall-clock model-generation time.

This is a separate evidence collection for retrospective experiments. It does not change the interpretation of the original forecast archive under `forecasts/`.

## Download and verify

- [Download the complete proof bundle](proof_bundle.zip?raw=true)
- [Verification instructions](VERIFICATION.md)
- [Machine-readable index](index.json)
- [Checksums of the unpacked package](SHA256SUMS)
- [Checksum of the ZIP download](proof_bundle.zip.sha256)

The package contains the five exact original manifests, all 15 saved proof versions (initial, intermediate pending upgrade, and verified upgrade for each experiment), five derived public verification receipts, and publication documentation. Each final verified proof is also copied beside its manifest as `manifest.json.ots` for convenient verification. No proof was newly stamped for this publication.

## Experiments

Recorded execution dates below come from archived local records, use **Asia/Singapore**, and are **not independently certified by these timestamps**. Game counts distinguish predicted from scored fixtures; the two NBA experiments cover the same 354 games, and the football samples overlap, so these counts should not be summed as unique events.

| Sample | Model | Recorded execution date | Completed requests | Games: predicted / scored | Evidence |
| --- | --- | --- | ---: | ---: | --- |
| World Cup | GPT-6.1 Sol | 2026-10-15 | 34 | 104 / 104 | [Manifest](worldcup_2026_gpt61sol_v1/manifest.json) · [OTS](worldcup_2026_gpt61sol_v1/manifest.json.ots) · [Receipt](worldcup_2026_gpt61sol_v1/verification_public.json) |
| NBA | GPT-5.2 | 2026-10-16 | 74 | 354 / 354 | [Manifest](nba_2026_gpt52_v1/manifest.json) · [OTS](nba_2026_gpt52_v1/manifest.json.ots) · [Receipt](nba_2026_gpt52_v1/verification_public.json) |
| European football | GPT-5.2 | 2026-10-16 | 246 | 721 / 719 | [Manifest](football_2026_gpt52_v1/manifest.json) · [OTS](football_2026_gpt52_v1/manifest.json.ots) · [Receipt](football_2026_gpt52_v1/verification_public.json) |
| European football | GPT-6 Luna | 2026-10-16 | 141 | 420 / 419 | [Manifest](football_2026_gpt6luna_precutoff_v1/manifest.json) · [OTS](football_2026_gpt6luna_precutoff_v1/manifest.json.ots) · [Receipt](football_2026_gpt6luna_precutoff_v1/verification_public.json) |
| NBA | GPT-5.2 Pro (Batch) | 2026-10-27 | 74 | 354 / 354 | [Manifest](nba_2026_gpt52pro_batch_v1/manifest.json) · [OTS](nba_2026_gpt52pro_batch_v1/manifest.json.ots) · [Receipt](nba_2026_gpt52pro_batch_v1/verification_public.json) |

The European-football GPT-6 Luna subset uses target dates strictly before 18 May 2026. World Cup counts cover 104 primary match targets; additional advancement targets from the same responses are not counted as extra matches. The World Cup archive also records an interrupted attempt of unknown cost; the completed-request count does not erase that attempt.

## How the evidence connects

Each original `manifest.json` lists file paths, byte sizes, and SHA-256 hashes for a frozen local experiment snapshot. Its `.ots` proof commits to the SHA-256 of that **exact manifest file**. This binds the listed file commitments without joining all data into one large text file.

This minimal public package does **not** include the underlying prompts, responses, results, code copies, or expense records listed inside the manifests. Readers can verify the manifests' timestamps now. Recomputing the hashes of the underlying files requires access to those files. A timestamp does not itself establish that the reported forecasts or results are correct.

The local archive retains 1,473 snapshot file copies and 10 additional snapshot artifacts across the five experiments, including repeated shared files. Those local copies were checked against the manifests before publication.

## Verification already recorded

All five final proofs were verified on 27 October 2026, between 09:23 and 09:24 UTC. The recorded method checked the OpenTimestamps proof operations and Merkle path, the Bitcoin block header hash and proof of work, and matching canonical-chain observations from **Blockstream and Mempool**. The saved observations reported eight confirmations at that time.

**This verification relies on two public Bitcoin data sources; it is not local full-node verification.** A reader can independently verify using their own Bitcoin Core node or the official OpenTimestamps browser verifier. The [guide](VERIFICATION.md) explains these different trust bases.

Public `verification_public.json` files are explicitly marked **derived public receipts**. They retain the original verification facts while omitting local bookkeeping paths, identify every omitted field, and include the SHA-256 of the untouched original receipt. The original receipts remain in the local archive. These public receipts, this README, the index, and the ZIP were prepared for publication later; they are **not** covered by the earlier five manifest timestamps.

## Exact manifest SHA-256 values

- `worldcup_2026_gpt61sol_v1`

  `7e9ea7ac3c53a7c627f1640ea77511a32c0956b6e5c1839bd02dc0876fde66a5`

- `nba_2026_gpt52_v1`

  `6359155cb1daca8cf1128b1364f11f55b48cde57cbdfc429b746aadb942c94ad`

- `football_2026_gpt52_v1`

  `92ffa53732bacca10ff785e9d1866e31a79f2d26a6b1dd6c89097997c84c0741`

- `football_2026_gpt6luna_precutoff_v1`

  `31300836f7424fcaee8a0c66bbfcec93cba2419a15d2c3760fcb7c35b5e5e859`

- `nba_2026_gpt52pro_batch_v1`

  `b8ece22f7ad40b1e5beac8bdd52441854f91be9b061a947f69d34c8a77938470`

## Citation and interpretation

Cite this page using a GitHub URL containing the full commit ID, and identify the relevant experiment and manifest SHA-256. The GitHub publication time and any X announcement time are separate from the Bitcoin timestamp and the recorded execution dates.

The proofs establish retrospective preservation (补存证), not historical preregistration. This evidence collection is not a complete replication package.
