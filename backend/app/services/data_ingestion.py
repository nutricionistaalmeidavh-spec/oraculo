"""
Serviço de Ingestão de Dados v2.0
Busca dados OHLCV da Binance e armazena localmente.
"""
import pandas as pd
import os
from typing import Optional


class DataIngestionService:
    """
    Serviço responsável por buscar e armazenar dados de criptoativos.

    PRIORIDADE:
    1. Dados CSV locais (baixados via fetch_real_data.py)
    2. Dados sintéticos (fallback para desenvolvimento)
    """

    DATA_DIR = "/app/data"

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def fetch_historical_data(
        self,
        symbol: str,
        interval: str = "1d",
        days: int = 1000,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Carrega dados OHLCV.

        PRIORIDADE:
        1. Arquivo CSV local (dados reais da Binance)
        2. Dados sintéticos (fallback)
        """
        symbol = symbol.upper().replace("USDT", "")
        cache_file = os.path.join(self.DATA_DIR, f"{symbol}USDT_{interval}.csv")

        # 1. Tentar carregar dados REAIS do CSV
        if use_cache and os.path.exists(cache_file):
            print(f"📂 Carregando dados REAIS: {cache_file}")
            df = pd.read_csv(cache_file)
            df['open_time'] = pd.to_datetime(df['open_time'])
            df = df.set_index('open_time')
            return df

        # 2. Fallback: dados sintéticos
        print(f"⚠️ Dados reais não encontrados para {symbol}. Gerando sintéticos...")
        print(f"   💡 Dica: Rode 'python fetch_real_data.py' para baixar dados reais da Binance")
        return self._generate_synthetic_data(symbol, days)

    def _generate_synthetic_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Gera dados sintéticos realistas para desenvolvimento"""
        import numpy as np

        np.random.seed(42)
        base_price = {"BTC": 35000, "ETH": 2000, "SOL": 150}.get(symbol, 100)
        volatility = base_price * 0.02

        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
        returns = np.random.randn(days) * volatility
        prices = base_price + np.cumsum(returns)

        df = pd.DataFrame({
            'open': prices + np.random.randn(days) * (base_price * 0.005),
            'high': prices + np.abs(np.random.randn(days)) * (base_price * 0.015) + (base_price * 0.005),
            'low': prices - np.abs(np.random.randn(days)) * (base_price * 0.015) - (base_price * 0.005),
            'close': prices,
            'volume': np.abs(np.random.randn(days)) * 1000 + 5000,
            'quote_volume': np.abs(np.random.randn(days)) * 50000 + 250000
        }, index=dates)

        return df

    def save_to_csv(self, df: pd.DataFrame, symbol: str, interval: str):
        """Salva DataFrame em CSV para cache"""
        cache_file = os.path.join(self.DATA_DIR, f"{symbol}USDT_{interval}.csv")
        df.reset_index().to_csv(cache_file, index=False)
        print(f"💾 Dados salvos em {cache_file}")
