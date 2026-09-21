"""
API Endpoints para Zonas
"""
from fastapi import APIRouter, Query
from typing import List, Optional
import pandas as pd

from app.algorithms.fibonacci_oracle import FibonacciOracle, TimeHorizon

router = APIRouter()

# Cache em memória simples (em produção usar Redis)
_data_cache = {}
_oracle_cache = {}


def load_data(symbol: str) -> pd.DataFrame:
    """Carrega dados OHLCV do CSV local"""
    import os

    cache_key = f"{symbol}_daily"
    if cache_key in _data_cache:
        return _data_cache[cache_key]

    # Tentar carregar do arquivo CSV baixado
    filepath = f"/app/data/{symbol}USDT_daily.csv"

    # Se não existir, usar dados de exemplo
    if not os.path.exists(filepath):
        # Criar dados sintéticos para demo
        import numpy as np
        np.random.seed(42)
        n = 1000
        base_price = 35000 if symbol == "BTC" else (2000 if symbol == "ETH" else 150)
        prices = base_price + np.cumsum(np.random.randn(n) * (base_price * 0.01))

        df = pd.DataFrame({
            'open': prices + np.random.randn(n) * (base_price * 0.005),
            'high': prices + np.abs(np.random.randn(n)) * (base_price * 0.015) + (base_price * 0.005),
            'low': prices - np.abs(np.random.randn(n)) * (base_price * 0.015) - (base_price * 0.005),
            'close': prices,
            'volume': np.random.randn(n) * 1000 + 5000
        })
        _data_cache[cache_key] = df
        return df

    df = pd.read_csv(filepath)
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df = df.set_index('open_time')
    _data_cache[cache_key] = df
    return df


@router.get("/{symbol}")
async def get_zones(
    symbol: str = Query(..., description="Símbolo do ativo: BTC, ETH, SOL"),
    min_score: int = Query(0, ge=0, le=100, description="Score mínimo para filtrar"),
    zone_type: Optional[str] = Query(None, description="Filtrar por tipo: critical, high, medium"),
    timeframe: Optional[str] = Query(None, description="Horizonte temporal específico")
):
    """
    Retorna todas as zonas de confluência detectadas para um ativo.

    Exemplo: GET /api/v1/zones/BTC?min_score=70&zone_type=critical
    """
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)
    current_price = float(df['close'].iloc[-1])

    oracle = FibonacciOracle()
    result = oracle.analyze(df, current_price)

    # Filtrar
    zones = result['all_zones']
    if min_score > 0:
        zones = [z for z in zones if z['score'] >= min_score]
    if zone_type:
        zones = [z for z in zones if z['zone_type'] == zone_type]

    return {
        "symbol": f"{symbol}USDT",
        "current_price": current_price,
        "zones": zones,
        "count": len(zones)
    }


@router.get("/{symbol}/fusion")
async def get_fusion_zones(symbol: str):
    """
    Retorna apenas as zonas de maior confluência (fusion).
    Zonas onde 3+ Fibonaccis de horizontes diferentes convergem.
    """
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)
    current_price = float(df['close'].iloc[-1])

    oracle = FibonacciOracle()
    result = oracle.analyze(df, current_price)

    # Apenas critical + high
    fusion = result['critical_zones'] + result['high_zones']

    return {
        "symbol": f"{symbol}USDT",
        "current_price": current_price,
        "fusion_zones": fusion,
        "count": len(fusion)
    }


@router.get("/{symbol}/horizons")
async def get_horizon_analysis(symbol: str):
    """
    Retorna análise detalhada por horizonte temporal.
    Mostra swing points e níveis Fib de cada horizonte separadamente.
    """
    symbol = symbol.upper().replace("USDT", "")
    df = load_data(symbol)
    current_price = float(df['close'].iloc[-1])

    oracle = FibonacciOracle()
    result = oracle.analyze(df, current_price)

    return {
        "symbol": f"{symbol}USDT",
        "current_price": current_price,
        "horizons": result['horizons']
    }
