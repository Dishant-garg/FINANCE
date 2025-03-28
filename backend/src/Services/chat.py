import os
import google.generativeai as genai
from src.Models.chat import ChatHistory, ChatMessage
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

class ChatResponseService:
    ANALYSIS_TYPES = {
        'financials': '_financials_analysis.txt',
        'balance_sheet': '_balance_sheet_analysis.txt',
        'cash_flow': '_cash_flow_analysis.txt'
    }

    @staticmethod
    def read_analysis_files(company: str) -> Dict[str, str]:
        """Read all analysis files for a given company."""
        analysis_contents = {}
        base_path = './Analysis'
        
        for analysis_type, file_suffix in ChatResponseService.ANALYSIS_TYPES.items():
            file_path = f"{base_path}/{company}{file_suffix}"
            try:
                with open(file_path, 'r') as file:
                    analysis_contents[analysis_type] = file.read()
            except FileNotFoundError:
                print(f"Warning: {file_path} not found")
                analysis_contents[analysis_type] = f"No {analysis_type} analysis available."
        
        return analysis_contents

    @staticmethod
    async def chat_response(chat_history: ChatHistory) -> str:
        try:
            # Read all analysis files for the company
            analyses = ChatResponseService.read_analysis_files(chat_history.company)
            
            # Combine all analyses into a comprehensive document
            combined_analysis = "\n\n".join([
                f"### {analysis_type.upper()} ANALYSIS:\n{content}" 
                for analysis_type, content in analyses.items()
            ])

            # Convert chat history to text format
            chat_text = "\n\n".join([
                f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
                for msg in chat_history.messages
            ])

            # Create the enhanced prompt with instructions for simpler responses
            prompt = f"""
            Context:
            You are a friendly financial advisor explaining {chat_history.company}'s financial information to a regular person who might not be familiar with complex financial terms.

            Document Analyses:
            {combined_analysis}

            Previous Conversation:
            {chat_text}

            Instructions:
            1. Use simple, everyday language as if explaining to a friend
            2. Provide real-world analogies (e.g., compare business concepts to personal finance)
            3. Break down complex financial terms with easy-to-understand explanations
            4. Use relatable comparisons for large numbers
            5. Focus on practical implications for investors
            6. Keep responses clear and concise
            7. Format your response using Markdown for better readability
            8. If you mention any financial term, explain it in parentheses right after

            Please respond to the last user message following these guidelines.
            """

            # Generate response using the complete prompt
            response = await model.generate_content_async(prompt)
            
            if not response.text:
                return "I apologize, but I couldn't generate a response."
            
            return response.text

        except Exception as e:
            raise Exception(f"Error in chat response: {str(e)}")