import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_key_stats(ticker):
    # Get API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please set this up.")
    
    # Define the AI prompt for key statistics analysis
    prompt = """
    You are a financial analyst who explains company financial health in simple, everyday language. Given the key financial statistics of a company, analyze them and provide clear insights into the company's future performance, risks, and investment potential. Avoid technical jargon and use practical comparisons to make the analysis easy to understand.
    
    ### Key Areas to Analyze:
    
    #### 1. Market Valuation (How Much is the Company Worth?)
    - Examine **Market Capitalization and Enterprise Value** to understand the company's overall market size and investor perception.
    
    #### 2. Profitability (Is the Company Generating Sustainable Profits?)
    - Analyze **Revenue, Gross Profit, Net Income, and EBITDA** to assess the company's ability to generate earnings.
    
    #### 3. Efficiency (How Well is the Company Managing Costs?)
    - Look at **Operating Margin, Profit Margin, Return on Assets (ROA), and Return on Equity (ROE)** to determine if the company is maximizing profits efficiently.
    
    #### 4. Financial Stability (Is the Company at Risk?)
    - Review **Debt-to-Equity Ratio, Current Ratio, Quick Ratio, and Interest Coverage Ratio** to understand how well the company manages its debts and financial obligations.
    
    #### 5. Growth Potential (Will the Company Expand?)
    - Examine **Revenue Growth and Earnings Per Share (EPS) Growth** to determine if the company is growing and increasing shareholder value.
    
    #### 6. Stock Performance (How Attractive is the Company for Investors?)
    - Assess **Price-to-Earnings (P/E) Ratio, Price-to-Book (P/B) Ratio, Dividend Yield, and Beta** to evaluate stock valuation, investor returns, and risk levels.
    
    ### Final Output:
    Provide a clear and concise summary of the company's financial health. Highlight its strengths, weaknesses, and future potential in a way that is easy for a non-expert to understand. Help them decide if the company is financially strong, risky, or a good investment opportunity.
    """

    try:
        # Build the file path for the key statistics CSV file using the ticker
        csv_file_path = f"Data/company_data/{ticker}/company_info.csv"

        # Load the key statistics data from the CSV file
        df = pd.read_csv(csv_file_path)

        # Convert the data to a dictionary with metric names as keys and their corresponding values
        csv_data = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

        # Initialize the Groq client with the API key
        client = Groq(api_key=api_key)

        # Make the API call to analyze the key statistics data using the provided prompt
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
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
        final_output_keystats = chat_completion.choices[0].message.content

        # Save the analysis to a file named using the ticker
        output_file_path = f"{ticker}_key_stats_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(final_output_keystats)

        print(f"Key stats analysis for {ticker} completed successfully")
        return True
        
    except FileNotFoundError:
        error_msg = f"Error: Could not find data file for {ticker}. Please ensure the file exists at {csv_file_path}"
        print(error_msg)
        
        # Create an error file instead
        output_file_path = f"{ticker}_key_stats_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(f"# Analysis Error\n\n{error_msg}")
        
        raise FileNotFoundError(error_msg)
        
    except Exception as e:
        error_msg = f"Error analyzing key stats for {ticker}: {str(e)}"
        print(error_msg)
        
        # Create an error file instead
        output_file_path = f"{ticker}_key_stats_analysis.txt"
        with open(output_file_path, "w") as file:
            file.write(f"# Analysis Error\n\n{error_msg}")
        
        raise