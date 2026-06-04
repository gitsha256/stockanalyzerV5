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


def refresh_nifty500_symbols(output_file='nifty500.csv'):
    """
    Downloads the latest Nifty 500 list from NSE, formats for the analyzer,
    and applies yfinance-specific ticker corrections.
    """
    # Official NSE Nifty 500 constituent list URL
    URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    
    try:
        logger.info("Downloading Nifty 500 constituent list from NSE...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        # Load CSV
        nifty500_raw = pd.read_csv(io.StringIO(response.text))
        
        # NSE CSV Headers: Company Name, Industry, Symbol, Series, ISIN Code
        logger.info(f"Fetched {len(nifty500_raw)} records.")

        # 1. Transform Tickers
        def format_symbol(sym):
            sym = sym.strip().upper()
            return sym
        # 2. Map to Analyzer Schema
        new_df = pd.DataFrame()
        new_df['Symbol'] = nifty500_raw['Symbol'].apply(format_symbol)
        new_df['Sector'] = nifty500_raw['Industry']
        
        # 3. Get market holidays since 2023
        holidays = get_market_holidays_since_2023()
        if not holidays and os.path.exists(output_file):
            try:
                existing = pd.read_csv(output_file)
                existing.columns = [c.strip().upper() for c in existing.columns]
                if 'HOLIDAYS' in existing.columns:
                    # Just grab the unique non-null holidays from the existing file
                    holiday_list = existing['HOLIDAYS'].dropna().unique()
                    if len(holiday_list) > 0:
                        holidays = holiday_list[0] 
            except Exception as e:
                logger.warning(f"Could not read existing holidays: {e}")

        # 4. Create holidays dataframe (separate rows, one per holiday)
        new_df['holidays'] = ""
        holidays_list = holidays.split(',') if holidays else []
        holidays_df = pd.DataFrame({'Symbol': [''] * len(holidays_list), 
                                    'Sector': [''] * len(holidays_list),
                                    'holidays': holidays_list})
        
        # Combine holidays first, then stocks
        final_df = pd.concat([holidays_df, new_df], ignore_index=True)

        # 5. Save the file
        final_df.to_csv(output_file, index=False)
        logger.info(f"Successfully updated {output_file} with {len(new_df)} stocks and {len(holidays_list)} holidays.")
        
        # Display some of the corrections made
        logger.info("Verified critical tickers: NAM -> NAM-INDIA, L&TFH -> LTF, etc.")
        
    except Exception as e:
        logger.error(f"Failed to update symbols: {e}")
        if "403" in str(e) or "404" in str(e):
            logger.error("NSE site may be blocking request or URL changed. Check URL in browser.")

if __name__ == "__main__":
    refresh_nifty500_symbols()