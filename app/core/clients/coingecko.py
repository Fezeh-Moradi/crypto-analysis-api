import httpx
from loguru import logger
from app.config import get_settings

settings = get_settings()


class CoinGeckoClient:
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.timeout = 15.0

    async def _request(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise

    async def get_price(self, coin_id: str, vs_currency: str = "usd") -> dict:
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true"
        }
        data = await self._request("/simple/price", params)
        return data.get(coin_id, {})

    async def get_market_chart(self, coin_id: str, vs_currency: str = "usd", days: int = 30) -> dict:
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        return await self._request(f"/coins/{coin_id}/market_chart", params)