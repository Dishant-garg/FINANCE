from fastapi import APIRouter, HTTPException
from src.Models.chat import ChatHistory, ChatMessage
from src.Services.chat import ChatResponseService
import os
from typing import Dict, List

router = APIRouter()

@router.post("/story/{companyTicker}")
async def read_analysed_files(companyTicker: str):
    """
    Reads all analysis files for a given company ticker from the Analysis directory.
    
    Args:
        companyTicker (str): The company ticker symbol (e.g., 'HDB', 'INFY')
        
    Returns:
        Dict[str, str]: Dictionary containing analysis type and content
        
    Raises:
        HTTPException: If no files found for the company or if there's an error
    """
    try:
        base_path = './Analysis'
        analysis_files = {}
        
        # Get all files in Analysis directory
        files = os.listdir(base_path)
        
        # Filter files that start with the company ticker
        company_files = [f for f in files if f.startswith(companyTicker)]
        
        if not company_files:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis files found for company {companyTicker}"
            )
        
        # Read content of each file
        for file_name in company_files:
            # Extract analysis type from filename (e.g., 'financials' from 'HDB_financials_analysis.txt')
            analysis_type = file_name.split('_')[1].replace('_analysis.txt', '')
            
            file_path = os.path.join(base_path, file_name)
            try:
                with open(file_path, 'r') as file:
                    analysis_files[analysis_type] = file.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")
                continue
        
        return {
            "company": companyTicker,
            "analyses": analysis_files
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )