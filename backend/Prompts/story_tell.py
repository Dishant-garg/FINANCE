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
        You are a financial storyteller who transforms complex financial analyses into engaging, easy-to-understand narratives. Given multiple financial analyses for a company, create a cohesive company story that captures its financial journey, current position, and future outlook.

        ### Your Task:
        1. Synthesize the various analyses into a flowing narrative.
        2. Highlight key strengths, challenges, and opportunities facing the company.
        3. Use concrete examples and real-world comparisons to explain financial concepts.
        4. Avoid technical jargon - write as if explaining to someone with no financial background.
        5. Create a story with a clear beginning (company history and past performance), middle (current financial health), and end (future outlook).

        ### Story Structure:
        - **Introduction**: Brief overview of the company and why it matters to investors.
        - **Financial Journey**: How the company has managed its finances over time.
        - **Current Position**: The company's financial health right now, highlighting strengths and weaknesses.
        - **Growth Story**: The company's potential for future expansion and areas of opportunity.
        - **Risk Narrative**: Key challenges and threats the company faces.
        - **Conclusion**: Final assessment of the company as an investment opportunity.

        ### Guidelines:
        - Be honest about both strengths and weaknesses.
        - Use storytelling techniques like metaphors, analogies, and examples.
        - Focus on the most important insights rather than listing every detail.
        - Create a balanced view that helps readers form their own opinion.
        - Write in a conversational, engaging tone.

        The final output should read like an engaging article that anyone can understand, bringing financial numbers to life through storytelling.
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