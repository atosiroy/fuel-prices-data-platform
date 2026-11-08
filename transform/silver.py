import argparse
import io
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import pandas as pd
def read_xml_bytes(path):
    path = Path(path)
    if path.suffix == '.zip':
        with zipfile.ZipFile(path) as archive:
            return archive.read(archive.namelist()[0])
    return path.read_bytes()

def parse_xml(xml_bytes):
    rows = []
    for _, element in ET.iterparse(io.BytesIO(xml_bytes), events=('end',)):
        if element.tag != 'pdv':
            continue
    
    station = {
        'station_id': element.get('id'),
        'postal_code': element.get('cp'),
        'city': (element.findtext('ville') or '').strip().upper(),
        'address': (element.findtext('adresse') or '').strip(),
        'latitude': element.get('latitude'),
        'longitude': element.get('longitude'),
        }
    for price in element.findall('prix'):
        rows.append({
         **station,
        'fuel_id': price.get('id'),
        'fuel_name': price.get('nom'),
        'price_updated_at': price.get('maj'),
        'price_eur': price.get('valeur'),
        })
        element.clear()
    return pd.DataFrame(rows)

# validation file
def clean(df):
    stats = {'rows_in': len(df)}
    df = df.copy()
    df['price_eur'] = pd.to_numeric(df['price_eur'], errors='coerce')
    df['price_updated_at'] = pd.to_datetime(df['price_updated_at'],errors='coerce')

    for column in ('latitude', 'longitude'):
        df[column] = pd.to_numeric(df[column], errors='coerce') / 100000
    required = ['station_id', 'fuel_id', 'price_eur', 'price_updated_at']
    before = len(df)
    df = df.dropna(subset=required)
    stats['rejected_missing_values'] = before - len(df)
    before = len(df)
    df = df[(df['price_eur'] > 0) & (df['price_eur'] < 5)]
    stats['rejected_price_out_of_range'] = before - len(df)
    before = len(df)
    df = df.drop_duplicates(subset=['station_id', 'fuel_id','price_updated_at'])
    stats['duplicates_removed'] = before - len(df)
    stats['rows_out'] = len(df)
    return df, stats

# The output path depends only on the run date, so rerunning a date replaces its partition and never duplicates rows
def run(run_date, input_path=None, base_dir='data'):
    base = Path(base_dir)
    if input_path is None:
        input_path = next((base / 'bronze' / f'date={run_date}').glob('*.zip'))

    df, stats = clean(parse_xml(read_xml_bytes(input_path)))
    df['ingestion_date'] = run_date

    silver_dir = base / 'silver' / 'prices' / f'date={run_date}'
    silver_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(silver_dir / 'part.parquet', index=False)

    report_dir = base / 'reports' / f'date={run_date}'
    report_dir.mkdir(parents=True, exist_ok=True)
    stats['run_date'] = run_date
    (report_dir / 'validation.json').write_text(json.dumps(stats, indent=2))
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', required=True)
    parser.add_argument('--input', default=None)
    args = parser.parse_args()
    print(run(args.date, args.input))