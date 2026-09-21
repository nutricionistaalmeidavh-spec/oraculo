"""
Oráculo de Zonas Fibonacci - Motor de Confluência
Detecta zonas onde múltiplos Fibonaccis de diferentes horizontes temporais convergem.
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import warnings
warnings.filterwarnings('ignore')


class ZoneType(Enum):
    CRITICAL = "critical"      # 4+ confluências
    HIGH = "high"              # 3 confluências
    MEDIUM = "medium"          # 2 confluências
    OBSERVATION = "observation" # 1 confluência


class TimeHorizon(Enum):
    CICLO_COMPLETO = "ciclo_completo"  # ~3 anos
    ANO_1 = "1_ano"
    MESES_6 = "6_meses"
    MESES_3 = "3_meses"
    MES_1 = "1_mes"
    SEMANAL = "semanal"


@dataclass
class FibZone:
    """Uma zona Fibonacci individual de um horizonte temporal"""
    price: float
    level: float                    # 0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.272, 1.618, 2.618
    horizon: TimeHorizon
    swing_high: float
    swing_low: float
    direction: str                  # "retracement" ou "extension"

    def __repr__(self):
        return f"FibZone({self.horizon.value}, {self.level:.3f}, ${self.price:,.2f})"


@dataclass
class SuperZone:
    """Zona de confluência onde múltiplos Fibonaccis convergem"""
    center_price: float
    price_bottom: float
    price_top: float
    score: int                      # 0-100
    zone_type: ZoneType
    confluence_count: int           # quantos fibs convergem
    fib_zones: List[FibZone] = field(default_factory=list)
    timeframes: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "center_price": round(self.center_price, 2),
            "price_bottom": round(self.price_bottom, 2),
            "price_top": round(self.price_top, 2),
            "score": self.score,
            "zone_type": self.zone_type.value,
            "confluence_count": self.confluence_count,
            "timeframes": self.timeframes,
            "description": self.description,
            "fib_details": [
                {"horizon": z.horizon.value, "level": z.level, "price": round(z.price, 2)}
                for z in self.fib_zones
            ]
        }


class FibonacciOracle:
    """
    Oráculo de Zonas Fibonacci

    Detecta zonas de alta confluência onde múltiplos níveis Fibonacci
    de diferentes horizontes temporais se sobrepõem.

    Horizontes analisados:
    - Ciclo completo (~3 anos de dados)
    - 1 ano
    - 6 meses
    - 3 meses
    - 1 mês
    - Semanal (últimas 4 semanas)
    """

    FIB_LEVELS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.272, 1.618, 2.618]
    EXTENSION_LEVELS = [1.0, 1.272, 1.618, 2.0, 2.618, 3.618, 4.236]

    # Tolerância para considerar dois níveis Fib como "na mesma zona" (em %)
    TOLERANCE = 0.015  # 1.5%

    # Número de candles para cada horizonte (diário)
    HORIZON_PERIODS = {
        TimeHorizon.CICLO_COMPLETO: 1000,
        TimeHorizon.ANO_1: 365,
        TimeHorizon.MESES_6: 180,
        TimeHorizon.MESES_3: 90,
        TimeHorizon.MES_1: 30,
        TimeHorizon.SEMANAL: 7,
    }

    def __init__(self, tolerance: float = 0.015):
        self.TOLERANCE = tolerance

    def find_swing_points(self, df: pd.DataFrame, window: int = 5) -> Tuple[float, float]:
        """
        Encontra swing high e swing low usando pivôs de janela deslizante.

        Args:
            df: DataFrame com colunas 'high', 'low', 'close'
            window: janela para detectar pivôs (padrão: 5 candles)

        Returns:
            (swing_high, swing_low)
        """
        highs = df['high'].values
        lows = df['low'].values

        # Detectar pivôs de topo
        pivot_highs = []
        for i in range(window, len(highs) - window):
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                pivot_highs.append((i, highs[i]))

        # Detectar pivôs de fundo
        pivot_lows = []
        for i in range(window, len(lows) - window):
            if all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1)):
                pivot_lows.append((i, lows[i]))

        if not pivot_highs or not pivot_lows:
            # Fallback: usar máximo/mínimo do período
            return df['high'].max(), df['low'].min()

        # Pegar o swing high e low mais significativos (mais recentes com maior amplitude)
        swing_high = max(pivot_highs, key=lambda x: x[1])[1]
        swing_low = min(pivot_lows, key=lambda x: x[1])[1]

        return swing_high, swing_low

    def calculate_fibonacci_levels(self, swing_high: float, swing_low: float, 
                                    direction: str = "retracement") -> List[Tuple[float, float]]:
        """
        Calcula níveis Fibonacci.

        Args:
            swing_high: preço do topo
            swing_low: preço do fundo
            direction: "retracement" ou "extension"

        Returns:
            Lista de (nível, preço)
        """
        range_price = swing_high - swing_low
        levels = []

        if direction == "retracement":
            for level in self.FIB_LEVELS:
                price = swing_high - (range_price * level)
                levels.append((level, price))
        else:  # extension
            for level in self.EXTENSION_LEVELS:
                price = swing_high + (range_price * (level - 1.0))
                levels.append((level, price))

        return levels

    def analyze_horizon(self, df: pd.DataFrame, horizon: TimeHorizon) -> List[FibZone]:
        """
        Analisa um horizonte temporal específico e retorna zonas Fibonacci.

        Args:
            df: DataFrame completo de OHLCV
            horizon: horizonte temporal a analisar

        Returns:
            Lista de FibZones
        """
        n_periods = self.HORIZON_PERIODS[horizon]
        df_horizon = df.tail(n_periods).copy()

        if len(df_horizon) < 10:
            return []

        swing_high, swing_low = self.find_swing_points(df_horizon)

        zones = []

        # Retrações (tendência de baixa: high -> low)
        retracement_levels = self.calculate_fibonacci_levels(swing_high, swing_low, "retracement")
        for level, price in retracement_levels:
            zones.append(FibZone(
                price=price,
                level=level,
                horizon=horizon,
                swing_high=swing_high,
                swing_low=swing_low,
                direction="retracement"
            ))

        # Extensões (projeção além do swing high)
        extension_levels = self.calculate_fibonacci_levels(swing_high, swing_low, "extension")
        for level, price in extension_levels:
            zones.append(FibZone(
                price=price,
                level=level,
                horizon=horizon,
                swing_high=swing_high,
                swing_low=swing_low,
                direction="extension"
            ))

        return zones

    def find_confluences(self, all_zones: List[FibZone], current_price: float) -> List[SuperZone]:
        """
        Encontra zonas onde múltiplos Fibonaccis convergem.

        Algoritmo:
        1. Agrupa zonas que estão dentro da tolerância (±1.5%)
        2. Para cada grupo, calcula score baseado em:
           - Número de confluências (peso 50%)
           - Diversidade de horizontes temporais (peso 30%)
           - Proximidade com preço atual (peso 20%)
        3. Classifica em CRITICAL/HIGH/MEDIUM/OBSERVATION

        Args:
            all_zones: todas as zonas Fib de todos os horizontes
            current_price: preço atual do ativo

        Returns:
            Lista de SuperZones ordenadas por score
        """
        if not all_zones:
            return []

        # Ordenar por preço
        sorted_zones = sorted(all_zones, key=lambda z: z.price)

        # Agrupar por proximidade
        clusters = []
        current_cluster = [sorted_zones[0]]

        for zone in sorted_zones[1:]:
            # Verificar se está dentro da tolerância do centro do cluster
            cluster_center = np.mean([z.price for z in current_cluster])
            tolerance_price = cluster_center * self.TOLERANCE

            if abs(zone.price - cluster_center) <= tolerance_price:
                current_cluster.append(zone)
            else:
                clusters.append(current_cluster)
                current_cluster = [zone]

        if current_cluster:
            clusters.append(current_cluster)

        # Criar SuperZones a partir dos clusters
        super_zones = []

        for cluster in clusters:
            if len(cluster) < 1:
                continue

            prices = [z.price for z in cluster]
            center = np.mean(prices)
            bottom = min(prices) * 0.995
            top = max(prices) * 1.005

            # Calcular score
            confluence_count = len(cluster)
            unique_horizons = len(set(z.horizon for z in cluster))
            unique_levels = len(set(round(z.level, 3) for z in cluster))

            # Peso 1: Confluência (quantos fibs) - normalizado 0-50
            score_confluence = min(confluence_count * 12, 50)

            # Peso 2: Diversidade de horizontes - normalizado 0-30
            score_diversity = unique_horizons * 5  # max 6*5 = 30

            # Peso 3: Proximidade com preço atual - normalizado 0-20
            price_distance = abs(center - current_price) / current_price
            score_proximity = max(0, 20 - (price_distance * 1000))  # decai rápido

            total_score = int(score_confluence + score_diversity + score_proximity)
            total_score = min(100, max(0, total_score))

            # Classificar tipo de zona
            if confluence_count >= 4 and unique_horizons >= 3:
                zone_type = ZoneType.CRITICAL
            elif confluence_count >= 3 and unique_horizons >= 2:
                zone_type = ZoneType.HIGH
            elif confluence_count >= 2:
                zone_type = ZoneType.MEDIUM
            else:
                zone_type = ZoneType.OBSERVATION

            # Gerar descrição
            horizons_str = ", ".join(sorted(set(z.horizon.value for z in cluster)))
            levels_str = ", ".join([f"{z.level:.3f}" for z in sorted(cluster, key=lambda x: x.level)])

            description = f"Confluência de {confluence_count} níveis Fibonacci. \"
            description += f"Horizontes: {horizons_str}. Níveis: {levels_str}"

            super_zones.append(SuperZone(
                center_price=center,
                price_bottom=bottom,
                price_top=top,
                score=total_score,
                zone_type=zone_type,
                confluence_count=confluence_count,
                fib_zones=cluster,
                timeframes=sorted(set(z.horizon.value for z in cluster)),
                description=description
            ))

        # Ordenar por score decrescente
        super_zones.sort(key=lambda z: z.score, reverse=True)

        return super_zones

    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Executa análise completa do Oráculo.

        Args:
            df: DataFrame com dados OHLCV (colunas: open, high, low, close, volume)
            current_price: preço atual do ativo

        Returns:
            Dict com todas as zonas detectadas
        """
        all_fib_zones = []
        horizon_results = {}

        # Analisar cada horizonte temporal
        for horizon in TimeHorizon:
            zones = self.analyze_horizon(df, horizon)
            all_fib_zones.extend(zones)
            horizon_results[horizon.value] = {
                "swing_high": zones[0].swing_high if zones else None,
                "swing_low": zones[0].swing_low if zones else None,
                "zones_count": len(zones),
                "zones": [
                    {"level": z.level, "price": round(z.price, 2), "direction": z.direction}
                    for z in zones
                ]
            }

        # Encontrar confluências
        super_zones = self.find_confluences(all_fib_zones, current_price)

        # Separar por tipo
        critical_zones = [z for z in super_zones if z.zone_type == ZoneType.CRITICAL]
        high_zones = [z for z in super_zones if z.zone_type == ZoneType.HIGH]
        medium_zones = [z for z in super_zones if z.zone_type == ZoneType.MEDIUM]

        return {
            "current_price": current_price,
            "total_fib_zones": len(all_fib_zones),
            "total_super_zones": len(super_zones),
            "critical_zones": [z.to_dict() for z in critical_zones],
            "high_zones": [z.to_dict() for z in high_zones],
            "medium_zones": [z.to_dict() for z in medium_zones],
            "all_zones": [z.to_dict() for z in super_zones],
            "horizons": horizon_results
        }


# ============================================
# EXEMPLO DE USO (para teste local)
# ============================================
if __name__ == "__main__":
    # Criar dados simulados para teste
    np.random.seed(42)
    n = 1000
    prices = 35000 + np.cumsum(np.random.randn(n) * 500)

    df = pd.DataFrame({
        'open': prices + np.random.randn(n) * 100,
        'high': prices + np.abs(np.random.randn(n)) * 300 + 100,
        'low': prices - np.abs(np.random.randn(n)) * 300 - 100,
        'close': prices,
        'volume': np.random.randn(n) * 1000 + 5000
    })

    oracle = FibonacciOracle()
    result = oracle.analyze(df, current_price=df['close'].iloc[-1])

    print("=" * 60)
    print("🎯 ORÁCULO DE ZONAS FIBONACCI")
    print("=" * 60)
    print(f"Preço atual: ${result['current_price']:,.2f}")
    print(f"Total de zonas Fib: {result['total_fib_zones']}")
    print(f"Zonas de confluência: {result['total_super_zones']}")
    print()

    print(f"🔴 Zonas CRÍTICAS ({len(result['critical_zones'])}):")
    for z in result['critical_zones'][:3]:
        print(f"   Score {z['score']} | ${z['price_bottom']:,.0f} - ${z['price_top']:,.0f} | {z['confluence_count']} confluências")
        print(f"   {z['description']}")

    print(f"\n🟡 Zonas HIGH ({len(result['high_zones'])}):")
    for z in result['high_zones'][:3]:
        print(f"   Score {z['score']} | ${z['price_bottom']:,.0f} - ${z['price_top']:,.0f} | {z['confluence_count']} confluências")
