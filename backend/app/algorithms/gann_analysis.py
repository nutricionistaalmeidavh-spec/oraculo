"""
Gann Analysis Engine
Caixa de Gann, Leque de Gann, Quadrado de Gann (Square of 9)
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class GannEngine:
    """
    Engine completo de análise Gann
    """

    def square_of_9(self, base_price: float, num_levels: int = 10) -> Dict:
        """
        Quadrado de Gann (Square of 9)
        Calcula níveis de preço baseados na geometria espiral de Gann

        Fórmula: preço = sqrt(base) + (n * 0.5))^2
        onde n é o número de passos no quadrado
        """
        cardinal = []
        cross = []

        root = np.sqrt(base_price)

        for n in range(-num_levels, num_levels + 1):
            price = (root + (n * 0.5)) ** 2
            if n % 2 == 0:
                cardinal.append(round(price, 2))
            else:
                cross.append(round(price, 2))

        # Níveis de 45°, 90°, 135°, 180°, 225°, 270°, 315°, 360°
        angles = {}
        for angle in [45, 90, 135, 180, 225, 270, 315, 360]:
            step = angle / 45
            price = (root + (step * 0.5)) ** 2
            angles[f"{angle}°"] = round(price, 2)

        return {
            "base_price": base_price,
            "cardinal": sorted(list(set(cardinal))),
            "cross": sorted(list(set(cross))),
            "angles": angles
        }

    def gann_angles(self, swing_low: float, swing_high: float, 
                    start_date: datetime, num_points: int = 100) -> Dict:
        """
        Leque de Gann (Gann Fan)
        Calcula ângulos de Gann: 1x1, 1x2, 2x1, 1x4, 4x1

        1x1 = 45° - 1 unidade de preço por 1 unidade de tempo
        1x2 = 63.75° - 2 unidades de preço por 1 de tempo
        2x1 = 26.25° - 1 unidade de preço por 2 de tempo
        """
        price_range = swing_high - swing_low

        angles = {
            "1x8": {"slope": 8.0, "angle_deg": 82.5},
            "1x4": {"slope": 4.0, "angle_deg": 75.0},
            "1x2": {"slope": 2.0, "angle_deg": 63.75},
            "1x1": {"slope": 1.0, "angle_deg": 45.0},
            "2x1": {"slope": 0.5, "angle_deg": 26.25},
            "4x1": {"slope": 0.25, "angle_deg": 15.0},
            "8x1": {"slope": 0.125, "angle_deg": 7.5}
        }

        result = {}
        for name, config in angles.items():
            slope = config["slope"]
            # Projeção de preço baseada no slope
            projected = swing_low + (price_range * slope * 0.5)
            result[name] = {
                "slope": slope,
                "angle_deg": config["angle_deg"],
                "current_projection": round(projected, 2)
            }

        return result

    def gann_box(self, high: float, low: float, start_date: datetime, 
                 end_date: datetime) -> Dict:
        """
        Caixa de Gann (Gann Box)
        Divide o range em proporções de 1/8 (Gann dividia tudo em 8 partes)
        """
        range_price = high - low
        levels = {}

        for i in range(9):
            fraction = i / 8
            price = low + (range_price * fraction)
            levels[f"{i}/8"] = round(price, 2)

        # Níveis críticos de Gann
        critical = {
            "0/8": levels["0/8"],      # Suporte forte
            "1/8": levels["1/8"],      # Reversão fraca
            "2/8": levels["2/8"],      # Reversão
            "3/8": levels["3/8"],      # Resistência
            "4/8": levels["4/8"],      # Pivô / centro
            "5/8": levels["5/8"],      # Resistência
            "6/8": levels["6/8"],      # Reversão
            "7/8": levels["7/8"],      # Reversão fraca
            "8/8": levels["8/8"]       # Resistência forte
        }

        return {
            "high": high,
            "low": low,
            "range": round(range_price, 2),
            "levels": levels,
            "critical": critical
        }

    def time_cycles(self, start_date: datetime) -> Dict:
        """
        Ciclos de tempo de Gann
        30, 60, 90, 120, 180, 270, 360 dias
        """
        cycles = [30, 60, 90, 120, 180, 270, 360]
        result = {}

        for days in cycles:
            date = start_date + timedelta(days=days)
            result[f"{days}_days"] = date.strftime("%Y-%m-%d")

        # Ciclos quadrados (importantes para Gann)
        square_cycles = [49, 144, 169, 256, 324, 441, 576]
        for days in square_cycles:
            date = start_date + timedelta(days=days)
            result[f"square_{days}"] = date.strftime("%Y-%m-%d")

        return result

    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Análise completa Gann"""
        swing_high = df['high'].max()
        swing_low = df['low'].min()
        start_date = pd.to_datetime(df.index[0]) if hasattr(df.index[0], 'strftime') else datetime.now()

        return {
            "square_of_9": self.square_of_9(current_price),
            "gann_angles": self.gann_angles(swing_low, swing_high, start_date),
            "gann_box": self.gann_box(swing_high, swing_low, start_date, datetime.now()),
            "time_cycles": self.time_cycles(start_date),
            "recommendation": self._generate_recommendation(current_price, swing_high, swing_low)
        }

    def _generate_recommendation(self, price: float, high: float, low: float) -> str:
        """Gera recomendação baseada na posição no Gann Box"""
        mid = (high + low) / 2
        if price > mid * 1.05:
            return "Preço acima do pivô 4/8. Zonas de resistência Gann ativas acima."
        elif price < mid * 0.95:
            return "Preço abaixo do pivô 4/8. Zonas de suporte Gann ativas abaixo."
        else:
            return "Preço próximo ao pivô 4/8. Zona de decisão crítica."
