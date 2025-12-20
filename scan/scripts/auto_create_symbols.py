import os
import django
import redis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from screener.models import Symbol

r = redis.Redis(host='localhost', port=6379, db=0)

# Get all bar keys
keys = r.keys('bars:*')
print(f'Found {len(keys)} bar keys')

# Extract unique symbols
symbols = set()
for key in keys:
    parts = key.decode().split(':')
    if len(parts) >= 3:
        market_type = parts[1]  # spot or futures
        symbol = parts[2]
        symbols.add((symbol, market_type))

print(f'Found {len(symbols)} unique symbols')

# Create symbols in database
created = 0
for symbol, market_type in symbols:
    obj, was_created = Symbol.objects.get_or_create(
        symbol=symbol,
        market_type=market_type
    )
    if was_created:
        created += 1

print(f'Created {created} new symbols')
print(f'Total symbols in DB: {Symbol.objects.count()}')
