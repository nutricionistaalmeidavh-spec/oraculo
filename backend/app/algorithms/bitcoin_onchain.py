"""
Bitcoin On-Chain & Macro Analysis Engine
36 métricas on-chain e macro para contexto de mercado
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime


class BitcoinOnChainEngine:
    """
    Engine de métricas on-chain e macro de Bitcoin
    Nota: Em produção, integrar com APIs (Glassnode, CryptoQuant, etc.)
    Aqui usamos proxies calculados a partir de dados de preço/volume
    """

    def __init__(self):
        self.halving_dates = [
            "2009-01-03",  # Genesis
            "2012-11-28",  # 1º Halving
            "2016-07-09",  # 2º Halving
            "2020-05-11",  # 3º Halving
            "2024-04-19",  # 4º Halving
            "2028-04-01"   # 5º Halving (estimado)
        ]

    def _calculate_realized_price(self, df: pd.DataFrame) -> float:
        """Proxy de Realized Price: média ponderada por volume"""
        return (df['close'] * df['volume']).sum() / df['volume'].sum()

    def mvrv_ratio(self, df: pd.DataFrame) -> Dict:
        """MVRV = Market Cap / Realized Cap (proxy)"""
        market_price = df['close'].iloc[-1]
        realized_price = self._calculate_realized_price(df)
        mvrv = market_price / realized_price if realized_price > 0 else 1.0

        return {
            "mvrv": round(mvrv, 2),
            "market_price": round(market_price, 2),
            "realized_price": round(realized_price, 2),
            "signal": "overvalued" if mvrv > 3.5 else "undervalued" if mvrv < 1.0 else "fair_value",
            "zone": "top" if mvrv > 3.5 else "bottom" if mvrv < 1.0 else "mid"
        }

    def nupl(self, df: pd.DataFrame) -> Dict:
        """Net Unrealized Profit/Loss (proxy)"""
        realized = self._calculate_realized_price(df)
        market = df['close'].iloc[-1]
        nupl = (market - realized) / realized

        return {
            "nupl": round(nupl, 4),
            "signal": "euphoria" if nupl > 0.5 else "hope" if nupl > 0 else "capitulation" if nupl < -0.25 else "hope_fear",
            "zone": "distribution" if nupl > 0.4 else "accumulation" if nupl < 0 else "neutral"
        }

    def sopr(self, df: pd.DataFrame) -> Dict:
        """Spent Output Profit Ratio (proxy via retornos)"""
        returns = df['close'].pct_change().dropna()
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]

        sopr = 1.0 + (positive_returns.mean() + abs(negative_returns.mean())) / 2

        return {
            "sopr": round(sopr, 4),
            "signal": "profit_taking" if sopr > 1.02 else "loss_taking" if sopr < 0.98 else "neutral",
            "trend": "distribution" if sopr > 1.01 else "accumulation" if sopr < 0.99 else "equilibrium"
        }

    def puell_multiple(self, df: pd.DataFrame) -> Dict:
        """Puell Multiple: proxy via volume/price ratio"""
        daily_issuance_proxy = df['volume'].rolling(30).mean()
        current = daily_issuance_proxy.iloc[-1]
        yearly_avg = df['volume'].mean()
        puell = current / yearly_avg if yearly_avg > 0 else 1.0

        return {
            "puell_multiple": round(puell, 2),
            "signal": "sell" if puell > 4 else "buy" if puell < 0.5 else "neutral"
        }

    def mayer_multiple(self, df: pd.DataFrame) -> Dict:
        """Mayer Multiple = preço / SMA 200"""
        sma200 = df['close'].rolling(200).mean().iloc[-1]
        price = df['close'].iloc[-1]
        mm = price / sma200 if sma200 > 0 else 1.0

        return {
            "mayer_multiple": round(mm, 2),
            "sma200": round(sma200, 2),
            "signal": "overbought" if mm > 2.4 else "oversold" if mm < 0.8 else "neutral"
        }

    def pi_cycle_top(self, df: pd.DataFrame) -> Dict:
        """Pi Cycle Top: 111 DMA vs 350 DMA * 2"""
        dma111 = df['close'].rolling(111).mean().iloc[-1]
        dma350 = df['close'].rolling(350).mean().iloc[-1]
        pi_top = dma350 * 2

        return {
            "dma_111": round(dma111, 2),
            "pi_top_line": round(pi_top, 2),
            "distance_to_top": round(((pi_top - dma111) / dma111) * 100, 2),
            "signal": "top_warning" if dma111 > pi_top * 0.95 else "safe"
        }

    def stock_to_flow(self, current_price: float) -> Dict:
        """Stock-to-Flow Model (simplificado)"""
        # Após halving 2024: stock ~19.7M, flow ~164k/ano
        stock = 19700000
        flow = 164062  # 450 BTC/dia * 365
        s2f = stock / flow

        # Modelo S2F: price = exp(3.3 * ln(S2F) + 14.6)
        model_price = np.exp(3.3 * np.log(s2f) + 14.6)
        ratio = current_price / model_price

        return {
            "s2f_ratio": round(s2f, 2),
            "model_price": round(model_price, 2),
            "current_price": current_price,
            "deviation": round((ratio - 1) * 100, 2),
            "signal": "undervalued" if ratio < 0.5 else "overvalued" if ratio > 2 else "fair"
        }

    def halving_cycle(self) -> Dict:
        """Análise de ciclo de halving"""
        now = datetime.now()
        last_halving = datetime(2024, 4, 19)
        next_halving = datetime(2028, 4, 1)

        days_since = (now - last_halving).days
        days_until = (next_halving - now).days
        cycle_progress = days_since / (days_since + days_until)

        # Fases típicas do ciclo
        if cycle_progress < 0.15:
            phase = "accumulation"
        elif cycle_progress < 0.35:
            phase = "early_bull"
        elif cycle_progress < 0.55:
            phase = "mid_bull"
        elif cycle_progress < 0.75:
            phase = "late_bull"
        else:
            phase = "bear_market"

        return {
            "days_since_halving": days_since,
            "days_until_next": days_until,
            "cycle_progress": round(cycle_progress * 100, 1),
            "phase": phase,
            "typical_top_zone": "450-600 days post-halving"
        }

    def rainbow_chart(self, current_price: float) -> Dict:
        """Bitcoin Rainbow Chart (logarithmic regression bands)"""
        # Simplificado: bandas logarítmicas
        x = 16  # anos desde 2010
        base = np.exp(5.8 * np.log(x) + 2)

        bands = {
            "maximum_bubble": round(base * 4, 0),
            "sell": round(base * 2.5, 0),
            "fomo": round(base * 1.8, 0),
            "hodl": round(base * 1.2, 0),
            "accumulate": round(base * 0.8, 0),
            "buy": round(base * 0.5, 0),
            "fire_sale": round(base * 0.3, 0)
        }

        # Determinar banda atual
        current_band = "unknown"
        for band, price in sorted(bands.items(), key=lambda x: x[1]):
            if current_price >= price:
                current_band = band

        return {
            "current_band": current_band,
            "bands": bands,
            "current_price": current_price
        }

    def funding_liquidation_proxy(self, df: pd.DataFrame) -> Dict:
        """Proxy de funding rates e liquidations via volatilidade"""
        returns = df['close'].pct_change().dropna()
        volatility = returns.rolling(7).std().iloc[-1]

        # Alta volatilidade = possível alta funding + liquidations
        funding_proxy = volatility * 100  # proxy

        return {
            "funding_rate_proxy": round(funding_proxy, 4),
            "liquidation_risk": "high" if volatility > returns.std() * 2 else "medium" if volatility > returns.std() else "low",
            "open_interest_proxy": round(df['volume'].iloc[-1] / df['volume'].mean(), 2)
        }

    def analyze(self, df: pd.DataFrame, symbol: str = "BTC") -> Dict:
        """Análise on-chain completa (apenas para BTC)"""
        if "BTC" not in symbol.upper():
            return {"error": "On-chain metrics only available for BTC"}

        current_price = df['close'].iloc[-1]

        return {
            "mvrv": self.mvrv_ratio(df),
            "nupl": self.nupl(df),
            "sopr": self.sopr(df),
            "puell_multiple": self.puell_multiple(df),
            "mayer_multiple": self.mayer_multiple(df),
            "pi_cycle_top": self.pi_cycle_top(df),
            "stock_to_flow": self.stock_to_flow(current_price),
            "halving_cycle": self.halving_cycle(),
            "rainbow_chart": self.rainbow_chart(current_price),
            "funding_liquidation": self.funding_liquidation_proxy(df),
            "summary": {
                "market_phase": self._determine_market_phase(df),
                "risk_level": self._calculate_risk_level(df),
                "recommendation": self._generate_recommendation(df)
            }
        }

    def _determine_market_phase(self, df: pd.DataFrame) -> str:
        """Determina fase do mercado combinando métricas"""
        mvrv = self.mvrv_ratio(df)['mvrv']
        nupl = self.nupl(df)['nupl']

        if mvrv > 3.0 and nupl > 0.5:
            return "euphoria_distribution"
        elif mvrv < 1.0 and nupl < 0:
            return "capitulation_accumulation"
        elif mvrv > 1.5:
            return "bull_market"
        else:
            return "transition"

    def _calculate_risk_level(self, df: pd.DataFrame) -> str:
        """Calcula nível de risco composto"""
        mm = self.mayer_multiple(df)['mayer_multiple']
        mvrv = self.mvrv_ratio(df)['mvrv']

        risk_score = 0
        if mm > 2.0: risk_score += 3
        elif mm > 1.5: risk_score += 2

        if mvrv > 3.0: risk_score += 3
        elif mvrv > 2.0: risk_score += 2

        if risk_score >= 5: return "very_high"
        if risk_score >= 3: return "high"
        if risk_score >= 1: return "medium"
        return "low"

    def _generate_recommendation(self, df: pd.DataFrame) -> str:
        """Gera recomendação baseada em todas as métricas"""
        phase = self._determine_market_phase(df)
        risk = self._calculate_risk_level(df)

        if phase == "capitulation_accumulation" and risk == "low":
            return "Forte sinal de acumulação. Múltiplas métricas on-chain indicam fundo de mercado."
        elif phase == "euphoria_distribution" and risk == "very_high":
            return "Alerta de distribuição. Considere realização de lucros."
        else:
            return "Mercado em fase de transição. Aguardar confirmação de múltiplas métricas."
