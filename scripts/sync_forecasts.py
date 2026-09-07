#!/usr/bin/env python3
"""Import completed JSON/OTS pairs without changing source or archived bytes."""

import argparse
import csv
import io
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from verify_archive import ROOT, proof_info, sha256, verify
from archive_layout import COLLECTIONS, EXCLUDED_COLLECTIONS, classify
FIELDS = [
    'sport', 'competition', 'competition_label', 'season_or_year', 'forecast_month',
    'source_collection', 'source_relative_path', 'json_path', 'forecast_date_from_filename',
    'target_date', 'target_date_source', 'generated_at_raw', 'model_record_count',
    'model_label_count', 'json_bytes', 'json_sha256', 'ots_path', 'ots_bytes',
    'ots_sha256', 'ots_digest_matches_json', 'ots_attestation_state',
    'bitcoin_block_heights', 'first_imported_at_utc', 'x_post_url',
]
SECRET_PATTERNS = {
    'provider credential': re.compile(r'\b(?:sk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|tvly-[A-Za-z0-9_-]{20,})'),
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'authorization header': re.compile(r'(?i)authorization[\s"\x27]*[:=][\s"\x27]*bearer\s+[A-Za-z0-9_.-]{16,}'),
    'URL credential': re.compile(r'(?i)[?&](?:api_key|apikey|access_token|token)=[^\s"&<>]{12,}'),
}


def write_if_changed(path, text):
    data = text.encode('utf-8')
    if path.exists() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(data)
    os.replace(temporary, path)


def make_row(relative, data, proof_data, imported_at):
    classification = classify(relative.as_posix())
    obj = json.loads(data)
    if isinstance(obj, dict):
        meta, records = obj.get('meta_info', {}), obj.get('model_predictions', [])
    else:
        raise ValueError(f'Unexpected JSON structure: {relative}')
    if not isinstance(meta, dict) or not isinstance(records, list):
        raise ValueError(f'Unexpected forecast schema: {relative}')
    model_labels = {str(r['model_name']) for r in records if isinstance(r, dict) and r.get('model_name')}
    digest = sha256(data)
    state, heights = proof_info(proof_data, digest)
    return {
        **classification,
        'generated_at_raw': str(meta.get('generated_at', '')),
        'model_record_count': str(len(records)),
        'model_label_count': str(len(model_labels)),
        'json_bytes': str(len(data)), 'json_sha256': digest,
        'ots_path': classification['json_path'] + '.ots',
        'ots_bytes': str(len(proof_data)), 'ots_sha256': sha256(proof_data),
        'ots_digest_matches_json': 'true', 'ots_attestation_state': state,
        'bitcoin_block_heights': heights, 'first_imported_at_utc': imported_at,
        'x_post_url': '',
    }


def write_metadata(rows):
    rows = sorted(rows, key=lambda row: row['json_path'])
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    write_if_changed(ROOT / 'metadata/forecast_index.csv', buf.getvalue())
    sums = {}
    for row in rows:
        for kind in ('json', 'ots'):
            sums[row[kind + '_path']] = row[kind + '_sha256']
    write_if_changed(ROOT / 'metadata/SHA256SUMS', ''.join(f'{sums[p]}  {p}\n' for p in sorted(sums)))
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['sport'], row['competition'], row['season_or_year'])].append(row)
    states = Counter(row['ots_attestation_state'] for row in rows)
    total_bytes = sum(int(row['json_bytes']) + int(row['ots_bytes']) for row in rows)
    latest_import = max(row['first_imported_at_utc'] for row in rows)
    lines = [
        '# Archive snapshot', '',
        f'Latest first-import time represented: **{latest_import}**.', '',
        f'**{len(rows)} forecast batches**, each with one original JSON and one matching OTS file: '
        f'**{len(rows) * 2} files**, **{total_bytes / 1_000_000:.2f} MB** (decimal).', '',
        'The counts below describe files, not matches or a balanced analysis sample. Date ranges use '
        'available target-date fields; they do not establish continuous coverage.', '',
        '| Sport | Competition | Season / year | Batches | Earliest target | Latest target |',
        '| --- | --- | --- | ---: | --- | --- |',
    ]
    catalog = [
        '# Browse forecasts', '',
        'Choose a sport, competition, season or tournament year, then the **forecast month**. '
        'Months refer to the date the forecast was made, as recorded in the filename, not the event date. '
        'Each original JSON stays next to its matching `.json.ots` proof.', '',
        f'This archive contains **{len(rows)} JSON files and {len(rows)} OTS files**. '
        'F1, policy predictions, and pilot runs are excluded.', '',
    ]
    current_sport = None
    for (sport, competition, season), group in sorted(grouped.items()):
        dates = sorted(r['target_date'] for r in group if r['target_date'])
        label = group[0]['competition_label']
        folder = f'../forecasts/{sport}/{competition}/{season}'
        lines.append(f'| {sport.title()} | [{label}]({folder}/) | {season} | {len(group)} | '
                     f'{dates[0] if dates else "not recorded"} | {dates[-1] if dates else "not recorded"} |')
        if sport != current_sport:
            catalog += [f'## {sport.title()}', '',
                        '| Competition | Season / year | JSON files | Forecast months (file count) |',
                        '| --- | --- | ---: | --- |']
            current_sport = sport
        months = Counter(r['forecast_month'] for r in group)
        month_links = ' · '.join(f'[{month} ({count})]({folder}/{month}/)' for month, count in sorted(months.items()))
        catalog.append(f'| [{label}]({folder}/) | {season} | {len(group)} | {month_links} |')
    # Insert a blank line before each heading following a table.
    catalog_text = '\n'.join(catalog).replace('\n## ', '\n\n## ')
    write_if_changed(ROOT / 'docs/forecast_catalog.md', catalog_text + '\n')
    lines += ['', '## Existing proof status', '',
              '| State | Files |', '| --- | ---: |']
    for state, count in sorted(states.items()):
        lines.append(f'| `{state}` | {count} |')
    lines += ['',
        'Every imported proof was fully parsed and its committed SHA-256 matched the original JSON. '
        'Bitcoin attestations, where present, were identified from the saved proof structure; their '
        'blockchain validity and event-relative times were not independently verified in this import. '
        'Pending proofs may need calendar upgrades before external verification.', '',
        'Per-file X links have not yet been systematically indexed. Blanks do not establish that no post exists.', '',
        'F1, policy predictions, World Cup pilot runs, backup proofs, and temporary files '
        'are outside this archive. See [data notes](data_notes.md) and the [verification guide](verification.md).', '',
    ]
    write_if_changed(ROOT / 'docs/archive_snapshot.md', '\n'.join(lines))


def sync(source):
    source = source.resolve()
    if not source.is_dir() or source == (ROOT / 'forecasts').resolve():
        raise ValueError('Provide the separate production forecast_results directory.')
    index = ROOT / 'metadata/forecast_index.csv'
    existing = {}
    if index.exists():
        old_rows, _ = verify(check_ots=True)
        existing = {row['json_path']: row for row in old_rows}
    elif (ROOT / 'forecasts').exists():
        raise ValueError('Archive files exist without an index; review before importing.')
    imported_at = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    additions, writes, skipped = [], [], Counter()
    candidates = sorted(source.rglob('*.json'))
    if not candidates:
        raise ValueError('No source JSON files found.')
    for path in candidates:
        relative = path.relative_to(source)
        if relative.parts[0] in EXCLUDED_COLLECTIONS:
            skipped[relative.parts[0]] += 1
            continue
        if any(part.startswith('pilot_smoke') for part in relative.parts):
            skipped['pilot_json'] += 1
            continue
        if relative.parts[0] not in COLLECTIONS or len(relative.parts) not in (2, 3):
            raise ValueError(f'Unexpected collection/layout: {relative}')
        if len(relative.parts) == 3 and not re.fullmatch(r'\d{4}_\d{2}', relative.parts[1]):
            raise ValueError(f'Unexpected nested directory: {relative}')
        proof_path = path.with_name(path.name + '.ots')
        if not proof_path.is_file():
            raise ValueError(f'Missing OTS companion: {relative}')
        if any(p.is_symlink() for p in [path, proof_path, *path.parents]):
            raise ValueError(f'Symlink in source path: {relative}')
        data, proof_data = path.read_bytes(), proof_path.read_bytes()
        text = data.decode('utf-8')
        for category, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                raise ValueError(f'Possible {category} in {relative}; inspect locally before publication.')
        row = make_row(relative, data, proof_data, imported_at)
        old = existing.get(row['json_path'])
        if old:
            if any(old[kind + '_sha256'] != row[kind + '_sha256'] for kind in ('json', 'ots')):
                raise ValueError(f'Refusing to overwrite changed archived bytes: {relative}')
            continue
        additions.append(row)
        writes.extend([(ROOT / row['json_path'], data), (ROOT / row['ots_path'], proof_data)])
    # All candidates have passed preflight before any raw file is copied.
    for target, _ in writes:
        if target.exists() or target.is_symlink():
            raise ValueError(f'Refusing existing unindexed destination: {target.relative_to(ROOT)}')
    for target, data in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output:
            output.write(data)
    all_rows = [*existing.values(), *additions]
    if not all_rows:
        raise ValueError('No production forecast pairs found.')
    write_metadata(all_rows)
    rows, states = verify(check_ots=True)
    print(f'Imported {len(additions)} new batches; archive has {len(rows)} JSON/OTS pairs.')
    print('Excluded source JSONs: ' + json.dumps(dict(skipped), sort_keys=True))
    print('Saved proof states: ' + json.dumps(dict(states), sort_keys=True))
    print('Source files were not changed. No upload or external timestamp verification was performed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Production forecast_results directory.')
    args = parser.parse_args()
    try:
        sync(args.source)
    except Exception as exc:
        parser.exit(1, f'Import stopped: {exc}\n')


if __name__ == '__main__':
    main()
