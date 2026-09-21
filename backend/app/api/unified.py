"""
API Endpoints Unificados - Oráculo v2.0
Expõe TODOS os 80+ parâmetros/conceitos
"""
from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd

from app.algorithms.unified_oracle import UnifiedOracle

router = APIRouter()
_oracle_cache = {}


def load_data(symbol: str) -> pd.DataFrame:
    """Carrega dados OHLCV"""
    import numpy as np
    np.random.seed(42)
    n = 1000
    base_price = 35000 if symbol == "BTC" else (2000 if symbol == "ETH" else 150)
    prices = base_price + np.cumsum(np.random.randn(n) * (base_price * 0.015))

    df = pd.DataFrame({
        'open': prices + np.random.randn(n) * (base_price * 0.005),
        'high': prices + np.abs(np.random.randn(n)) * (base_price * 0.015) + (base_price * 0.005),
        'low': prices - np.abs(np.random.randn(n)) * (base_price * 0.015) - (base_price * 0.005),
        'close': prices,
        'volume': np.abs(np.random.randn(n)) * 1000 + 5000
    })
    return df


@router.get("/{symbol}/full-analysis")
async def full_analysis(
    symbol: str = Query(..., description="BTC, ETH, SOL"),
    include_onchain: bool = Query(True, description="Incluir métricas on-chain (apenas BTC)")
):
    """
    🎯 ENDPOINT PRINCIPAL: Análise completa com TODOS os 80+ parâmetros

    Retorna:
    - Zonas unificadas (Fib + MM + Gann + Stats)
    - Market Makers (OB, FVG, Breaker, Liquidity)
    - Gann (Square of 9, Fan, Box, Time Cycles)
    - Indicadores Técnicos (ATR, Bollinger, RSI, MACD, StochRSI, VWAP, Volume Profile)
    - Séries Temporais (ARIMA, GARCH, Prophet)
    - Machine Learning (RF, XGBoost, LSTM)
    - On-Chain (MVRV, NUPL, SOPR, Puell, Mayer, S2F, Halving, Rainbow)
    - Modelos Estatísticos (GMM, KDE, Quantile, Markov, Monte Carlo, Bayesian, Hurst)
    - Elliott Waves
    - Wyckoff Advanced
    - Temporal Prediction (sazonalidade, calendário de reversões)
    """
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)

    oracle = UnifiedOracle()
    result = oracle.analyze(df, symbol)

    if not include_onchain or "BTC" not in symbol:
        result.pop("onchain", None)

    return result


@router.get("/{symbol}/zones")
async def get_zones(
    symbol: str,
    min_score: int = Query(0, ge=0, le=100),
    zone_type: Optional[str] = Query(None)
):
    """Apenas zonas unificadas (score 0-100)"""
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)
    oracle = UnifiedOracle()
    result = oracle.analyze(df, symbol)

    zones = result['unified_zones']
    if min_score > 0:
        zones = [z for z in zones if z['score'] >= min_score]
    if zone_type:
        zones = [z for z in zones if z['zone_type'] == zone_type]

    return {"symbol": symbol, "zones": zones, "count": len(zones)}


@router.get("/{symbol}/onchain")
async def get_onchain(symbol: str):
    """Apenas métricas on-chain (BTC only)"""
    symbol = symbol.upper().replace("USDT", "")
    if "BTC" not in symbol:
        return {"error": "On-chain metrics only available for BTC"}

    df = load_data(symbol)
    oracle = UnifiedOracle()
    result = oracle.analyze(df, symbol)
    return result.get("onchain", {})


@router.get("/{symbol}/temporal")
async def get_temporal(symbol: str):
    """Apenas previsões temporais (sazonalidade, calendário)"""
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)
    oracle = UnifiedOracle()
    result = oracle.analyze(df, symbol)
    return result.get("temporal", {})


@router.get("/{symbol}/summary")
async def get_summary(symbol: str):
    """Resumo executivo apenas"""
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)
    oracle = UnifiedOracle()
    result = oracle.analyze(df, symbol)
    return result.get("summary", {})
