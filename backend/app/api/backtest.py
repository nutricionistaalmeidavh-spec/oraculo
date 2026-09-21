"""
API Endpoints para Backtest
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class BacktestRequest(BaseModel):
    symbol: str
    strategy: str  # "zone_bounce", "zone_break", "confluence_entry"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 10000.0
    risk_per_trade: float = 0.02  # 2%


@router.post("/")
async def run_backtest(request: BacktestRequest):
    """Executa backtest de estratégia baseada em zonas"""

    # Simulação de backtest (em produção usar dados históricos reais)
    return {
        "symbol": request.symbol,
        "strategy": request.strategy,
        "initial_capital": request.initial_capital,
        "final_capital": 14750.0,
        "total_return": 47.5,
        "total_trades": 23,
        "winning_trades": 16,
        "losing_trades": 7,
        "win_rate": 69.6,
        "profit_factor": 2.34,
        "max_drawdown": 12.3,
        "sharpe_ratio": 1.87,
        "avg_trade_return": 2.06,
        "trades": [
            {"entry": 95000, "exit": 102000, "return": 7.4, "type": "long", "result": "win"},
            {"entry": 108000, "exit": 104500, "return": -3.2, "type": "short", "result": "loss"},
            {"entry": 74000, "exit": 85000, "return": 14.9, "type": "long", "result": "win"}
        ]
    }


@router.get("/strategies")
async def list_strategies():
    """Lista estratégias de backtest disponíveis"""
    return {
        "strategies": [
            {
                "id": "zone_bounce",
                "name": "Reversão na Zona",
                "description": "Entrada long em zona de suporte, short em resistência. Stop atrás da zona."
            },
            {
                "id": "zone_break",
                "name": "Rompimento de Zona",
                "description": "Entrada na direção do rompimento com volume. Stop do outro lado da zona."
            },
            {
                "id": "confluence_entry",
                "name": "Entrada em Confluência",
                "description": "Só entra quando 3+ metodologias concordam na mesma zona."
            }
        ]
    }
