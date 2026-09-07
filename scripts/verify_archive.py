#!/usr/bin/env python3
"""Check archive inventory and bytes; optionally parse OTS proofs, offline."""

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath

from archive_layout import classify

ROOT = Path(__file__).resolve().parents[1]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def archive_path(root, relative):
    path = PurePosixPath(relative)
    if not path.parts or path.is_absolute() or '..' in path.parts or path.parts[0] != 'forecasts':
        raise ValueError(f'Unsafe archive path: {relative}')
    target = root.joinpath(*path.parts)
    if any(p.is_symlink() for p in [target, *target.parents]):
        raise ValueError(f'Symlink is not permitted: {relative}')
    if not target.is_file():
        raise ValueError(f'Missing file: {relative}')
    return target


def proof_info(data, json_hash):
    try:
        from opentimestamps.core.timestamp import DetachedTimestampFile
        from opentimestamps.core.serialize import StreamDeserializationContext
        from opentimestamps.core.op import OpSHA256
        from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
    except ImportError as exc:
        raise ValueError('Install requirements.txt to parse OTS proofs.') from exc
    proof = DetachedTimestampFile.deserialize(StreamDeserializationContext(io.BytesIO(data)))
    if not isinstance(proof.file_hash_op, OpSHA256):
        raise ValueError('Expected a SHA-256 OTS proof.')
    if proof.file_digest.hex() != json_hash:
        raise ValueError('OTS committed digest does not match JSON.')
    attestations = [a for _, a in proof.timestamp.all_attestations()]
    heights = sorted({a.height for a in attestations if isinstance(a, BitcoinBlockHeaderAttestation)})
    if heights:
        state = 'bitcoin_attestation_present_unverified'
    elif attestations and all(isinstance(a, PendingAttestation) for a in attestations):
        state = 'pending_only'
    else:
        state = 'other_unverified'
    return state, ';'.join(map(str, heights))


def verify(root=ROOT, check_ots=False):
    checksum_file = root / 'metadata/SHA256SUMS'
    checksums = {}
    for line in checksum_file.read_text(encoding='utf-8').splitlines():
        digest, sep, relative = line.partition('  ')
        if not sep or not re.fullmatch(r'[0-9a-f]{64}', digest) or relative in checksums:
            raise ValueError('Malformed or duplicate checksum entry.')
        checksums[relative] = digest
    with (root / 'metadata/forecast_index.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError('Archive index is empty.')
    expected = {}
    proof_counts = Counter()
    sources = set()
    for row in rows:
        classification = classify(row['source_relative_path'])
        if any(row[key] != value for key, value in classification.items()):
            raise ValueError(f'Incorrect classification: {row["json_path"]}')
        if row['source_relative_path'] in sources:
            raise ValueError('Duplicate source record in index.')
        sources.add(row['source_relative_path'])
        if row['ots_path'] != row['json_path'] + '.ots':
            raise ValueError('Unexpected JSON/OTS pairing.')
        for kind in ('json', 'ots'):
            relative = row[kind + '_path']
            if relative in expected:
                raise ValueError(f'Duplicate indexed path: {relative}')
            data = archive_path(root, relative).read_bytes()
            digest = sha256(data)
            if digest != row[kind + '_sha256'] or len(data) != int(row[kind + '_bytes']):
                raise ValueError(f'Changed file bytes: {relative}')
            expected[relative] = digest
            if kind == 'json':
                json.loads(data)
        if row['ots_digest_matches_json'] != 'true':
            raise ValueError(f'Unmatched proof recorded: {row["json_path"]}')
        if check_ots:
            state, heights = proof_info((root / row['ots_path']).read_bytes(), row['json_sha256'])
            if (state, heights) != (row['ots_attestation_state'], row['bitcoin_block_heights']):
                raise ValueError(f'Proof metadata differs: {row["ots_path"]}')
        proof_counts[row['ots_attestation_state']] += 1
    actual = {
        p.relative_to(root).as_posix()
        for p in (root / 'forecasts').rglob('*')
        if (p.is_file() or p.is_symlink()) and p.name != '.DS_Store'
    }
    if actual != set(expected):
        raise ValueError(f'Archive inventory differs: {sorted(actual.symmetric_difference(expected))[:8]}')
    if checksums != expected:
        raise ValueError('SHA256SUMS differs from the file index.')
    return rows, proof_counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ots', action='store_true', help='Parse OTS proofs offline; requires requirements.txt.')
    args = parser.parse_args()
    try:
        rows, states = verify(check_ots=args.ots)
    except Exception as exc:
        parser.exit(1, f'Verification failed: {exc}\n')
    print(f'PASS: {len(rows)} JSON/OTS pairs; {len(rows) * 2} files match the index and checksums.')
    if args.ots:
        print('PASS: all OTS proofs parse and commit to their JSON SHA-256 digest.')
    print('Saved proof states: ' + json.dumps(dict(states), sort_keys=True))
    print('External blockchain timestamps, X posts, and pre-event timing were not verified by this command.')


if __name__ == '__main__':
    main()
