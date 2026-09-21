"""
Oráculo de Zonas v2.0 - Backend FastAPI
SaaS de análise de criptoativos com 80+ parâmetros
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import zones, analysis, alerts, backtest, unified


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Oráculo de Zonas v2.0 iniciando...")
    yield
    print("🛑 Oráculo de Zonas v2.0 encerrando...")


app = FastAPI(
    title="Oráculo de Zonas API v2.0",
    description="SaaS de identificação de zonas de interesse em BTC/ETH/SOL. 80+ parâmetros: Fibonacci, Market Makers, Gann, Wyckoff, Elliott, On-Chain, ML, Estatística, Temporal.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers v1 (mantidos para compatibilidade)
app.include_router(zones.router, prefix="/api/v1/zones", tags=["Zonas v1"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Análise v1"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alertas"])
app.include_router(backtest.router, prefix="/api/v1/backtest", tags=["Backtest"])

# Router v2 - UNIFIED (novo)
app.include_router(unified.router, prefix="/api/v2", tags=["Oráculo Unificado v2"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0", "modules": 11}


@app.get("/modules")
async def list_modules():
    """Lista todos os módulos disponíveis"""
    return {
        "modules": [
            {"id": "fibonacci", "name": "Fibonacci Multi-Timeframe", "params": 6},
            {"id": "market_makers", "name": "Smart Money Concepts", "params": 10},
            {"id": "gann", "name": "Gann Analysis", "params": 4},
            {"id": "technical_indicators", "name": "Technical Indicators", "params": 7},
            {"id": "time_series", "name": "Time Series", "params": 3},
            {"id": "machine_learning", "name": "Machine Learning", "params": 3},
            {"id": "bitcoin_onchain", "name": "Bitcoin On-Chain", "params": 36},
            {"id": "statistical_models", "name": "Statistical Models", "params": 7},
            {"id": "elliott_waves", "name": "Elliott Wave Theory", "params": 5},
            {"id": "wyckoff", "name": "Wyckoff Method", "params": 5},
            {"id": "temporal", "name": "Temporal Prediction", "params": 3}
        ],
        "total_params": 80
    }
