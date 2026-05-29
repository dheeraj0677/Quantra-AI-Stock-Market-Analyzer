"""
Quantra — API v1 router aggregation.
"""

from fastapi import APIRouter

from app.api.v1.alerts import router as alerts_router
from app.api.v1.auth import router as auth_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.market import router as market_router
from app.api.v1.news import router as news_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.prediction import router as prediction_router
from app.api.v1.screener import router as screener_router
from app.api.v1.signals import router as signals_router
from app.api.v1.stocks import router as stocks_router
from app.api.v1.suggestions import router as suggestions_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(stocks_router, prefix="/stocks", tags=["Stocks"])
api_router.include_router(prediction_router, prefix="/predict", tags=["Prediction"])
api_router.include_router(screener_router, prefix="/screener", tags=["Screener"])
api_router.include_router(news_router, prefix="/news", tags=["News"])
api_router.include_router(market_router, prefix="/market", tags=["Market"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(backtest_router, prefix="/backtest", tags=["Backtest"])
api_router.include_router(signals_router, prefix="/signals", tags=["Signals"])
api_router.include_router(suggestions_router, prefix="/suggestions", tags=["Suggestions"])
