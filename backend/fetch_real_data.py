"""
Fetch Real Data from Binance
Baixa dados históricos reais de BTC, ETH, SOL
"""
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import time

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)


def fetch_binance_klines(symbol: str, interval: str = "1d", limit: int = 1000):
    """
    Busca dados OHLCV da API pública da Binance (não precisa de API key)
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": f"{symbol}USDT",
        "interval": interval,
        "limit": limit
    }

    print(f"📡 Buscando {symbol}USDT ({interval}, {limit} candles)...")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
            'taker_buy_quote_volume', 'ignore'
        ])

        # Converter tipos
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df = df.set_index('open_time')

        print(f"✅ {len(df)} candles baixados. De {df.index[0]} até {df.index[-1]}")
        return df

    except Exception as e:
        print(f"❌ Erro ao buscar {symbol}: {e}")
        return None


def save_data(df: pd.DataFrame, symbol: str, interval: str):
    """Salva em CSV"""
    filepath = os.path.join(DATA_DIR, f"{symbol}USDT_{interval}.csv")
    df.to_csv(filepath)
    print(f"💾 Salvo em: {filepath}")
    return filepath


def fetch_all(symbols=["BTC", "ETH", "SOL"], intervals=["1d", "4h", "1h"]):
    """Baixa todos os dados"""
    for symbol in symbols:
        for interval in intervals:
            df = fetch_binance_klines(symbol, interval)
            if df is not None:
                save_data(df, symbol, interval)
            time.sleep(0.5)  # Respeitar rate limit
    print("\n🎉 Todos os dados baixados!")


if __name__ == "__main__":
    print("=" * 50)
    print("📊 ORÁCULO DE ZONAS - Download de Dados Reais")
    print("=" * 50)
    fetch_all()
