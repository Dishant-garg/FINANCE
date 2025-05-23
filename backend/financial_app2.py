# Import your analysis modules
import streamlit as st
import pandas as pd
import base64
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from Prompts import (
    balance_sheet,
    cashflow, 
    financials, 
    key_stats,
    story_tell
)


# Optional: Import services from your other app if available
try:
    from src.Services import article_generator, chat, education_resources, viz
    from src.Models import chat as chatting
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    print("Advanced features not available. Continuing with basic functionality.")

# Load environment variables
load_dotenv()

# Set page configuration - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Financial Analysis Suite", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)
TICKER2_MAPPING = {
        "HDB": "HDFC Bank",
        "INFY": "Infosys",
        "LICI.NS": "LIC India"
}
def get_ticker_dropdown(default_value=''):
    """
    Create a dropdown for selecting stock tickers with predefined options.
    
    Args:
        default_value (str, optional): Default ticker to pre-select. Defaults to ''.
    
    Returns:
        str: Selected ticker
    """
    TICKER_MAPPING = {
        "HDB": "HDFC Bank",
        "INFY": "Infosys",
        "LICI.NS": "LIC India"
    }
    
    # Create dropdown with full names for better readability
    options = list(TICKER_MAPPING.keys())
    display_options = [f"{ticker} - {TICKER_MAPPING[ticker]}" for ticker in options]
    
    # Find the default index
    default_index = 0
    if default_value in options:
        default_index = options.index(default_value)
    
    # Dropdown selection
    selected_display = st.selectbox(
        "Select Stock Ticker", 
        display_options, 
        index=default_index
    )
    
    # Extract the actual ticker from the selected display option
    selected_ticker = selected_display.split(" - ")[0]
    
    return selected_ticker



def validate_ticker(ticker):
    """Validate the input ticker."""
    # Add more robust validation if needed
    return ticker and len(ticker) > 0

def initialize_session_state():
    """Initialize all necessary session state variables."""
    # Initialize with default empty values
    default_states = {
        'selected_ticker': '',
        'analyses': {},
        'visualizations': {},
        'chat_history': [],
        'current_ticker': None
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def generate_analysis(ticker):
    """Wrapper function to generate analysis with error handling."""
    if not ADVANCED_FEATURES_AVAILABLE:
        return None
        
    try:
        
        analyses = asyncio.run(article_generator.ArticleGeneratorService.generate_company_analysis(ticker))
        visualizations = asyncio.run(viz.VisualizationService.get_stock_visualizations(ticker))
        
        return {
            'analyses': analyses,
            'visualizations': visualizations
        }
    except Exception as e:
        st.error(f"Error generating analysis for {ticker}: {str(e)}")
        return None

async def handle_chat_interaction(ticker, user_input):
    """Handle chat interaction with error logging."""
    if not ADVANCED_FEATURES_AVAILABLE:
        return "Advanced chat features are not available."
        
    try:
        chat_history = chatting.ChatHistory(
            company=ticker,
            messages=[chatting.ChatMessage(role="user", content=user_input)]
        )
        response = await chat.ChatResponseService.chat_response(chat_history)
        # print(response)
        
        # Store conversation in session
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("analyst", response))
        
        return response
    except Exception as e:
        st.error(f"Error in chat interaction: {str(e)}")
        return None

def display_chat_history():
    """Display the last 5 messages in chat history."""
    if st.session_state.chat_history:
        st.markdown("### Conversation History")
        for role, message in st.session_state.chat_history[-5:]:
            bubble_class = "chat-user" if role == "user" else "chat-analyst"
            display_name = "You" if role == "user" else "Analyst"
            st.markdown(
                f"<div class='chat-bubble {bubble_class}'>"
                f"<strong>{display_name}:</strong> {message}"
                f"</div>",
                unsafe_allow_html=True
            )

def display_educational_resources(ticker):
    """Display educational resources for a given ticker."""
    if not ADVANCED_FEATURES_AVAILABLE:
        st.info("Educational resources feature not available.")
        return
        
    try:
        resources = education_resources.get_finance_education_resources(ticker)
        if resources and resources.get('items'):
            st.header("📚 Educational Resources")
            for res in resources['items'][:3]:
                st.markdown(f"🔗 [{res['title']}]({res['link']})")
                st.caption(res.get('snippet', ''))
    except Exception as e:
        st.error(f"Error loading educational resources: {str(e)}")

def display_visualizations():
    """Display visualizations with robust error checking."""
    if not 'visualizations' in st.session_state or not st.session_state.visualizations:
        return
        
    with st.sidebar:
        st.header("📊 Key Visualizations")
        
        # Check for profitability visualization
        if 'profitability' in st.session_state.visualizations:
            try:
                viz_data = st.session_state.visualizations['profitability']
                if viz_data and "," in viz_data:
                    st.image(
                        base64.b64decode(viz_data.split(",")[1]), 
                        caption="Profitability Metrics"
                    )
                else:
                    st.info("Profitability visualization not available")
            except Exception as e:
                st.error(f"Error displaying visualization: {str(e)}")

def home_page():
    """Landing page for the Financial Analysis Suite."""
    st.title("📊 Financial Analysis Suite")
    st.markdown("""
    ### Welcome to Your Financial Insights Companion! 🚀

    This application provides comprehensive financial analysis for publicly traded companies. 
    Our suite offers:

    - 📈 Detailed Balance Sheet Analysis
    - 💰 Cash Flow Insights
    - 📊 Financial Performance Breakdown
    - 📋 Key Statistical Metrics
    - 📖 Company Story Generation
    - 🤖 AI-Powered Stock Analysis
    - 💬 Chat with an AI Financial Analyst

    Get started by selecting a page from the sidebar and entering a stock ticker!
    """)

    # Featured Tickers Section
    st.markdown("### 🌟 Popular Tickers")
    col1, col2, col3 = st.columns(3)
    
    featured_tickers = ["HDB", "LICI.NS", "INFY"]
    for i, ticker in enumerate(featured_tickers):
        with locals()[f"col{i+1}"]:
            if st.button(f"{ticker} - {TICKER2_MAPPING.get(ticker, ticker)}"):
                st.session_state.selected_ticker = ticker
                st.rerun()

def balance_sheet_page():
    """Page for Balance Sheet Analysis."""
    st.title("🏦 Balance Sheet Analysis")
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if st.button("Analyze Balance Sheet") and validate_ticker(ticker):
        with st.spinner("Analyzing Balance Sheet..."):
            try:
                balance_sheet.analyze_balance_sheet(ticker)
                
                # Read the generated analysis
                with open(f"{ticker}_balance_sheet_analysis.txt", "r") as file:
                    analysis = file.read()
                
                st.success(f"Balance Sheet Analysis for {TICKER2_MAPPING.get(ticker, ticker)}")
                st.markdown(analysis)
            
            except Exception as e:
                st.error(f"Error in analysis: {e}")

def cash_flow_page():
    """Page for Cash Flow Analysis."""
    st.title("💸 Cash Flow Analysis")
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if st.button("Analyze Cash Flow") and validate_ticker(ticker):
        with st.spinner("Analyzing Cash Flow..."):
            try:
                cashflow.analyze_cash_flow(ticker)
                
                # Read the generated analysis
                with open(f"{ticker}_cash_flow_analysis.txt", "r") as file:
                    analysis = file.read()
                
                st.success(f"Cash Flow Analysis for {TICKER2_MAPPING.get(ticker, ticker)}")
                st.markdown(analysis)
            
            except Exception as e:
                st.error(f"Error in analysis: {e}")

def financials_page():
    """Page for Financial Performance Analysis."""
    st.title("📈 Financial Performance")
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if st.button("Analyze Financials") and validate_ticker(ticker):
        with st.spinner("Analyzing Financial Performance..."):
            try:
                financials.analyze_financials(ticker)
                
                # Read the generated analysis
                with open(f"{ticker}_financials_analysis.txt", "r") as file:
                    analysis = file.read()
                
                st.success(f"Financial Performance Analysis for {TICKER2_MAPPING.get(ticker, ticker)}")
                st.markdown(analysis)
            
            except Exception as e:
                st.error(f"Error in analysis: {e}")

def key_stats_page():
    """Page for Key Statistics Analysis."""
    st.title("📊 Key Financial Statistics")
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if st.button("Analyze Key Statistics") and validate_ticker(ticker):
        with st.spinner("Analyzing Key Statistics..."):
            try:
                key_stats.analyze_key_stats(ticker)
                
                # Read the generated analysis
                with open(f"{ticker}_key_stats_analysis.txt", "r") as file:
                    analysis = file.read()
                
                st.success(f"Key Statistics Analysis for {TICKER2_MAPPING.get(ticker, ticker)}")
                st.markdown(analysis)
            
            except Exception as e:
                st.error(f"Error in analysis: {e}")

def company_story_page():
    """Page for Company Story Generation."""
    st.title("📖 Company Story")
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if st.button("Generate Company Story") and validate_ticker(ticker):
        with st.spinner("Generating Company Story..."):
            try:
                # Create a progress bar to show processing steps
                progress_bar = st.progress(0)
                
                # Run the analysis functions one by one with progress updates
                try:
                    st.info("Analyzing balance sheet...")
                    balance_sheet.analyze_balance_sheet(ticker)
                    progress_bar.progress(20)
                except Exception as e:
                    st.warning(f"Balance sheet analysis failed: {str(e)}")
                
                try:
                    st.info("Analyzing cash flow...")
                    cashflow.analyze_cash_flow(ticker)
                    progress_bar.progress(40)
                except Exception as e:
                    st.warning(f"Cash flow analysis failed: {str(e)}")
                
                try:
                    st.info("Analyzing financials...")
                    financials.analyze_financials(ticker)
                    progress_bar.progress(60)
                except Exception as e:
                    st.warning(f"Financial analysis failed: {str(e)}")
                
                try:
                    st.info("Analyzing key statistics...")
                    key_stats.analyze_key_stats(ticker)
                    progress_bar.progress(80)
                except Exception as e:
                    st.warning(f"Key statistics analysis failed: {str(e)}")
                
                # Generate the company story
                st.info("Generating final company story...")
                story_tell.generate_company_story(ticker)
                progress_bar.progress(100)
                
                # Check possible file paths
                possible_paths = [
                    f"{ticker}_company_story.txt",
                    f"backend/Analysis/{ticker}_company_story.txt",
                    f"Analysis/{ticker}_company_story.txt"
                ]
                
                story = None
                for path in possible_paths:
                    try:
                        with open(path, "r") as file:
                            story = file.read()
                            break
                    except FileNotFoundError:
                        continue
                
                if story:
                    st.success(f"Company Story for {TICKER2_MAPPING.get(ticker, ticker)}")
                    st.markdown(story)
                else:
                    st.error(f"Could not find company story file for {ticker}. Please check file paths.")
                
            except Exception as e:
                st.error(f"Error generating story: {str(e)}")
                # Add more debug info
                import traceback
                st.expander("Error Details").code(traceback.format_exc())

def ai_analysis_page():
    """Page for AI-Powered Stock Analysis."""
    st.title("🤖 AI-Powered Stock Analysis")
    
    if not ADVANCED_FEATURES_AVAILABLE:
        st.warning("Advanced AI features are not available. Make sure you have the necessary modules installed.")
        return
    
    st.markdown("""
    This feature uses advanced artificial intelligence to generate comprehensive stock analysis 
    including financial reports, technical analysis, and business overviews.
    """)
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if st.button("Generate AI Analysis") and validate_ticker(ticker):
        with st.spinner("🧠 Generating comprehensive analysis..."):
            result = generate_analysis(ticker)
            if result:
                st.session_state.analyses = result['analyses']
                st.session_state.visualizations = result['visualizations']
                st.session_state.current_ticker = ticker
                st.success("Analysis completed!")
                
                # Display analysis in tabs
                tab1, tab2, tab3 = st.tabs(["Financial Analysis", "Business Overview", "Technical Analysis"])
                
                with tab1:
                    st.markdown(st.session_state.analyses.get('financials', 'No financial analysis available'), unsafe_allow_html=True)
                    if st.session_state.visualizations.get('revenue_growth'):
                        try:
                            viz_data = st.session_state.visualizations['revenue_growth']
                            if viz_data and "," in viz_data:
                                st.image(
                                    base64.b64decode(viz_data.split(",")[1]), 
                                    caption="Revenue Growth Trend"
                                )
                        except Exception as e:
                            st.error(f"Error displaying visualization: {str(e)}")
                
                with tab2:
                    st.markdown(st.session_state.analyses.get('business', 'No business analysis available'), unsafe_allow_html=True)
                
                with tab3:
                    st.markdown(st.session_state.analyses.get('technical', 'No technical analysis available'), unsafe_allow_html=True)
                    if st.session_state.visualizations.get('stock_price'):
                        try:
                            viz_data = st.session_state.visualizations['stock_price']
                            if viz_data and "," in viz_data:
                                st.image(
                                    base64.b64decode(viz_data.split(",")[1]), 
                                    caption="Stock Price Movement"
                                )
                        except Exception as e:
                            st.error(f"Error displaying visualization: {str(e)}")
                
                # Display educational resources if available
                display_educational_resources(ticker)
# Fix the chat_page function - make it non-async and handle async calls properly
def chat_page():
    """Page for AI Financial Analyst Chat."""
    st.title("💬 Chat with AI Financial Analyst")
    
    if not ADVANCED_FEATURES_AVAILABLE:
        st.warning("Advanced AI chat features are not available. Make sure you have the necessary modules installed.")
        return
    
    st.markdown("""
    Have a conversation with our AI Financial Analyst. Ask questions about any publicly traded company, 
    and get expert insights and explanations.
    """)
    
    ticker = get_ticker_dropdown(st.session_state.get('selected_ticker', ''))
    
    if not ticker:
        st.warning("Please select a stock ticker to start the conversation.")
        return
    
    # Set current ticker
    st.session_state.current_ticker = ticker
    
    # Initialize chat history if needed
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display current company
    st.info(f"Currently analyzing: {ticker} - {TICKER2_MAPPING.get(ticker, ticker)}")
    
    # Generate initial analysis if needed
    if 'analyses' not in st.session_state or not st.session_state.analyses:
        if st.button("Generate Initial Analysis"):
            with st.spinner("Generating background analysis..."):
                result = generate_analysis(ticker)
                if result:
                    st.session_state.analyses = result['analyses']
                    st.session_state.visualizations = result['visualizations']
                    st.success(f"Initial analysis for {ticker} completed! You can now ask questions.")
    
    # Chat interface
    user_input = st.text_input("Ask your question:", key="ai_chat_input")
    
    if st.button("Send") and user_input:
        with st.spinner("💡 Analyzing..."):
            # Note: we're using asyncio.run to handle the async function
            if ADVANCED_FEATURES_AVAILABLE:
                try:
                    # Add user message to history first
                    # st.session_state.chat_history.append(("user", user_input))
                    
                    # Run the async function
                    response = asyncio.run(handle_chat_interaction(ticker, user_input))
                    
                    # If response was handled by the function, we don't need to add it again
                    # The function already adds it to chat_history
                    
                    st.success("Response generated!")
                    st.rerun()  # Force a rerun to show the updated chat
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    # Add a fallback response
                    fallback = f"I apologize, but I encountered a technical issue. Please try again with a different question."
                    st.session_state.chat_history.append(("analyst", fallback))
            else:
                # Fallback for when advanced features aren't available
                st.session_state.chat_history.append(("user", user_input))
                fallback = f"I'm a simulated financial analyst. The advanced AI features aren't available currently."
                st.session_state.chat_history.append(("analyst", fallback))
                st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Conversation")
        for i, (role, message) in enumerate(st.session_state.chat_history):
            if role == "user":
                # st.markdown(f"""
                # <div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: right;">
                #     <strong>You:</strong> {message}
                # </div>
                # """, unsafe_allow_html=True)
                st.markdown(message)
            else:
                # st.markdown(f"""
                # <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                #     <strong>Financial Analyst:</strong> {message}
                # </div>
                # """, unsafe_allow_html=True)
                st.markdown(message)
    else:
        st.info("No conversation yet. Ask a question to get started!")

# Fix the main function - make it non-async
def main():
    # Initialize session state
    initialize_session_state()
    
    # Check for API key at startup
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.sidebar.error("⚠️ GROQ_API_KEY not found in environment variables. Please set this up in your .env file.")
    
    # Sidebar navigation with additional options
    with st.sidebar:
        selected = option_menu(
            menu_title="Financial Analysis Suite",
            options=[
                "Home", 
                "Balance Sheet", 
                "Cash Flow", 
                "Financials", 
                "Key Statistics", 
                "Company Story",
                "AI Analysis", 
                "Chat Assistant"
            ],
            icons=[
                'house', 
                'bank', 
                'cash-coin', 
                'graph-up', 
                'calculator', 
                'book',
                'robot',
                'chat-dots'
            ],
            default_index=0,
        )
    
    # Page routing
    if selected == "Home":
        home_page()
    elif selected == "Balance Sheet":
        balance_sheet_page()
    elif selected == "Cash Flow":
        cash_flow_page()
    elif selected == "Financials":
        financials_page()
    elif selected == "Key Statistics":
        key_stats_page()
    elif selected == "Company Story":
        company_story_page()
    elif selected == "AI Analysis":
        ai_analysis_page()
    elif selected == "Chat Assistant":
        chat_page()  # No longer async

if __name__ == "__main__":
    main()  # Regular function call, not async