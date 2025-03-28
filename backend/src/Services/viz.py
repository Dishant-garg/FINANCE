import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from typing import Dict, Any
from datetime import datetime, timedelta
import base64
import traceback

class VisualizationService:
    @staticmethod
    async def get_stock_visualizations(ticker: str) -> Dict[str, Any]:
        """Generate interactive visualizations for company financials"""
        try:
            company = yf.Ticker(ticker)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3*365)
            stock_data = company.history(start=start_date, end=end_date)
            
            visualizations = {
                "stock_price": await VisualizationService._create_stock_chart(stock_data, ticker),
                "revenue_growth": await VisualizationService._create_revenue_chart(company),
                "profitability": await VisualizationService._create_profitability_chart(company)
            }
            
            return visualizations
            
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {}

    @staticmethod
    async def _convert_fig_to_base64(fig) -> str:
        """Convert plotly figure to base64 string"""
        try:
            # Ensure figure has layout
            if fig.layout is None:
                fig.layout = go.Layout()
            
            # Set static image size
            fig.update_layout(width=800, height=500)
            
            # Attempt to configure renderer if kaleido is available
            try:
                import kaleido
                pio.kaleido.scope.mathjax = None
            except ImportError:
                print("Kaleido not available. Using default rendering.")
            
            # Convert to image with higher quality
            img_bytes = pio.to_image(fig, format="png", scale=2)
            
            # Convert to base64
            base64_string = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_string}"
        except Exception as e:
            print(f"Error in _convert_fig_to_base64: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return ""

    @staticmethod
    async def _create_stock_chart(stock_data, ticker: str) -> str:
        """Create stock price chart"""
        try:
            # Check if stock_data is empty
            if stock_data.empty:
                print(f"No stock data available for {ticker}")
                return ""
            
            fig = go.Figure(data=[
                go.Candlestick(
                    x=stock_data.index,
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    open=stock_data['Open'],
                    close=stock_data['Close'],
                    name='Stock Price'
                )
            ])
            
            fig.update_layout(
                title=f"{ticker} Stock Price Movement",
                yaxis_title="Price",
                xaxis_title="Date",
                template="plotly_dark",
                width=800,
                height=500
            )
            
            return await VisualizationService._convert_fig_to_base64(fig)
        except Exception as e:
            print(f"Error creating stock chart: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return ""

    @staticmethod
    async def _create_revenue_chart(company) -> str:
        """Create revenue trend visualization"""
        try:
            # Check if income statement exists
            if company.income_stmt is None or company.income_stmt.empty:
                print("No income statement data available")
                return ""
            
            # Find revenue column
            revenue_columns = ['Total Revenue', 'Revenues', 'Revenue']
            revenue_data = None
            
            for col in revenue_columns:
                if col in company.income_stmt.index:
                    revenue_data = company.income_stmt.loc[col]
                    break
            
            # If no revenue data found
            if revenue_data is None or revenue_data.empty:
                print("No revenue data found")
                return ""
            
            # Create figure
            fig = px.line(
                x=revenue_data.index,
                y=revenue_data.values,
                title="Revenue Growth Trend"
            )
            
            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Revenue ($)",
                showlegend=True,
                width=800,
                height=500
            )
            
            return await VisualizationService._convert_fig_to_base64(fig)
        except Exception as e:
            print(f"Error creating revenue chart: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return ""

    @staticmethod
    async def _create_profitability_chart(company) -> str:
        """Create profitability metrics visualization"""
        try:
            # Check if income statement exists
            if company.income_stmt is None or company.income_stmt.empty:
                print("No income statement data available")
                return ""
            
            # Find income columns
            net_income_fields = ['Net Income', 'NetIncome', 'Net Income Common Stockholders']
            operating_income_fields = ['Operating Income', 'OperatingIncome', 'EBIT']
            
            net_income = None
            operating_income = None
            
            # Find net income
            for field in net_income_fields:
                if field in company.income_stmt.index:
                    net_income = company.income_stmt.loc[field]
                    break
            
            # Find operating income
            for field in operating_income_fields:
                if field in company.income_stmt.index:
                    operating_income = company.income_stmt.loc[field]
                    break
            
            # Check if both incomes are found
            if net_income is None or operating_income is None:
                print("Could not find income data")
                return ""
            
            # Create figure
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=net_income.index,
                y=net_income.values,
                name="Net Income"
            ))
            fig.add_trace(go.Bar(
                x=operating_income.index,
                y=operating_income.values,
                name="Operating Income"
            ))
            
            fig.update_layout(
                title="Profitability Metrics",
                barmode='group',
                template="plotly_dark",
                yaxis_title="Amount ($)",
                xaxis_title="Date",
                width=800,
                height=500
            )
            
            return await VisualizationService._convert_fig_to_base64(fig)
        except Exception as e:
            print(f"Error creating profitability chart: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return ""