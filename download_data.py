# download_data.py
# Downloads real stock data and extends it with realistic synthetic data

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Step 1: Download real data for one stock
print("\n[1/3] Downloading real ANET data from Yahoo Finance...")

ticker = yf.Ticker("ANET")
real_data = ticker.history(period="7d", interval="1m")

# Fix the column structure (handles multi-level columns from newer yfinance)
real_data = real_data.reset_index()

# Keep only the columns we need and rename them
real_data = real_data[['Datetime', 'Close']].copy()
real_data.columns = ['timestamp', 'price']  # Simple column names
real_data['symbol'] = 'ANET'

# Reorder columns to match assignment spec
real_data = real_data[['timestamp', 'symbol', 'price']]

# Remove any rows with missing prices
real_data = real_data.dropna()

print(f"    Downloaded {len(real_data)} rows of real data")

# Step 2: Generate synthetic data to reach 100,000+ rows
print("\n[2/3] Generating synthetic data to reach 100,000 rows...")

# We need this many additional rows
target_total = 105000
rows_needed = target_total - len(real_data)

# Get the last price and timestamp from real data
last_real_price = real_data['price'].iloc[-1]
last_real_timestamp = real_data['timestamp'].iloc[-1]

# Generate synthetic prices using a "random walk" model
np.random.seed(42)

# Daily volatility of about 1-2% is realistic for stocks
minute_volatility = 0.0005

# Generate random returns
random_returns = np.random.normal(0, minute_volatility, rows_needed)

# Convert returns to prices
synthetic_prices = [last_real_price]
for ret in random_returns:
    new_price = synthetic_prices[-1] * (1 + ret)
    synthetic_prices.append(new_price)

synthetic_prices = synthetic_prices[1:]

# Generate timestamps (1 minute apart)
synthetic_timestamps = []
current_time = last_real_timestamp

for i in range(rows_needed):
    current_time = current_time + timedelta(minutes=1)
    
    # Skip weekends
    while current_time.weekday() >= 5:
        current_time = current_time + timedelta(days=1)
        current_time = current_time.replace(hour=9, minute=30)
    
    # Keep market hours
    if current_time.hour >= 16:
        current_time = current_time + timedelta(days=1)
        current_time = current_time.replace(hour=9, minute=30)
    
    synthetic_timestamps.append(current_time)

# Create synthetic dataframe
synthetic_data = pd.DataFrame({
    'timestamp': synthetic_timestamps,
    'symbol': 'ANET',
    'price': synthetic_prices
})

print(f"    Generated {len(synthetic_data)} rows of synthetic data")

# Step 3: Combine and save
print("\n[3/3] Combining and saving to market_data.csv...")

combined = pd.concat([real_data, synthetic_data], ignore_index=True)
combined.to_csv('market_data.csv', index=False)

print(f"\n{'=' * 50}")
print(f"✅ SUCCESS!")
print(f"{'=' * 50}")
print(f"\nCreated market_data.csv with {len(combined):,} total rows")
print(f"  • Real data:      {len(real_data):,} rows")
print(f"  • Synthetic data: {len(synthetic_data):,} rows")
print(f"  • Symbol:         ANET (single ticker)")
print(f"\nPreview of data:")
print(combined.head(10))

# ============================================
# VISUALIZATION
# ============================================

import matplotlib.pyplot as plt

print("\nGenerating price charts...")

# Chart 1: Full series
plt.figure(figsize=(14, 6))
plt.plot(combined['price'].values, linewidth=0.5, color='blue', alpha=0.7)
real_data_end = len(real_data)
plt.axvline(x=real_data_end, color='red', linestyle='--', linewidth=1, label='Real → Synthetic')
plt.title('ANET Price Series (Real + Synthetic Data)', fontsize=14)
plt.xlabel('Tick Number', fontsize=12)
plt.ylabel('Price ($)', fontsize=12)
plt.legend()
plt.tight_layout()
plt.savefig('price_series.png', dpi=150)

# Chart 2: Zoomed views
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(real_data['price'].values, linewidth=0.5, color='green')
axes[0].set_title('Real ANET Data (Zoomed)', fontsize=12)
axes[0].set_xlabel('Tick Number')
axes[0].set_ylabel('Price ($)')
axes[0].grid(True, alpha=0.3)

axes[1].plot(combined['price'].values[:10000], linewidth=0.5, color='blue')
axes[1].axvline(x=len(real_data), color='red', linestyle='--', linewidth=2, label='Real → Synthetic')
axes[1].set_title('First 10,000 Ticks (Shows Transition)', fontsize=12)
axes[1].set_xlabel('Tick Number')
axes[1].set_ylabel('Price ($)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('price_series_zoomed.png', dpi=150)

print("✅ Saved charts")
plt.show()
