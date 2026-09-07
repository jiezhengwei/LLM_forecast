"""Public archive taxonomy, independent of the production folder layout."""

import re
from datetime import date
from pathlib import PurePosixPath

# Source collection -> sport, competition slug, readable name, season/year type.
COLLECTIONS = {
    'NBA_forecasts': ('basketball', 'nba', 'NBA', 'season'),
    'Premier League_forecasts': ('football', 'premier-league', 'Premier League', 'season'),
    'La Liga_forecasts': ('football', 'la-liga', 'La Liga', 'season'),
    'Bundesliga_forecasts': ('football', 'bundesliga', 'Bundesliga', 'season'),
    'Serie A_forecasts': ('football', 'serie-a', 'Serie A', 'season'),
    'Ligue 1_forecasts': ('football', 'ligue-1', 'Ligue 1', 'season'),
    'UCL_forecasts': ('football', 'champions-league', 'UEFA Champions League', 'season'),
    'WorldCup_2026': ('football', 'world-cup', 'FIFA World Cup', '2026'),
    'Wimbledon_2026': ('tennis', 'wimbledon', 'Wimbledon', '2026'),
    'US_Open_2026': ('tennis', 'us-open', 'US Open', '2026'),
}
EXCLUDED_COLLECTIONS = {'F1_forecasts', 'Policy_forecasts'}


def classify(source_relative_path):
    relative = PurePosixPath(source_relative_path)
    if relative.is_absolute() or '..' in relative.parts or len(relative.parts) not in (2, 3):
        raise ValueError(f'Unexpected source layout: {relative}')
    collection = relative.parts[0]
    if collection not in COLLECTIONS:
        raise ValueError(f'Collection is outside the public archive: {collection}')
    sport, competition, label, period_type = COLLECTIONS[collection]
    match = re.search(r'_pred_on_(\d{4}-\d{2}-\d{2})_for_(\d{4}-\d{2}-\d{2})(?:_|\.json)', relative.name)
    if not match or not relative.name.endswith('.json'):
        raise ValueError(f'Unrecognized production filename: {relative}')
    forecast_date, target_date = (date.fromisoformat(x) for x in match.groups())
    if period_type == 'season':
        if len(relative.parts) == 3:
            season_match = re.fullmatch(r'(\d{4})_(\d{2})', relative.parts[1])
            if not season_match:
                raise ValueError(f'Expected a source season such as 2026_27: {relative}')
            start_year = int(season_match[1])
            if int(season_match[2]) != (start_year + 1) % 100:
                raise ValueError(f'Invalid source season: {relative}')
        else:
            # The unpartitioned legacy NBA and club-football folders are 2025-26.
            # Later seasons must have an explicit source season subfolder.
            start_year = 2025
        if not date(start_year, 7, 1) <= target_date < date(start_year + 1, 7, 1):
            raise ValueError(f'Target date is outside its documented source season: {relative}')
        period = f'{start_year}-{(start_year + 1) % 100:02d}'
    else:
        if len(relative.parts) != 2 or target_date.year != int(period_type):
            raise ValueError(f'Target date/layout does not match tournament year: {relative}')
        period = period_type
    month = forecast_date.strftime('%Y-%m')
    return {
        'sport': sport, 'competition': competition, 'competition_label': label,
        'season_or_year': period, 'forecast_month': month,
        'source_collection': collection, 'source_relative_path': relative.as_posix(),
        'json_path': f'forecasts/{sport}/{competition}/{period}/{month}/{relative.name}',
        'forecast_date_from_filename': forecast_date.isoformat(),
        'target_date': target_date.isoformat(), 'target_date_source': 'filename',
    }
