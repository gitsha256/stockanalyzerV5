import pandas as pd
import requests
import io
import os
import logging
from datetime import date

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

try:
    import pandas_market_calendars as mcal
    NSE_CALENDAR = mcal.get_calendar('BSE')
except Exception:
    NSE_CALENDAR = None
    logger.warning("pandas_market_calendars is not installed or could not be loaded; holidays column will be blank.")


def get_market_holidays_since_2023():
    """Returns NSE/BSE market holiday dates from 2023 through today."""
    start_date = date(2023, 1, 1)
    end_date = date.today()
    if NSE_CALENDAR is None:
        return ""

    try:
        schedule = NSE_CALENDAR.schedule(start_date=start_date, end_date=end_date)
        business_days = pd.bdate_range(start=start_date, end=end_date)
        market_days = schedule.index.normalize()
        holiday_days = business_days.difference(market_days)
        return ",".join(holiday_days.strftime("%d-%m-%Y"))
    except Exception as e:
        logger.warning(f"Could not compute market holidays: {e}")
        return ""


def refresh_full_market_symbols(output_file='non-nifty500.csv'):
    """
    Downloads the master list of ALL NSE equities, applies corrections,
    and saves to non-nifty500.csv for a full-market scope.
    """
    # Official NSE Master List of all listed equities
    MASTER_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    # Nifty 500 list used to cross-reference sectors
    N500_URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    
    CORRECTIONS = {
        "NAM": "NAM-INDIA",
        "L&TFH": "LTF",
        "AMARAJABAT": "ARE&M",
        "LTI": "LTIM",
        "CADILAHC": "ZYDUSLIFE",
        "TATAMTRDVR": "TATAMOTORS"
    }

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # 1. Get Nifty 500 for sector mapping
        logger.info("Fetching Nifty 500 for sector cross-referencing...")
        n500_resp = requests.get(N500_URL, headers=headers)
        n500_df = pd.read_csv(io.StringIO(n500_resp.text))
        sector_map = dict(zip(n500_df['Symbol'].str.strip(), n500_df['Industry'].str.strip()))

        # 2. Get the Master List (All Stocks)
        logger.info("Downloading NSE Master Equity List (EQUITY_L)...")
        master_resp = requests.get(MASTER_URL, headers=headers)
        master_resp.raise_for_status()
        master_raw = pd.read_csv(io.StringIO(master_resp.text))
        
        # Clean up column names (NSE often has leading/trailing spaces in headers)
        master_raw.columns = [c.strip() for c in master_raw.columns]
        
        # Filter for only standard Equity series
        master_raw = master_raw[master_raw['SERIES'] == 'EQ'].copy()
        logger.info(f"Fetched {len(master_raw)} total listed equities.")

        # 3. Transform and Correct
        def process_row(row):
            sym = str(row['SYMBOL']).strip().upper()
            # Apply yfinance specific ticker corrections
            if sym in CORRECTIONS:
                sym = CORRECTIONS[sym]
            
            # Get sector from Nifty 500 map or default to 'Full Market'
            sector = sector_map.get(sym, "Full Market / Other")
            return pd.Series([f"{sym}-EQ", sector])

        new_df = master_raw.apply(process_row, axis=1)
        new_df.columns = ['Symbol', 'Sector']
        
        # Filter out Nifty 500 symbols to maintain "non-nifty" scope
        nifty_symbols = [f"{s.strip().upper()}-EQ" for s in n500_df['Symbol'].unique()]
        new_df = new_df[~new_df['Symbol'].isin(nifty_symbols)].copy()
        logger.info(f"Filtered to {len(new_df)} non-Nifty 500 symbols.")

        # 4. Get market holidays since 2023
        holidays = get_market_holidays_since_2023()
        if not holidays and os.path.exists(output_file):
            try:
                existing = pd.read_csv(output_file)
                existing.columns = [c.strip().upper() for c in existing.columns]
                if 'HOLIDAYS' in existing.columns:
                    h_list = existing['HOLIDAYS'].dropna().unique()
                    if len(h_list) > 0:
                        holidays = h_list[0]
            except Exception as e:
                logger.warning(f"Could not preserve holidays: {e}")

        # 5. Create holidays dataframe (separate rows, one per holiday)
        new_df['holidays'] = ""
        holidays_list = holidays.split(',') if holidays else []
        holidays_df = pd.DataFrame({'Symbol': [''] * len(holidays_list), 
                                    'Sector': [''] * len(holidays_list),
                                    'holidays': holidays_list})
        
        # Combine holidays first, then stocks
        final_df = pd.concat([holidays_df, new_df], ignore_index=True)

        # 6. Save the file
        final_df.to_csv(output_file, index=False)
        logger.info(f"Successfully updated {output_file} with {len(new_df)} stocks and {len(holidays_list)} holidays.")

    except Exception as e:
        logger.error(f"Failed to update full market symbols: {e}")

if __name__ == "__main__":
    refresh_full_market_symbols()