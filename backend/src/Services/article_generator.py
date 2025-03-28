import yfinance as yf
from typing import Dict, Any, List
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

class ArticleGeneratorService:
    @staticmethod
    async def generate_company_analysis(ticker: str) -> Dict[str, Any]:
        """Generate comprehensive company analysis articles"""
        try:
            company = yf.Ticker(ticker)
            
            # Create Analysis directory if it doesn't exist
            os.makedirs('./Analysis', exist_ok=True)
            
            # Generate different types of analysis
            analyses = {
                'financials': await ArticleGeneratorService._generate_financial_analysis(company, ticker),
                'business': await ArticleGeneratorService._generate_business_analysis(company, ticker),
                'technical': await ArticleGeneratorService._generate_technical_analysis(company, ticker)
            }
            
            # Save analyses to files
            for analysis_type, content in analyses.items():
                if content:
                    filename = f"./Analysis/{ticker}_{analysis_type}_analysis.txt"
                    with open(filename, 'w') as f:
                        f.write(content)
            
            return analyses
            
        except Exception as e:
            raise Exception(f"Error generating analysis: {str(e)}")

    @staticmethod
    async def _generate_financial_analysis(company, ticker: str) -> str:
        """Generate financial analysis article"""
        try:
            # Get financial data
            income_stmt = company.income_stmt
            balance_sheet = company.balance_sheet
            cashflow = company.cashflow
            
            if income_stmt is None or balance_sheet is None or cashflow is None:
                return ""
                
            # Create analysis content
            analysis = f"""Financial Analysis for {ticker}
Generated on {datetime.now().strftime('%Y-%m-%d')}

Revenue Analysis:
----------------
{ArticleGeneratorService._analyze_revenue(income_stmt)}

Profitability Analysis:
----------------------
{ArticleGeneratorService._analyze_profitability(income_stmt)}

Balance Sheet Analysis:
---------------------
{ArticleGeneratorService._analyze_balance_sheet(balance_sheet)}

Cash Flow Analysis:
-----------------
{ArticleGeneratorService._analyze_cashflow(cashflow)}
"""
            return analysis
            
        except Exception as e:
            print(f"Error generating financial analysis: {str(e)}")
            return ""

    @staticmethod
    def _analyze_revenue(income_stmt) -> str:
        try:
            revenue = income_stmt.loc['Total Revenue']
            latest_revenue = revenue.iloc[-1]
            yoy_growth = (revenue.iloc[-1] - revenue.iloc[-2]) / revenue.iloc[-2] * 100
            
            return f"""
Latest Revenue: ${latest_revenue:,.2f}
Year-over-Year Growth: {yoy_growth:.2f}%
Revenue Trend: {'Positive' if yoy_growth > 0 else 'Negative'}
"""
        except Exception as e:
            return f"Unable to analyze revenue: {str(e)}"

    @staticmethod
    def _analyze_profitability(income_stmt) -> str:
        try:
            net_income = income_stmt.loc['Net Income']
            operating_income = income_stmt.loc['Operating Income']
            
            latest_net_income = net_income.iloc[-1]
            latest_operating_income = operating_income.iloc[-1]
            
            return f"""
Net Income: ${latest_net_income:,.2f}
Operating Income: ${latest_operating_income:,.2f}
Profit Margin: {(latest_net_income / income_stmt.loc['Total Revenue'].iloc[-1] * 100):.2f}%
"""
        except Exception as e:
            return f"Unable to analyze profitability: {str(e)}"

    # Add these methods to the ArticleGeneratorService class after the existing methods
    @staticmethod
    async def _generate_business_analysis(company, ticker: str) -> str:
        """Generate business analysis article"""
        try:
            info = company.info
            if not info:
                return ""
                
            analysis = f"""Business Analysis for {ticker}
Generated on {datetime.now().strftime('%Y-%m-%d')}

Company Overview:
---------------
Company Name: {info.get('longName', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Sector: {info.get('sector', 'N/A')}
Website: {info.get('website', 'N/A')}

Business Description:
------------------
{info.get('longBusinessSummary', 'No business summary available.')}

Market Position:
--------------
Market Cap: ${info.get('marketCap', 0):,.2f}
Full Time Employees: {info.get('fullTimeEmployees', 'N/A')}
Country: {info.get('country', 'N/A')}

Key Statistics:
-------------
52-Week High: ${info.get('fiftyTwoWeekHigh', 0):,.2f}
52-Week Low: ${info.get('fiftyTwoWeekLow', 0):,.2f}
Average Volume: {info.get('averageVolume', 0):,.0f}
P/E Ratio: {info.get('trailingPE', 'N/A')}
"""
            return analysis
            
        except Exception as e:
            print(f"Error generating business analysis: {str(e)}")
            return ""

    @staticmethod
    async def _generate_technical_analysis(company, ticker: str) -> str:
        """Generate technical analysis article"""
        try:
            # Get historical data for technical analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            history = company.history(start=start_date, end=end_date)
            
            if history.empty:
                return ""
                
            # Calculate some basic technical indicators
            current_price = history['Close'][-1]
            ma_50 = history['Close'].tail(50).mean()
            ma_200 = history['Close'].tail(200).mean()
            rsi = ArticleGeneratorService._calculate_rsi(history['Close'])
            
            analysis = f"""Technical Analysis for {ticker}
Generated on {datetime.now().strftime('%Y-%m-%d')}

Price Analysis:
-------------
Current Price: ${current_price:.2f}
50-Day Moving Average: ${ma_50:.2f}
200-Day Moving Average: ${ma_200:.2f}

Technical Indicators:
------------------
Trend (50 MA vs 200 MA): {'Bullish' if ma_50 > ma_200 else 'Bearish'}
RSI (14-period): {rsi:.2f}
Market Condition: {'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'}

Volume Analysis:
--------------
Average Volume (10 days): {history['Volume'].tail(10).mean():,.0f}
Latest Volume: {history['Volume'][-1]:,.0f}
"""
            return analysis
            
        except Exception as e:
            print(f"Error generating technical analysis: {str(e)}")
            return ""

    @staticmethod
    def _calculate_rsi(prices, periods=14):
        """Calculate Relative Strength Index"""
        try:
            deltas = prices.diff()
            seed = deltas[:periods+1]
            up = seed[seed >= 0].sum()/periods
            down = -seed[seed < 0].sum()/periods
            rs = up/down
            rsi = 100 - (100/(1+rs))
            return rsi
        except Exception:
            return 50  # Return neutral RSI if calculation fails

    @staticmethod
    def _analyze_balance_sheet(balance_sheet) -> str:
        try:
            assets = balance_sheet.loc['Total Assets'].iloc[-1]
            liabilities = balance_sheet.loc['Total Liabilities'].iloc[-1]
            equity = assets - liabilities
            
            return f"""
Total Assets: ${assets:,.2f}
Total Liabilities: ${liabilities:,.2f}
Shareholders Equity: ${equity:,.2f}
Debt to Equity Ratio: {(liabilities / equity):.2f}
"""
        except Exception as e:
            return f"Unable to analyze balance sheet: {str(e)}"

    @staticmethod
    def _analyze_cashflow(cashflow) -> str:
        try:
            operating_cf = cashflow.loc['Operating Cash Flow'].iloc[-1]
            investing_cf = cashflow.loc['Investing Cash Flow'].iloc[-1]
            financing_cf = cashflow.loc['Financing Cash Flow'].iloc[-1]
            
            return f"""
Operating Cash Flow: ${operating_cf:,.2f}
Investing Cash Flow: ${investing_cf:,.2f}
Financing Cash Flow: ${financing_cf:,.2f}
Free Cash Flow: ${(operating_cf + investing_cf):,.2f}
"""
        except Exception as e:
            return f"Unable to analyze cash flow: {str(e)}"