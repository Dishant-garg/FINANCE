from fastapi import APIRouter, HTTPException
from src.Services.article_generator import ArticleGeneratorService
import os

router = APIRouter()

@router.post("/article/{companyTicker}")
async def generate_and_read_analysis(companyTicker: str):
    try:
        # Generate new analysis
        await ArticleGeneratorService.generate_company_analysis(companyTicker)
        
        # Read generated files
        base_path = './Analysis'
        analysis_files = {}
        
        files = os.listdir(base_path)
        company_files = [f for f in files if f.startswith(companyTicker)]
        
        if not company_files:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis files generated for company {companyTicker}"
            )
        
        for file_name in company_files:
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