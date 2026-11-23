import pandas as pd

from transform.silver import clean, parse_xml, read_xml_bytes

SAMPLE = 'tests/fixtures/sample.xml'


def make_row(**overrides):
    row = {
        'station_id': '1000001',
        'postal_code': '01000',
        'city': 'BOURG',
        'address': '1 RUE TEST',
        'latitude': '4620114',
        'longitude': '519791',
        'fuel_id': '1',
        'fuel_name': 'Gazole',
        'maj': '2026-11-04 09:00:00',
        'valeur': '2.309',
    }
    row.update(overrides)
    return row


def test_parse_xml_returns_rows():
    df = parse_xml(read_xml_bytes(SAMPLE))
    assert len(df) > 0
    assert {'station_id', 'fuel_id', 'valeur'} <= set(df.columns)


def test_clean_removes_out_of_range_prices():
    df = pd.DataFrame([make_row(), make_row(station_id='2', valeur='-1')])
    cleaned, stats = clean(df)
    assert len(cleaned) == 1
    assert stats['rejected_price_out_of_range'] == 1


def test_clean_removes_duplicates():
    df = pd.DataFrame([make_row(), make_row()])
    cleaned, stats = clean(df)
    assert len(cleaned) == 1
    assert stats['duplicates_removed'] == 1


def test_clean_rejects_missing_prices():
    df = pd.DataFrame([make_row(valeur=None)])
    cleaned, stats = clean(df)
    assert len(cleaned) == 0
    assert stats['rejected_missing_values'] == 1