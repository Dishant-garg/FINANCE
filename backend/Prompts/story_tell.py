import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_company_story(ticker):
    # Get API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please set this up.")
    
    try:
        # Read the individual analysis files
        balance_sheet_file = f"{ticker}_balance_sheet_analysis.txt"
        cash_flow_file = f"{ticker}_cash_flow_analysis.txt"
        financials_file = f"{ticker}_financials_analysis.txt"
        key_stats_file = f"{ticker}_key_stats_analysis.txt"
        
        # Initialize combined analysis
        combined_analysis = ""
        
        # Check and read each file if it exists
        for file_name, section_title in [
            (balance_sheet_file, "Balance Sheet Analysis"),
            (cash_flow_file, "Cash Flow Analysis"),
            (financials_file, "Financial Performance Analysis"),
            (key_stats_file, "Key Statistics Analysis")
        ]:
            try:
                with open(file_name, "r") as file:
                    combined_analysis += f"\n\n## {section_title}\n\n"
                    combined_analysis += file.read()
            except FileNotFoundError:
                print(f"Warning: Could not find {file_name}")
                combined_analysis += f"\n\n## {section_title}\n\n"
                combined_analysis += f"Analysis not available for {ticker}."
        
        # Define the AI prompt for storytelling
        story_prompt = """
        You are a financial analyst who explains company performance in a simple, engaging storytelling format. Given a company's financial data, generate a compelling story that highlights its rise, challenges, and future outlook in a way that is easy to understand. Avoid technical jargon and focus on clear, real-world comparisons.

    ### Structure of the Story:

    #### 1. **The Rise and Challenges of {ticker_mapping.get(ticker, ticker)}**
    - Introduce the company, its founders, and its early success.
    - Highlight its rapid growth and how it gained investor and customer confidence.
    - Set up the premise of challenges that emerged despite its success.

    #### 2. **The Growth Strategy: Risky or Rewarding?**
    - Analyze whether the company’s growth is sustainable or overly aggressive.
    - Compare its revenue growth and market presence to industry averages.

    ✅ **What Went Well:**  
    - Strong revenue growth, expanding market presence, increasing investor confidence.

    ❌ **Red Flags:**  
    - High debt levels or over-reliance on risky sectors.  
    - Aggressive expansion strategies that may backfire.

    #### 3. **Financial Stability & Warning Signs**
    - Evaluate if reported financials match reality or if warning signs exist.
    - Analyze how the company manages bad loans, debt, and financial risks.

    ✅ **What Went Well:**  
    - Strong reported earnings, low declared bad loans.

    ❌ **Red Flags:**  
    - Frequent loan restructuring instead of recognizing losses.  
    - Low reserves for bad loans compared to industry standards.  

    #### 4. **Leadership & Governance Issues**
    - Assess whether leadership decisions support long-term stability.
    - Identify governance concerns, management turnover, and oversight weaknesses.

    ✅ **What Went Well:**  
    - Strong leadership presence, ambitious expansion.

    ❌ **Red Flags:**  
    - Over-concentration of power in leadership.  
    - High turnover in senior management, indicating instability.

    #### 5. **Revenue & Profitability Trends**
    - Evaluate the company’s income sources and profitability trends.
    - Identify whether earnings are sustainable or artificially inflated.

    ✅ **What Went Well:**  
    - Consistent revenue growth, positive quarterly earnings.

    ❌ **Red Flags:**  
    - Over-reliance on non-core income like fees and commissions.  
    - Declining profit margins in core business operations.

    #### 6. **Market Perception & Investor Confidence**
    - Examine investor sentiment, stock performance, and financial stability.
    - Highlight discrepancies between stock valuation and actual financial health.

    ✅ **What Went Well:**  
    - Strong stock market valuation, optimistic investor sentiment.

    ❌ **Red Flags:**  
    - High promoter pledging of shares, indicating financial stress.  
    - Stock price may be overvalued compared to real financial health.

    ### **Final Verdict**
    - Conclude whether the company is truly strong or facing hidden risks.
    - Provide an overall assessment of financial stability, governance, and risk management.

    📌 **Key Takeaway:** Investors should focus beyond headline growth and assess financial discipline, governance, and risk before making investment decisions.
   
        """
        
        # Initialize the Groq client with the API key from environment variables
        client = Groq(api_key=api_key)
        
        # Make the API call to generate the company story
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": story_prompt},
                {"role": "user", "content": combined_analysis},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=1500,
            top_p=1,
            stop=None,
            stream=False,
        )
        
        # Extract the AI-generated story
        final_story = chat_completion.choices[0].message.content
        
        # Create directory if it doesn't exist
        os.makedirs("Analysis", exist_ok=True)
        
        # Save the story to files in different locations to ensure it can be found
        output_file_paths = [
            f"{ticker}_company_story.txt",
            f"Analysis/{ticker}_company_story.txt",
            f"backend/Analysis/{ticker}_company_story.txt"
        ]
        
        for path in output_file_paths:
            try:
                # Create directory if needed
                os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
                
                # Write the file
                with open(path, "w") as file:
                    file.write(final_story)
            except Exception as e:
                print(f"Warning: Could not save to {path}: {str(e)}")
        
        print(f"Company story for {ticker} generated successfully")
        return True
        
    except Exception as e:
        error_msg = f"Error generating company story for {ticker}: {str(e)}"
        print(error_msg)
        
        # Create an error file instead
        output_file_paths = [
            f"{ticker}_company_story.txt",
            f"Analysis/{ticker}_company_story.txt",
            f"backend/Analysis/{ticker}_company_story.txt"
        ]
        
        for path in output_file_paths:
            try:
                os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
                with open(path, "w") as file:
                    file.write(f"# Analysis Error\n\n{error_msg}")
            except Exception:
                pass
        
        raise