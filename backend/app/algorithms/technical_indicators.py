"""
Technical Indicators Engine
ATR, Bollinger Bands, RSI, MACD, Stoch RSI, VWAP, Volume Profile
"""
import numpy as np
import pandas as pd
from typing import Dict, List


class TechnicalIndicatorsEngine:
    """Engine de indicadores técnicos para confirmação de zonas"""

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    @staticmethod
    def bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict:
        """Bollinger Bands"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        bandwidth = (upper - lower) / sma

        return {
            "middle": sma.iloc[-1],
            "upper": upper.iloc[-1],
            "lower": lower.iloc[-1],
            "bandwidth": bandwidth.iloc[-1],
            "percent_b": (df['close'].iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
        }

    @staticmethod
    def rsi(df: pd.DataFrame, period: int = 14) -> float:
        """Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    @staticmethod
    def macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {
            "macd": macd_line.iloc[-1],
            "signal": signal_line.iloc[-1],
            "histogram": histogram.iloc[-1],
            "trend": "bullish" if macd_line.iloc[-1] > signal_line.iloc[-1] else "bearish"
        }

    @staticmethod
    def stochastic_rsi(df: pd.DataFrame, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Dict:
        """Stochastic RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        rsi_min = rsi.rolling(window=period).min()
        rsi_max = rsi.rolling(window=period).max()
        stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min)
        k = stoch_rsi.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()

        return {
            "k": k.iloc[-1] * 100,
            "d": d.iloc[-1] * 100,
            "oversold": k.iloc[-1] < 0.2,
            "overbought": k.iloc[-1] > 0.8
        }

    @staticmethod
    def vwap(df: pd.DataFrame) -> float:
        """Volume Weighted Average Price"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap.iloc[-1]

    @staticmethod
    def volume_profile(df: pd.DataFrame, num_bins: int = 20) -> List[Dict]:
        """Volume Profile: distribuição de volume por faixa de preço"""
        min_p = df['low'].min()
        max_p = df['high'].max()
        bin_size = (max_p - min_p) / num_bins

        profile = []
        for i in range(num_bins):
            low_bin = min_p + (i * bin_size)
            high_bin = min_p + ((i + 1) * bin_size)
            mask = (df['close'] >= low_bin) & (df['close'] < high_bin)
            volume = df.loc[mask, 'volume'].sum()
            profile.append({
                "price_low": round(low_bin, 2),
                "price_high": round(high_bin, 2),
                "volume": volume,
                "center": round((low_bin + high_bin) / 2, 2)
            })

        # Encontrar POC (Point of Control)
        poc = max(profile, key=lambda x: x['volume'])
        for p in profile:
            p['is_poc'] = (p['center'] == poc['center'])

        return profile

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise completa de indicadores técnicos"""
        return {
            "atr": round(self.atr(df).iloc[-1], 2),
            "bollinger": {k: round(v, 2) if isinstance(v, float) else v for k, v in self.bollinger_bands(df).items()},
            "rsi": round(self.rsi(df), 2),
            "macd": {k: round(v, 4) if isinstance(v, float) else v for k, v in self.macd(df).items()},
            "stoch_rsi": {k: round(v, 2) if isinstance(v, float) else v for k, v in self.stochastic_rsi(df).items()},
            "vwap": round(self.vwap(df), 2),
            "volume_profile": self.volume_profile(df)[:10]
        }
