#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import pandas as pd
import random
import time
import os
from datetime import datetime, timedelta

# ✅ User-Agent list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

# ✅ Function to get random headers
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }

# ✅ Function to fetch stock data for each trading day
def fetch_daily_stock_data(stock_symbol):
    session = requests.Session()
    headers = get_headers()

    base_url = "https://www.nseindia.com/api/historical/cm/equity"
    
    start_date = datetime.now() - timedelta(days=365 * 2)  # 10 years back
    end_date = datetime.now()

    all_data = []
    missing_dates = []

    print(f"📊 Fetching daily stock data for {stock_symbol.upper()} from {start_date.date()} to {end_date.date()}...\n")

    # ✅ Loop through each day in the last 10 years
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() >= 5:  # Skip weekends (Saturday = 5, Sunday = 6)
            current_date += timedelta(days=1)
            continue

        date_str = current_date.strftime("%d-%m-%Y")  # Format: DD-MM-YYYY
        params = {
            "symbol": stock_symbol.upper(),
            "from": date_str,
            "to": date_str
        }

        try:
            # First request to establish session
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
            time.sleep(random.uniform(1, 3))  # Random delay

            # Fetch data
            response = session.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or not data["data"]:
                print(f"❌ No data for {date_str}")
                missing_dates.append(date_str)
            else:
                for entry in data["data"]:
                    all_data.append({
                        "Date": entry["CH_TIMESTAMP"],
                        "Stock Name": stock_symbol.upper(),
                        "Open Price": entry["CH_OPENING_PRICE"],
                        "High Price": entry["CH_TRADE_HIGH_PRICE"],
                        "Low Price": entry["CH_TRADE_LOW_PRICE"],
                        "Close Price": entry["CH_CLOSING_PRICE"],
                        "Volume": entry["CH_TOT_TRADED_QTY"],
                    })
                print(f"✅ Data retrieved for {date_str}")

            time.sleep(random.uniform(1, 3))  # Avoid bot detection

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request failed for {date_str}: {e}")
            missing_dates.append(date_str)

        current_date += timedelta(days=1)  # Move to the next day

    # ✅ Convert to DataFrame
    df = pd.DataFrame(all_data)

    if df.empty:
        print("⚠️ No data retrieved. Please check the stock symbol or NSE availability.")
        return None, missing_dates

    return df, missing_dates

# ✅ Get stock symbol from environment variable
stock_symbol = os.getenv("STOCK_SYMBOL", "TCS")  # Default to TCS if not provided
df, missing_dates = fetch_daily_stock_data(stock_symbol)

if df is not None:
    filename = f"{stock_symbol.lower()}_10yr_daily_stock_data.csv"
    df.to_csv(filename, index=False)
    print(f"\n📂 Data saved to {filename}")

    # Print missing dates
    if missing_dates:
        print("\n⚠️ The following dates had missing data:")
        print(", ".join(missing_dates[:10]) + " ...")  # Show first 10 missing dates
    else:
        print("\n✅ Data is available for all trading days!")

    print(df.head())  # Show first 5 rows

