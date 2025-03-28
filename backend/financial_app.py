import streamlit as st
import base64
import asyncio
from datetime import datetime,timedelta

# Example imports (you'll use your own modules)
from src.Services import article_generator, chat, education_resources, viz
from src.Models import chat as chatting

# Configure page settings
st.set_page_config(
    page_title="Financial Analysis Suite",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize all necessary session state variables."""
    # Initialize with default empty values
    default_states = {
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
    try:
        # Use asyncio.run to handle async functions
        analyses = asyncio.run(article_generator.ArticleGeneratorService.generate_company_analysis(ticker))
        visualizations = asyncio.run(viz.VisualizationService.get_stock_visualizations(ticker))
        
        return {
            'analyses': analyses,
            'visualizations': visualizations
        }
    except Exception as e:
        st.error(f"Error generating analysis for {ticker}: {str(e)}")
        return None

def handle_chat_interaction(ticker, user_input):
    """Handle chat interaction with error logging."""
    try:
        chat_history = chatting.ChatHistory(
            company=ticker,
            messages=[chatting.ChatMessage(role="user", content=user_input)]
        )
        response = chat.ChatResponseService.chat_response(chat_history)
        
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
    with st.sidebar:
        st.header("📊 Key Visualizations")
        
        # Check for profitability visualization
        if 'profitability' in st.session_state.visualizations:
            try:
                st.image(
                    base64.b64decode(
                        st.session_state.visualizations['profitability'].split(",")[1]
                    ), 
                    caption="Profitability Metrics"
                )
            except Exception as e:
                st.error(f"Error displaying profitability visualization: {str(e)}")

def main():
    # Initialize session state
    initialize_session_state()

    st.title("📊 Financial Analysis Suite")

    # Sidebar controls
    with st.sidebar:
        st.header("🔍 Analysis Controls")
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):", key="ticker").upper()
        
        if st.button("Generate Analysis", key="generate"):
            if ticker:
                with st.spinner("🧠 Generating comprehensive analysis..."):
                    result = generate_analysis(ticker)
                    if result:
                        st.session_state.analyses = result['analyses']
                        st.session_state.visualizations = result['visualizations']
                        st.session_state.current_ticker = ticker
                        st.success("Analysis completed!")
            else:
                st.warning("Please enter a valid stock ticker.")

        st.markdown("---")
        st.header("💬 Chat with Analyst")
        user_input = st.text_input("Ask a question about the company:", key="chat_input")
        
        if user_input and st.session_state.current_ticker:
            with st.spinner("💡 Thinking..."):
                handle_chat_interaction(st.session_state.current_ticker, user_input)
        elif user_input:
            st.warning("Please generate an analysis first.")

        # Display chat history
        display_chat_history()

    # Main content area
    if st.session_state.analyses:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(f"📄 {st.session_state.current_ticker} Analysis Reports")
            
            # Create tabs for different analyses
            tab1, tab2, tab3 = st.tabs(["Financial Analysis", "Business Overview", "Technical Analysis"])
            
            with tab1:
                st.markdown(st.session_state.analyses.get('financials', ''), unsafe_allow_html=True)
                if st.session_state.visualizations.get('revenue_growth'):
                    try:
                        st.image(
                            base64.b64decode(
                                st.session_state.visualizations['revenue_growth'].split(",")[1]
                            ), 
                            caption="Revenue Growth Trend"
                        )
                    except Exception as e:
                        st.error(f"Error displaying revenue growth visualization: {str(e)}")
                
            with tab2:
                st.markdown(st.session_state.analyses.get('business', ''), unsafe_allow_html=True)
                
            with tab3:
                st.markdown(st.session_state.analyses.get('technical', ''), unsafe_allow_html=True)
                if st.session_state.visualizations.get('stock_price'):
                    try:
                        st.image(
                            base64.b64decode(
                                st.session_state.visualizations['stock_price'].split(",")[1]
                            ), 
                            caption="Stock Price Movement"
                        )
                    except Exception as e:
                        st.error(f"Error displaying stock price visualization: {str(e)}")

        with col2:
            # Display key visualizations
            display_visualizations()
           
            # Display educational resources
            display_educational_resources(st.session_state.current_ticker)

    else:
        # Fallback when no ticker is provided or no analysis is generated
        st.markdown(
            """
            <div style='text-align: center; padding: 50px;'>
                <h3>Welcome to Financial Analysis Suite! 🚀</h3>
                <p>Enter a stock ticker in the sidebar to get started!</p>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()