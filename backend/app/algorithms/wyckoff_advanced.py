"""
Wyckoff Method Advanced Engine
Detecção automática de fases A/B/C/D/E + springs/upthrusts
"""
import numpy as np
import pandas as pd
from typing import Dict, List


class WyckoffAdvancedEngine:
    """Engine avançado de Wyckoff Method"""

    def detect_phase(self, df: pd.DataFrame) -> Dict:
        """
        Detecta fase Wyckoff atual (A/B/C/D/E)
        """
        prices = df['close'].values
        volumes = df['volume'].values

        n = len(prices)
        if n < 50:
            return {"phase": "insufficient_data", "confidence": 0.0}

        recent = df.iloc[-50:]

        # Métricas
        price_range = recent['high'].max() - recent['low'].min()
        avg_volume = recent['volume'].mean()
        volume_trend = np.polyfit(range(len(recent)), recent['volume'].values, 1)[0]
        price_trend = np.polyfit(range(len(recent)), recent['close'].values, 1)[0]

        # Bollinger squeeze (consolidação)
        sma20 = recent['close'].rolling(20).mean()
        std20 = recent['close'].rolling(20).std()
        bb_width = (std20 / sma20).mean()

        # Detectar springs (falso rompimento para baixo + reversão)
        lows = recent['low'].values
        spring = False
        if len(lows) > 10:
            min_idx = np.argmin(lows[-10:])
            if min_idx < 9:  # Não é o último
                recovery = lows[-1] > lows[-10:][min_idx] * 1.02
                high_volume = recent['volume'].iloc[-10:].iloc[min_idx] > avg_volume * 1.3
                spring = recovery and high_volume

        # Detectar upthrusts (falso rompimento para cima + reversão)
        highs = recent['high'].values
        upthrust = False
        if len(highs) > 10:
            max_idx = np.argmax(highs[-10:])
            if max_idx < 9:
                drop = highs[-1] < highs[-10:][max_idx] * 0.98
                high_vol = recent['volume'].iloc[-10:].iloc[max_idx] > avg_volume * 1.3
                upthrust = drop and high_vol

        # Classificar fase
        if spring and volume_trend < 0:
            phase = "C_spring"
            confidence = 0.75
        elif upthrust and volume_trend < 0:
            phase = "E_upthrust"
            confidence = 0.70
        elif bb_width < 0.02 and abs(price_trend) < price_range * 0.001:
            phase = "B_accumulation" if volume_trend < 0 else "B_distribution"
            confidence = 0.65
        elif price_trend > price_range * 0.005 and volume_trend > 0:
            phase = "D_markup"
            confidence = 0.70
        elif price_trend < -price_range * 0.005 and volume_trend > 0:
            phase = "E_markdown"
            confidence = 0.65
        else:
            phase = "A_transition"
            confidence = 0.50

        return {
            "phase": phase,
            "confidence": round(confidence, 2),
            "spring_detected": spring,
            "upthrust_detected": upthrust,
            "volume_trend": "decreasing" if volume_trend < 0 else "increasing",
            "price_trend": "up" if price_trend > 0 else "down",
            "consolidation": bb_width < 0.02,
            "narrative": self._narrative(phase, spring, upthrust)
        }

    def _narrative(self, phase: str, spring: bool, upthrust: bool) -> str:
        """Gera narrativa da fase Wyckoff"""
        narratives = {
            "A_transition": "Mercado em transição. Aguardar sinais de acumulação ou distribuição.",
            "B_accumulation": "Fase B de acumulação. Volume decrescendo, range apertado. Springs possíveis.",
            "B_distribution": "Fase B de distribuição. Volume decrescendo, range apertado. Upthrusts possíveis.",
            "C_spring": "Fase C com Spring detectado! Falso rompimento + reversão = sinal de compra institucional.",
            "D_markup": "Fase D de Markup. Tendência de alta com volume crescente. Seguir a tendência.",
            "E_upthrust": "Fase E com Upthrust! Falso rompimento + queda = sinal de venda institucional.",
            "E_markdown": "Fase E de Markdown. Tendência de baixa com volume crescente."
        }
        return narratives.get(phase, "Fase indefinida.")

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise Wyckoff completa"""
        return self.detect_phase(df)
