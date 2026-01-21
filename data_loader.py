import csv
from datetime import datetime
from models import MarketDataPoint

def parse_timestamp(timestamp_str: str) -> datetime:
    clean_str = timestamp_str[:-6]
    return datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")

def load_market_data(filename: str) -> list[MarketDataPoint]:
    data_points = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            point = MarketDataPoint(
                timestamp = parse_timestamp(row['timestamp']),
                symbol = row('symbol'),
                price = float(row('price'))
            )
            data_points.append(point)
    return data_points

def load_market_data_limited(filename: str, limit: int) -> list[MarketDataPoint]:
    data_points = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            point = MarketDataPoint(
                timestamp = parse_timestamp(row['timestamp']),
                symbol = row['symbol'],
                price = float(row['price'])
            )
            data_points.append(point)
    return data_points