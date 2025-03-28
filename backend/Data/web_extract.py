import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def extract_financial_data(ticker_symbol):
    """
    Extract financial data for a given company ticker using yfinance
    and save it to CSV files in a dedicated folder
    """
    ticker = yf.Ticker(ticker_symbol)
    
    output_dir = f"./company_data/{ticker_symbol}"
    os.makedirs(output_dir, exist_ok=True)
    
    end_date = datetime(2024, 3, 31)
    start_date = end_date - timedelta(days=366) # 1 year of data
    
    try:
        stock_data = ticker.history(start=start_date, end=end_date)
        stock_data.to_csv(f"{output_dir}/stock_prices.csv")
        
        # Financial statements -> keeping it to for 2 years
        balance_sheet = ticker.balance_sheet
        balance_sheet.iloc[:,:2].to_csv(f"{output_dir}/balance_sheet.csv")
        
        income_stmt = ticker.income_stmt
        income_stmt.iloc[:,:2].to_csv(f"{output_dir}/income_statement.csv")
        
        cash_flow = ticker.cash_flow
        cash_flow.iloc[:,:2].to_csv(f"{output_dir}/cash_flow.csv")
        
        info = pd.DataFrame.from_dict(ticker.info, orient='index')
        info.to_csv(f"{output_dir}/company_info.csv")
        
        print(f"Successfully extracted data for {ticker_symbol}")
        return True
        
    except Exception as e:
        print(f"Error extracting data for {ticker_symbol}: {str(e)}")
        return False

if __name__ == "__main__":
    symbols = ['HDB' , 'INFY', 'LICI.NS']
    for ticker_symbol in symbols:
        extract_financial_data(ticker_symbol.upper())