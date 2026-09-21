"""
Market Makers / Smart Money Concepts Engine
Detecta Order Blocks, Fair Value Gaps, Breaker Blocks, Liquidity Pools, etc.
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class OrderBlock:
    price_top: float
    price_bottom: float
    type: str          # "bullish" ou "bearish"
    timeframe: str
    strength: float    # 0.0 - 1.0
    status: str        # "fresh", "tested", "violated"
    volume_ratio: float
    index: int


@dataclass
class FairValueGap:
    top: float
    bottom: float
    type: str          # "bullish" ou "bearish"
    timeframe: str
    filled: bool
    index: int


@dataclass
class LiquidityPool:
    price: float
    type: str          # "buy_side" ou "sell_side"
    sweeps: int
    volume: float


@dataclass
class BreakerBlock:
    price_top: float
    price_bottom: float
    original_type: str
    current_type: str
    index: int


class MarketMakersEngine:
    """
    Engine completo de Smart Money Concepts (ICT/SMC)
    """

    def __init__(self, atr_multiplier: float = 1.5, volume_threshold: float = 1.3):
        self.atr_multiplier = atr_multiplier
        self.volume_threshold = volume_threshold

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def detect_order_blocks(self, df: pd.DataFrame, timeframe: str = "1d") -> List[OrderBlock]:
        """
        Detecta Order Blocks:
        - Última vela contrária antes de um movimento impulsivo
        - Body > 2x ATR e volume > 1.3x média
        """
        atr = self.calculate_atr(df)
        avg_volume = df['volume'].rolling(20).mean()

        obs = []
        for i in range(5, len(df) - 3):
            # Detectar movimento impulsivo (3 candles consecutivos na mesma direção)
            c1 = df['close'].iloc[i+1] > df['open'].iloc[i+1]  # candle 1 bullish
            c2 = df['close'].iloc[i+2] > df['open'].iloc[i+2]  # candle 2 bullish
            c3 = df['close'].iloc[i+3] > df['open'].iloc[i+3]  # candle 3 bullish

            if c1 and c2 and c3:
                # Candle contrário anterior = candidato OB bullish
                ob_candle = df.iloc[i]
                body = abs(ob_candle['close'] - ob_candle['open'])

                if body > atr.iloc[i] * self.atr_multiplier and \
                   ob_candle['volume'] > avg_volume.iloc[i] * self.volume_threshold:

                    strength = min(1.0, (body / atr.iloc[i]) * 0.3 + \
                                  (ob_candle['volume'] / avg_volume.iloc[i]) * 0.3 + \
                                  0.4)

                    obs.append(OrderBlock(
                        price_top=max(ob_candle['open'], ob_candle['close']),
                        price_bottom=min(ob_candle['open'], ob_candle['close']),
                        type="bullish",
                        timeframe=timeframe,
                        strength=strength,
                        status="fresh",
                        volume_ratio=ob_candle['volume'] / avg_volume.iloc[i],
                        index=i
                    ))

            # Movimento impulsivo de baixa
            c1b = df['close'].iloc[i+1] < df['open'].iloc[i+1]
            c2b = df['close'].iloc[i+2] < df['open'].iloc[i+2]
            c3b = df['close'].iloc[i+3] < df['open'].iloc[i+3]

            if c1b and c2b and c3b:
                ob_candle = df.iloc[i]
                body = abs(ob_candle['close'] - ob_candle['open'])

                if body > atr.iloc[i] * self.atr_multiplier and \
                   ob_candle['volume'] > avg_volume.iloc[i] * self.volume_threshold:

                    strength = min(1.0, (body / atr.iloc[i]) * 0.3 + \
                                  (ob_candle['volume'] / avg_volume.iloc[i]) * 0.3 + \
                                  0.4)

                    obs.append(OrderBlock(
                        price_top=max(ob_candle['open'], ob_candle['close']),
                        price_bottom=min(ob_candle['open'], ob_candle['close']),
                        type="bearish",
                        timeframe=timeframe,
                        strength=strength,
                        status="fresh",
                        volume_ratio=ob_candle['volume'] / avg_volume.iloc[i],
                        index=i
                    ))

        return obs

    def detect_fair_value_gaps(self, df: pd.DataFrame, timeframe: str = "1d") -> List[FairValueGap]:
        """
        Detecta Fair Value Gaps (FVG):
        - Bullish FVG: low[2] > high[0] (gap de 3 candles)
        - Bearish FVG: high[2] < low[0]
        """
        fvgs = []
        for i in range(len(df) - 3):
            c0 = df.iloc[i]
            c1 = df.iloc[i+1]
            c2 = df.iloc[i+2]

            # Bullish FVG: low do candle 2 > high do candle 0
            if c2['low'] > c0['high']:
                # Verificar se já foi preenchido (filled)
                filled = any(df['low'].iloc[i+3:min(i+20, len(df))] <= c0['high'])
                fvgs.append(FairValueGap(
                    top=c2['low'],
                    bottom=c0['high'],
                    type="bullish",
                    timeframe=timeframe,
                    filled=filled,
                    index=i
                ))

            # Bearish FVG: high do candle 2 < low do candle 0
            if c2['high'] < c0['low']:
                filled = any(df['high'].iloc[i+3:min(i+20, len(df))] >= c0['low'])
                fvgs.append(FairValueGap(
                    top=c0['low'],
                    bottom=c2['high'],
                    type="bearish",
                    timeframe=timeframe,
                    filled=filled,
                    index=i
                ))

        return fvgs

    def detect_breaker_blocks(self, df: pd.DataFrame, obs: List[OrderBlock]) -> List[BreakerBlock]:
        """
        Detecta Breaker Blocks: OB que foi violado e virou S/R oposto
        """
        breakers = []
        for ob in obs:
            if ob.status == "fresh":
                # Verificar se preço violou o OB
                future_prices = df.iloc[ob.index+1:min(ob.index+50, len(df))]

                if ob.type == "bullish":
                    violated = any(future_prices['low'] < ob.price_bottom)
                    if violated:
                        breakers.append(BreakerBlock(
                            price_top=ob.price_top,
                            price_bottom=ob.price_bottom,
                            original_type="bullish",
                            current_type="bearish",
                            index=ob.index
                        ))
                else:
                    violated = any(future_prices['high'] > ob.price_top)
                    if violated:
                        breakers.append(BreakerBlock(
                            price_top=ob.price_top,
                            price_bottom=ob.price_bottom,
                            original_type="bearish",
                            current_type="bullish",
                            index=ob.index
                        ))

        return breakers

    def detect_liquidity_pools(self, df: pd.DataFrame) -> List[LiquidityPool]:
        """
        Detecta Liquidity Pools:
        - Sell-side: stops acima de swing highs
        - Buy-side: stops abaixo de swing lows
        """
        pools = []
        window = 5

        for i in range(window, len(df) - window):
            # Swing high
            if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
                pools.append(LiquidityPool(
                    price=df['high'].iloc[i],
                    type="sell_side",
                    sweeps=sum(df['high'].iloc[i+1:min(i+20, len(df))] > df['high'].iloc[i]),
                    volume=df['volume'].iloc[i]
                ))

            # Swing low
            if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
                pools.append(LiquidityPool(
                    price=df['low'].iloc[i],
                    type="buy_side",
                    sweeps=sum(df['low'].iloc[i+1:min(i+20, len(df))] < df['low'].iloc[i]),
                    volume=df['volume'].iloc[i]
                ))

        return pools

    def detect_displacement(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detecta Displacement: movimento de alta velocidade + volume
        """
        displacements = []
        atr = self.calculate_atr(df)
        avg_volume = df['volume'].rolling(20).mean()

        for i in range(1, len(df)):
            body = abs(df['close'].iloc[i] - df['open'].iloc[i])
            if body > atr.iloc[i] * 2.5 and df['volume'].iloc[i] > avg_volume.iloc[i] * 1.5:
                displacements.append({
                    "index": i,
                    "price": df['close'].iloc[i],
                    "direction": "bullish" if df['close'].iloc[i] > df['open'].iloc[i] else "bearish",
                    "body_size": body,
                    "volume_ratio": df['volume'].iloc[i] / avg_volume.iloc[i]
                })

        return displacements

    def analyze(self, df: pd.DataFrame, timeframe: str = "1d") -> Dict:
        """Executa análise completa de Market Makers"""
        obs = self.detect_order_blocks(df, timeframe)
        fvgs = self.detect_fair_value_gaps(df, timeframe)
        breakers = self.detect_breaker_blocks(df, obs)
        pools = self.detect_liquidity_pools(df)
        displacements = self.detect_displacement(df)

        return {
            "order_blocks": [
                {"top": ob.price_top, "bottom": ob.price_bottom, "type": ob.type,
                 "strength": round(ob.strength, 2), "status": ob.status}
                for ob in obs[:10]
            ],
            "fair_value_gaps": [
                {"top": fvg.top, "bottom": fvg.bottom, "type": fvg.type, "filled": fvg.filled}
                for fvg in fvgs[:10]
            ],
            "breaker_blocks": [
                {"top": bb.price_top, "bottom": bb.price_bottom, "current_type": bb.current_type}
                for bb in breakers[:5]
            ],
            "liquidity_pools": [
                {"price": p.price, "type": p.type, "sweeps": p.sweeps}
                for p in pools[:10]
            ],
            "displacements": displacements[:5],
            "summary": {
                "total_obs": len(obs),
                "total_fvgs": len(fvgs),
                "total_breakers": len(breakers),
                "total_pools": len(pools)
            }
        }
