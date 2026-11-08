import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

SOURCE_URL = 'https://donnees.roulez-eco.fr/opendata/instantane'


def ingest(run_date, base_dir='data', url=SOURCE_URL):
    out_dir = Path(base_dir) / 'bronze' / f'date={run_date}'
    out_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    raw_path = out_dir / 'prix_carburants.zip'
    raw_path.write_bytes(response.content)

    meta = {
        'source': url,
        'run_date': run_date,
        'ingested_at': datetime.now(timezone.utc).isoformat(),
        'bytes': len(response.content),
    }

    (out_dir / '_meta.json').write_text(json.dumps(meta, indent=2))
    return raw_path


if __name__ == '__main__':
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=today)
    parser.add_argument('--url', default=SOURCE_URL)

    args = parser.parse_args()

    print(ingest(args.date, url=args.url))



