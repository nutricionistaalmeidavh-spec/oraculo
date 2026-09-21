"""
Elliott Wave Theory Engine
Detecta ondas 1-5 (impulso) e ABC (correção)
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional


class ElliottWaveEngine:
    """Engine de Elliott Wave Theory"""

    def find_pivots(self, df: pd.DataFrame, window: int = 5) -> List[Dict]:
        """Encontra pivôs de topo e fundo"""
        highs = df['high'].values
        lows = df['low'].values
        pivots = []

        for i in range(window, len(df) - window):
            # Pivot high
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                pivots.append({"index": i, "price": highs[i], "type": "high", "date": df.index[i]})

            # Pivot low
            if all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1)):
                pivots.append({"index": i, "price": lows[i], "type": "low", "date": df.index[i]})

        return sorted(pivots, key=lambda x: x['index'])

    def detect_elliott_pattern(self, df: pd.DataFrame) -> Dict:
        """
        Detecta padrão Elliott Wave simplificado
        Busca sequência: low → high → low → high → low → high → low (ondas 1-5 + ABC)
        """
        pivots = self.find_pivots(df)
        if len(pivots) < 7:
            return {"pattern": "insufficient_pivots", "confidence": 0.0}

        # Pegar últimos 7 pivôs
        recent = pivots[-7:]

        # Verificar se alternam high/low
        expected = ["low", "high", "low", "high", "low", "high", "low"]
        alternation = sum(1 for r, e in zip(recent, expected) if r['type'] == e) / 7

        if alternation < 0.7:
            return {"pattern": "no_clear_pattern", "confidence": round(alternation, 2)}

        # Calcular proporções Fibonacci das ondas
        wave1 = recent[1]['price'] - recent[0]['price']  # low → high
        wave2 = recent[2]['price'] - recent[1]['price']  # high → low
        wave3 = recent[3]['price'] - recent[2]['price']  # low → high
        wave4 = recent[4]['price'] - recent[3]['price']  # high → low
        wave5 = recent[5]['price'] - recent[4]['price']  # low → high

        wave_a = recent[6]['price'] - recent[5]['price']  # high → low

        # Regras de Elliott (simplificadas)
        checks = {
            "wave3_longest": abs(wave3) > abs(wave1) and abs(wave3) > abs(wave5),
            "wave2_retracement": abs(wave2) < abs(wave1) * 0.618,
            "wave4_retracement": abs(wave4) < abs(wave3) * 0.5,
            "wave5_extension": abs(wave5) > abs(wave1) * 0.5,
        }

        score = sum(checks.values()) / len(checks)

        current_wave = None
        if wave5 > 0 and recent[-1]['type'] == 'low':
            current_wave = "wave_A_correction"
        elif wave5 > 0:
            current_wave = "wave_5_complete"
        elif wave3 > 0 and wave4 < 0:
            current_wave = "wave_4_in_progress"
        elif wave3 > 0:
            current_wave = "wave_3_in_progress"

        return {
            "pattern": "elliott_5wave" if score > 0.6 else "possible_elliott",
            "confidence": round(score, 2),
            "current_wave": current_wave,
            "wave_lengths": {
                "wave1": round(abs(wave1), 2),
                "wave2": round(abs(wave2), 2),
                "wave3": round(abs(wave3), 2),
                "wave4": round(abs(wave4), 2),
                "wave5": round(abs(wave5), 2)
            },
            "checks": checks,
            "projected_C": round(recent[5]['price'] - abs(wave_a) * 1.618, 2) if wave_a != 0 else None
        }

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise Elliott Wave completa"""
        return {
            "elliott_pattern": self.detect_elliott_pattern(df),
            "pivots": self.find_pivots(df)[-10:]
        }
