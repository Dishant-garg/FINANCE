import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_cash_flow(ticker):
    # Get API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please set this up.")
    
    try:
        # Define the AI prompt for cash flow analysis
        cf_prompt = """
        You are a financial expert who explains company financial health in simple, everyday language. Given the cash flow statement of a company, analyze it and provide clear insights into its financial stability and future prospects. Avoid technical jargon and use real-world comparisons to make it easy for anyone to understand.

        ### Key Areas to Analyze:

        #### 1. Cash Flow Sustainability (Can the Company Sustain Itself?)
        - Look at **Free Cash Flow (FCF)** to see if the company has money left after expenses. A positive FCF means the company can grow, pay off debt, or return value to shareholders. A negative FCF might indicate financial struggles.

        #### 2. Debt and Financial Risk (Is the Company Overburdened?)
        - Check **Debt Repayments vs. New Borrowings** to see if the company is reducing or increasing its debt. A company constantly borrowing more money could be in financial trouble.

        #### 3. Investment in Growth (Is the Company Expanding?)
        - Look at **Capital Expenditure (CapEx)** to determine if the company is reinvesting in new projects, facilities, or technology. If CapEx is low, the company might not be investing in its future.

        #### 4. Liquidity (Does the Company Have Enough Cash to Operate?)
        - Analyze **End Cash Position and Changes in Cash** to check if the company has enough liquidity to handle its expenses. A declining cash position could mean financial stress.

        #### 5. Profitability (Is the Business Generating Enough Cash?)
        - Look at **Net Income from Continuing Operations** to assess how profitable the core business activities are. If income is growing but cash flow is declining, the company might struggle to collect payments.

        #### 6. Operational Efficiency (Is the Company Managing Finances Well?)
        - Check **Changes in Inventory and Receivables** to see if the company is overproducing products or having trouble collecting payments from customers.

        #### 7. Asset Depreciation (How Much Value Is Being Lost?)
        - Look at **Depreciation and Amortization** to understand how the company's assets are losing value over time. High depreciation can reduce profits but might provide tax benefits.

        #### 8. Employee Compensation Strategy (Is the Company Relying on Stock Payments?)
        - Analyze **Stock-Based Compensation** to determine if the company is paying employees with stock instead of cash. Too much stock-based compensation can reduce shareholder value.

        #### 9. Currency Risks (Is Foreign Exchange Impacting the Company?)
        - Check **Net Foreign Currency Exchange Gains/Losses** to see if international operations are affecting financial performance.

        ### Final Output:
        Provide a simple and easy-to-understand summary of the company's cash flow situation. Highlight strengths, weaknesses, and risks using practical, non-technical explanations. Help an everyday person determine whether the company is financially stable or facing challenges.
        """

        # Define important cash flow metrics
        important_metrics_cash_flow = [
            "Free Cash Flow",
            "Operating Cash Flow",
            "End Cash Position",
            "Beginning Cash Position",
            "Capital Expenditure",
            "Purchase Of PPE",
            "Net Business Purchase And Sale",
            "Sale Of Investment",
            "Repayment Of Debt",
            "Cash Dividends Paid",
            "Repurchase Of Capital Stock",
            "Changes In Working Capital",
            "Change In Receivables",
            "Depreciation And Amortization",
            "Net Income From Continuing Operations",
            "Gain Loss On Sale Of Business",
            "Effect Of Exchange Rate Changes",
        ]

        # Build file path for the cash flow CSV file using the ticker
        csv_file_path = f"Data/company_data/{ticker}/cash_flow.csv"
        
        try:
            df = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            error_msg = f"Error: Could not find cash flow data file for {ticker}. Please ensure the file exists at {csv_file_path}"
            print(error_msg)
            
            # Create an error file instead
            output_file_path = f"{ticker}_cash_flow_analysis.txt"
            with open(output_file_path, "w") as file:
                file.write(f"# Analysis Error\n\n{error_msg}")
            
            raise FileNotFoundError(error_msg)

        # Filter the DataFrame to keep only the desired metrics and convert it to a dictionary
        filtered_df = df[df.iloc[:, 0].isin(important_metrics_cash_flow)]
        csv_data = filtered_df.set_index(filtered_df.columns[0]).to_dict()[filtered_df.columns[1]]
        
        # Initialize the Groq client with the API key from environment variables
        client = Groq(api_key=api_key)
        
        # Make the API call to analyze the cash flow data using the defined prompt
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": cf_prompt},
                {"role": "user", "content": str(csv_data)},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        
        # Extract the AI-generated insights from the API response
        final_output_cashflow = chat_completion.choices[0].message.content
        
        # Save the analysis to a file named using the ticker
        output_file_path = f"{ticker}_cash_flow_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(final_output_cashflow)
        
        print(f"Cash flow analysis for {ticker} completed successfully")
        return True
        
    except Exception as e:
        error_msg = f"Error analyzing cash flow for {ticker}: {str(e)}"
        print(error_msg)
        
        # Create an error file instead
        output_file_path = f"{ticker}_cash_flow_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(f"# Analysis Error\n\n{error_msg}")
        
        raise