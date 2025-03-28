from fastapi import APIRouter, HTTPException
from src.Services.viz import VisualizationService
from typing import Dict, Any

router = APIRouter()

@router.get("/visualize/{ticker}")
async def get_company_visualizations(ticker: str) -> Dict[str, Any]:
    """
    Get interactive visualizations for a company's financial data
    
    Args:
        ticker (str): Company stock ticker symbol
        
    Returns:
        Dict containing various visualizations and metrics
    """
    try:
        visualizations = await VisualizationService.get_stock_visualizations(ticker)
        return {
            "status": "success",
            "company": ticker,
            "visualizations": visualizations
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )