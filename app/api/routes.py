from fastapi import APIRouter, HTTPException, Query
from app.services.market_data import MarketDataService
from app.models.schemas import PriceResponse, AnalysisResponse, CompareResponse

router = APIRouter()
service = MarketDataService()


@router.get("/price/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str):
    try:
        return await service.get_price(symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analysis/{symbol}", response_model=AnalysisResponse)
async def get_analysis(
    symbol: str,
    days: int = Query(60, ge=30, le=90, description="Number of days for historical data")
):
    try:
        return await service.get_analysis(symbol, days)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/compare", response_model=CompareResponse)
async def compare_coins(
    symbols: str = Query(..., description="Comma-separated symbols (example: BTC,ETH,SOL)")
):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    
    if not symbol_list:
        raise HTTPException(status_code=400, detail="At least one symbol is required")
    
    if len(symbol_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 symbols allowed")
    
    return await service.compare(symbol_list)