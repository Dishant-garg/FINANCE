import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_balance_sheet(ticker):
    # Get API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please set this up.")
    
    desired_metrics = [
        "Treasury Shares",
        "Ordinary Shares",
        "Total Debt",
        "Tangible Book Value",
        "Working Capital",
        "Retained Earnings",
        "Goodwill",
        "Net PPE",
        "Accounts Receivable",
        "Cash and Cash Equivalents",
    ]

    try:
        # Load balance sheet data from CSV file
        csv_file_path = f"FINANCE/backend/Data/company_data/{ticker}/balance_sheet.csv"
        
        try:
            df = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            error_msg = f"Error: Could not find balance sheet data file for {ticker}. Please ensure the file exists at {csv_file_path}"
            print(error_msg)
            
            # Create an error file instead
            output_file_path = f"{ticker}_balance_sheet_analysis.txt"
            with open(output_file_path, "w") as file:
                file.write(f"# Analysis Error\n\n{error_msg}")
            
            raise FileNotFoundError(error_msg)

        # Filter relevant metrics and convert to dictionary format
        filtered_df = df[df.iloc[:, 0].isin(desired_metrics)]
        csv_data = filtered_df.set_index(filtered_df.columns[0]).to_dict()[
            filtered_df.columns[1]
        ]

        # Initialize the Groq client with the API key from environment variables
        client = Groq(api_key=api_key)

        # Define prompt for AI analysis
        bs_prompt = """
        You are a financial expert who explains things in a simple, easy-to-understand way. Given the balance sheet of a company, analyze it and provide clear insights into the company's financial health and future prospects. Avoid technical jargon and use everyday language so that someone without a finance background can understand.

        ### Key Areas to Analyze:

        #### 1. Short-Term Financial Health (Can the Company Pay Its Bills?)
        - Look at **Cash and Cash Equivalents** to see if the company has enough money available to cover immediate expenses.
        - Check **Working Capital** to determine if short-term assets are enough to meet short-term liabilities. A negative value could signal financial trouble.
        - Analyze **Short-Term Investments** to see if the company has liquid assets that can be quickly converted into cash if needed.

        #### 2. Debt and Risk (Is the Company Borrowing Too Much?)
        - Compare **Total Debt** and **Net Debt** to understand how much the company owes and whether it has enough cash to cover its debts.
        - Identify if the company's debt levels are sustainable or could lead to financial problems in the future.

        #### 3. Profitability and Growth (Is the Company Building Long-Term Value?)
        - Look at **Tangible Book Value** to assess the real value of the company's assets.
        - Check **Invested Capital** to see how much money has been put into the business for growth and expansion.
        - Analyze **Accounts Receivable** to determine if the company is collecting money from customers on time or facing delays in payments.

        #### 4. Inventory and Resource Management (Is the Company Using Resources Efficiently?)
        - Look at **Finished Goods, Work-in-Process, and Raw Materials** to understand how well the company is managing its inventory.
        - Identify if the company has excess stock, which could tie up cash and hurt profitability.

        #### 5. Warning Signs (Are There Any Red Flags?)
        - Check **Other Receivables & Taxes Receivable** to see if the company is struggling to collect payments.
        - Analyze **Net Tangible Assets** to determine if the company's core assets are losing value.
        - Identify any decline in **Short-Term Investments**, which might indicate that the company is selling assets to stay afloat.

        #### 6. Industry Comparison (How Does the Company Compare to Others?)
        - See if the company's debt, cash reserves, and asset management are stronger or weaker than competitors.
        - Highlight strengths and weaknesses compared to similar companies in the industry.

        #### 7. Future Outlook (What Does the Future Look Like?)
        - Based on past trends in **cash flow, debt, and asset growth**, predict whether the company is in a strong or risky position.
        - Offer simple suggestions on how the company can maintain financial stability or improve performance.

        ### Final Output:
        Present a simple, clear, and practical breakdown of the company's financial position. Use real-world comparisons, everyday examples, and avoid technical terms so that anyone can understand. Make it easy for someone with no finance background to know whether the company is in good shape or facing trouble.
        """

        # Make API call to analyze balance sheet data
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": bs_prompt},
                {"role": "user", "content": str(csv_data)},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Extract and save AI-generated insights
        final_output_balance = chat_completion.choices[0].message.content
        output_file_path = f"{ticker}_balance_sheet_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(final_output_balance)

        print(f"Balance sheet analysis for {ticker} completed successfully")
        return True
        
    except Exception as e:
        error_msg = f"Error analyzing balance sheet for {ticker}: {str(e)}"
        print(error_msg)
        
        # Create an error file instead
        output_file_path = f"{ticker}_balance_sheet_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(f"# Analysis Error\n\n{error_msg}")
        
        raise