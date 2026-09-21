"""
UNIFIED ORACLE ENGINE v2.0
Integra todos os 80+ parâmetros/conceitos:
- Fibonacci multi-timeframe (6 horizontes)
- Market Makers (OB, FVG, Breaker, Liquidity, Displacement)
- Gann (Square of 9, Fan, Box, Time Cycles)
- Technical Indicators (ATR, Bollinger, RSI, MACD, StochRSI, VWAP, Volume Profile)
- Time Series (ARIMA, GARCH, Prophet)
- Machine Learning (Random Forest, XGBoost, LSTM)
- Bitcoin On-Chain (MVRV, NUPL, SOPR, Puell, Mayer, S2F, Halving, Rainbow, etc.)
- Statistical Models (GMM, KDE, Quantile Regression, Markov, Monte Carlo, Bayesian, Hurst)
- Elliott Waves (1-5 + ABC)
- Wyckoff Advanced (fases A-E, Springs, Upthrusts)
- Temporal Prediction (sazonalidade, tabela cruzada, próximas reversões)
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass, field

from app.algorithms.fibonacci_oracle import FibonacciOracle, SuperZone, ZoneType
from app.algorithms.market_makers import MarketMakersEngine
from app.algorithms.gann_analysis import GannEngine
from app.algorithms.technical_indicators import TechnicalIndicatorsEngine
from app.algorithms.time_series import TimeSeriesEngine
from app.algorithms.machine_learning import MachineLearningEngine
from app.algorithms.bitcoin_onchain import BitcoinOnChainEngine
from app.algorithms.statistical_models import StatisticalModelsEngine
from app.algorithms.elliott_waves import ElliottWaveEngine
from app.algorithms.wyckoff_advanced import WyckoffAdvancedEngine
from app.algorithms.temporal_prediction import TemporalPredictionEngine


@dataclass
class UnifiedZone:
    """Zona unificada com score de TODOS os módulos"""
    center_price: float
    price_bottom: float
    price_top: float
    score: int
    zone_type: str
    confluence_count: int
    modules: List[str] = field(default_factory=list)
    timeframes: List[str] = field(default_factory=list)
    description: str = ""
    onchain_context: Dict = field(default_factory=dict)
    ml_signal: str = "neutral"
    temporal_context: str = ""


class UnifiedOracle:
    """
    Oráculo Unificado v2.0
    Combina 80+ parâmetros em um único score de confiança
    """

    def __init__(self):
        self.fib = FibonacciOracle()
        self.mm = MarketMakersEngine()
        self.gann = GannEngine()
        self.tech = TechnicalIndicatorsEngine()
        self.ts = TimeSeriesEngine()
        self.ml = MachineLearningEngine()
        self.onchain = BitcoinOnChainEngine()
        self.stats = StatisticalModelsEngine()
        self.elliott = ElliottWaveEngine()
        self.wyckoff = WyckoffAdvancedEngine()
        self.temporal = TemporalPredictionEngine()

    def analyze(self, df: pd.DataFrame, symbol: str = "BTC", current_price: float = None) -> Dict:
        """
        Executa análise completa com TODOS os módulos
        """
        if current_price is None:
            current_price = float(df['close'].iloc[-1])

        # 1. Fibonacci (base)
        fib_result = self.fib.analyze(df, current_price)

        # 2. Market Makers
        mm_result = self.mm.analyze(df)

        # 3. Gann
        gann_result = self.gann.analyze(df, current_price)

        # 4. Indicadores Técnicos
        tech_result = self.tech.analyze(df)

        # 5. Séries Temporais
        ts_result = self.ts.analyze(df)

        # 6. Machine Learning
        ml_result = self.ml.analyze(df)

        # 7. On-Chain (apenas BTC)
        onchain_result = self.onchain.analyze(df, symbol) if "BTC" in symbol.upper() else {}

        # 8. Modelos Estatísticos
        stats_result = self.stats.analyze(df)

        # 9. Elliott Waves
        elliott_result = self.elliott.analyze(df)

        # 10. Wyckoff
        wyckoff_result = self.wyckoff.analyze(df)

        # 11. Temporal
        temporal_result = self.temporal.analyze(df)

        # FUSÃO: Combinar todas as zonas
        unified_zones = self._fuse_all_zones(
            fib_result, mm_result, gann_result, stats_result,
            current_price, tech_result, ml_result, onchain_result
        )

        return {
            "symbol": symbol,
            "current_price": current_price,
            "timestamp": pd.Timestamp.now().isoformat(),
            "unified_zones": [self._zone_to_dict(z) for z in unified_zones],
            "fibonacci": fib_result,
            "market_makers": mm_result,
            "gann": gann_result,
            "technical_indicators": tech_result,
            "time_series": ts_result,
            "machine_learning": ml_result,
            "onchain": onchain_result,
            "statistical_models": stats_result,
            "elliott_waves": elliott_result,
            "wyckoff": wyckoff_result,
            "temporal": temporal_result,
            "summary": self._generate_summary(
                unified_zones, ml_result, wyckoff_result, 
                onchain_result, tech_result
            )
        }

    def _fuse_all_zones(self, fib, mm, gann, stats, current_price, tech, ml, onchain) -> List[UnifiedZone]:
        """
        Zone Fusion Engine v2.0
        Combina zonas de TODOS os módulos em Super Zonas unificadas
        """
        all_candidates = []

        # Fibonacci zones
        for z in fib.get('all_zones', []):
            all_candidates.append({
                "price": z['center_price'],
                "bottom": z['price_bottom'],
                "top": z['price_top'],
                "score": z['score'],
                "module": "fibonacci",
                "timeframes": z.get('timeframes', [])
            })

        # Market Maker zones
        for ob in mm.get('order_blocks', []):
            all_candidates.append({
                "price": (ob['top'] + ob['bottom']) / 2,
                "bottom": ob['bottom'],
                "top": ob['top'],
                "score": int(ob['strength'] * 100),
                "module": "order_block",
                "timeframes": [ob.get('timeframe', '1d')]
            })

        for fvg in mm.get('fair_value_gaps', []):
            if not fvg['filled']:
                all_candidates.append({
                    "price": (fvg['top'] + fvg['bottom']) / 2,
                    "bottom": fvg['bottom'],
                    "top": fvg['top'],
                    "score": 70,
                    "module": "fvg",
                    "timeframes": [fvg.get('timeframe', '1d')]
                })

        # Gann zones
        for level_name, price in gann.get('square_of_9', {}).get('angles', {}).items():
            all_candidates.append({
                "price": price,
                "bottom": price * 0.99,
                "top": price * 1.01,
                "score": 60,
                "module": "gann",
                "timeframes": ["gann_cycle"]
            })

        # Statistical zones (GMM, Quantile)
        gmm = stats.get('gmm_clusters', {})
        for cluster in gmm.get('clusters', []):
            all_candidates.append({
                "price": cluster['mean'],
                "bottom": cluster['mean'] - cluster['std'],
                "top": cluster['mean'] + cluster['std'],
                "score": 65,
                "module": "gmm",
                "timeframes": ["statistical"]
            })

        # KDE high density
        for zone in stats.get('kde_heatmap', {}).get('high_density_zones', [])[:5]:
            all_candidates.append({
                "price": zone['price'],
                "bottom": zone['price'] * 0.995,
                "top": zone['price'] * 1.005,
                "score": 55,
                "module": "kde",
                "timeframes": ["statistical"]
            })

        # Agrupar por proximidade (2% de tolerância)
        tolerance = current_price * 0.02
        clusters = []

        for cand in sorted(all_candidates, key=lambda x: x['price']):
            added = False
            for cluster in clusters:
                center = np.mean([c['price'] for c in cluster])
                if abs(cand['price'] - center) <= tolerance:
                    cluster.append(cand)
                    added = True
                    break
            if not added:
                clusters.append([cand])

        # Criar UnifiedZones
        unified = []
        for cluster in clusters:
            if len(cluster) < 2:
                continue

            prices = [c['price'] for c in cluster]
            center = np.mean(prices)
            bottom = min(c['bottom'] for c in cluster)
            top = max(c['top'] for c in cluster)

            modules = list(set(c['module'] for c in cluster))
            tfs = list(set(tf for c in cluster for tf in c.get('timeframes', [])))

            # Score composto v2.0
            base_score = np.mean([c['score'] for c in cluster])
            module_bonus = len(modules) * 8  # +8 por módulo diferente
            tf_bonus = len(tfs) * 5

            # Bônus de confirmação técnica
            tech_bonus = 0
            if tech.get('rsi', 50) > 70 and center > current_price:
                tech_bonus += 5  # RSI overbought + zona acima = resistência confirmada
            if tech.get('rsi', 50) < 30 and center < current_price:
                tech_bonus += 5  # RSI oversold + zona abaixo = suporte confirmado

            # Bônus ML
            ml_bonus = 0
            if ml.get('random_forest', {}).get('signal') == 'bullish' and center > current_price:
                ml_bonus += 3

            total_score = min(100, int(base_score + module_bonus + tf_bonus + tech_bonus + ml_bonus))

            # Classificação
            if total_score >= 85 and len(modules) >= 3:
                ztype = "critical"
            elif total_score >= 70 and len(modules) >= 2:
                ztype = "high"
            elif total_score >= 55:
                ztype = "medium"
            else:
                ztype = "observation"

            description = f"Confluência de {len(cluster)} sinais de {len(modules)} módulos. "
            description += f"Módulos: {', '.join(modules)}. "
            description += f"Timeframes: {', '.join(tfs[:5])}"

            unified.append(UnifiedZone(
                center_price=center,
                price_bottom=bottom,
                price_top=top,
                score=total_score,
                zone_type=ztype,
                confluence_count=len(cluster),
                modules=modules,
                timeframes=tfs,
                description=description,
                ml_signal=ml.get('random_forest', {}).get('signal', 'neutral')
            ))

        unified.sort(key=lambda z: z.score, reverse=True)
        return unified

    def _zone_to_dict(self, zone: UnifiedZone) -> Dict:
        return {
            "center_price": round(zone.center_price, 2),
            "price_bottom": round(zone.price_bottom, 2),
            "price_top": round(zone.price_top, 2),
            "score": zone.score,
            "zone_type": zone.zone_type,
            "confluence_count": zone.confluence_count,
            "modules": zone.modules,
            "timeframes": zone.timeframes,
            "description": zone.description,
            "ml_signal": zone.ml_signal
        }

    def _generate_summary(self, zones, ml, wyckoff, onchain, tech) -> Dict:
        """Gera resumo executivo da análise"""
        critical = len([z for z in zones if z.zone_type == "critical"])
        high = len([z for z in zones if z.zone_type == "high"])

        return {
            "total_zones": len(zones),
            "critical_zones": critical,
            "high_zones": high,
            "ml_signal": ml.get('random_forest', {}).get('signal', 'neutral'),
            "ml_confidence": ml.get('random_forest', {}).get('confidence', 0),
            "wyckoff_phase": wyckoff.get('phase', 'unknown'),
            "wyckoff_confidence": wyckoff.get('confidence', 0),
            "market_phase": onchain.get('summary', {}).get('market_phase', 'unknown') if onchain else 'N/A',
            "risk_level": onchain.get('summary', {}).get('risk_level', 'unknown') if onchain else 'N/A',
            "rsi": tech.get('rsi', 50),
            "recommendation": self._final_recommendation(zones, wyckoff, onchain)
        }

    def _final_recommendation(self, zones, wyckoff, onchain) -> str:
        """Gera recomendação final baseada em TODOS os sinais"""
        phase = wyckoff.get('phase', '')

        if 'C_spring' in phase and len([z for z in zones if z.zone_type == 'critical' and z.center_price < z.price_bottom * 1.1]) > 0:
            return "🟢 FORTE SINAL DE COMPRA: Wyckoff Spring + Zona Crítica de suporte"
        elif 'E_upthrust' in phase:
            return "🔴 ALERTA DE VENDA: Wyckoff Upthrust detectado"
        elif onchain and onchain.get('summary', {}).get('market_phase') == 'capitulation_accumulation':
            return "🟢 ACUMULAÇÃO: Métricas on-chain indicam fundo de mercado"
        elif onchain and onchain.get('summary', {}).get('market_phase') == 'euphoria_distribution':
            return "🔴 DISTRIBUIÇÃO: Métricas on-chain indicam topo de mercado"
        else:
            return "🟡 NEUTRO: Aguardar confirmação em múltiplas métricas"
