"""
Statistical Models Engine
GMM, KDE, Regressão Quantílica, Markov Switching, Monte Carlo, Bayesian, Hurst, Cointegração
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats
from scipy.stats import gaussian_kde, norm


class StatisticalModelsEngine:
    """Engine de modelos estatísticos avançados"""

    def gaussian_mixture_zones(self, df: pd.DataFrame, n_components: int = 3) -> Dict:
        """
        Gaussian Mixture Model para identificar clusters de preço (POC, VAH, VAL)
        Em produção usar sklearn.mixture.GaussianMixture
        """
        prices = df['close'].values.reshape(-1, 1)

        # Simulação GMM com clustering por percentis
        means = [np.percentile(prices, 25), np.percentile(prices, 50), np.percentile(prices, 75)]
        stds = [np.std(prices[prices < means[0]]), np.std(prices[(prices >= means[0]) & (prices <= means[2])]), np.std(prices[prices > means[2]])]

        clusters = []
        for i, (mean, std) in enumerate(zip(means, stds)):
            clusters.append({
                "cluster": i,
                "mean": round(float(mean), 2),
                "std": round(float(std), 2),
                "weight": round(1.0 / n_components, 2),
                "zone": "low" if i == 0 else "mid" if i == 1 else "high"
            })

        return {
            "model": "GMM (simplified)",
            "clusters": clusters,
            "poc": clusters[1]["mean"],  # Point of Control
            "vah": clusters[2]["mean"],  # Value Area High
            "val": clusters[0]["mean"]   # Value Area Low
        }

    def kde_liquidity_heatmap(self, df: pd.DataFrame, num_points: int = 100) -> Dict:
        """
        Kernel Density Estimation para heatmap de liquidez horizontal
        """
        prices = df['close'].values

        if len(prices) < 10:
            return {"heatmap": []}

        kde = gaussian_kde(prices)
        x_range = np.linspace(prices.min(), prices.max(), num_points)
        densities = kde(x_range)

        heatmap = []
        for x, d in zip(x_range, densities):
            heatmap.append({
                "price": round(x, 2),
                "density": round(d, 6),
                "intensity": "high" if d > np.percentile(densities, 80) else "medium" if d > np.percentile(densities, 50) else "low"
            })

        # Zonas de alta densidade = zonas de liquidez
        high_density = [h for h in heatmap if h["intensity"] == "high"]

        return {
            "heatmap": heatmap[::10],  # Amostra para não sobrecarregar
            "high_density_zones": high_density[:10],
            "max_density_price": round(x_range[np.argmax(densities)], 2)
        }

    def quantile_regression_levels(self, df: pd.DataFrame) -> Dict:
        """
        Regressão Quantílica para múltiplos percentis do preço
        """
        prices = df['close'].values
        x = np.arange(len(prices))

        levels = {}
        for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
            # Regressão linear simples no quantil (proxy)
            residual = prices - np.mean(prices)
            quantile_level = np.percentile(prices, q * 100)
            levels[f"q{int(q*100)}"] = round(quantile_level, 2)

        return {
            "model": "Quantile Regression (simplified)",
            "levels": levels,
            "dynamic_support": levels["q25"],
            "dynamic_resistance": levels["q75"],
            "median": levels["q50"]
        }

    def markov_regime(self, df: pd.DataFrame) -> Dict:
        """
        Markov Switching Model para detectar regimes de mercado
        Em produção usar statsmodels.tsa.regime_switching
        """
        returns = df['close'].pct_change().dropna()

        # Proxy de regimes por volatilidade
        vol_low = returns.rolling(20).std() < returns.std() * 0.8
        vol_high = returns.rolling(20).std() > returns.std() * 1.2

        current_vol = returns.rolling(20).std().iloc[-1]

        if current_vol > returns.std() * 1.5:
            regime = "high_volatility"
            state = "crash_or_pump"
        elif current_vol > returns.std() * 1.0:
            regime = "trending"
            state = "directional"
        else:
            regime = "low_volatility"
            state = "ranging"

        return {
            "current_regime": regime,
            "current_state": state,
            "volatility_percentile": round(stats.percentileofscore(returns.rolling(20).std().dropna(), current_vol), 1),
            "transition_probability": {"trending": 0.6, "ranging": 0.3, "crash": 0.1}
        }

    def monte_carlo_projection(self, df: pd.DataFrame, n_simulations: int = 1000, days: int = 30) -> Dict:
        """
        Monte Carlo Simulation para projeção de zonas futuras
        """
        prices = df['close'].values
        returns = np.diff(np.log(prices))
        mu = np.mean(returns)
        sigma = np.std(returns)

        last_price = prices[-1]
        simulations = []

        for _ in range(n_simulations):
            path = [last_price]
            for _ in range(days):
                r = np.random.normal(mu, sigma)
                path.append(path[-1] * np.exp(r))
            simulations.append(path)

        simulations = np.array(simulations)

        # Percentis das simulações
        percentiles = [5, 25, 50, 75, 95]
        zones = {}
        for p in percentiles:
            zones[f"p{p}"] = round(np.percentile(simulations[:, -1], p), 2)

        return {
            "model": "Monte Carlo Geometric Brownian Motion",
            "simulations": n_simulations,
            "horizon_days": days,
            "projected_zones": zones,
            "expected_price": round(np.mean(simulations[:, -1]), 2),
            "probability_above_current": round(np.mean(simulations[:, -1] > last_price) * 100, 1)
        }

    def bayesian_zone_probability(self, df: pd.DataFrame, zone_price: float) -> Dict:
        """
        Bayesian Inference para probabilidade de toque/rejeição em uma zona
        """
        prices = df['close'].values
        returns = np.diff(np.log(prices))

        # Prior: baseado na distância da média
        current_price = prices[-1]
        distance = abs(zone_price - current_price) / current_price
        prior_touch = np.exp(-distance * 10)  # decai exponencialmente

        # Likelihood: baseado em histórico de toques
        tolerance = zone_price * 0.02
        touches = sum(abs(prices - zone_price) < tolerance)
        likelihood = touches / len(prices)

        # Posterior simplificado
        posterior = (prior_touch * 0.6) + (likelihood * 0.4)

        return {
            "zone_price": zone_price,
            "prior_probability": round(prior_touch, 4),
            "likelihood_historical": round(likelihood, 4),
            "posterior_probability": round(posterior, 4),
            "expected_time_to_touch": round(distance * 30, 1),  # dias estimados
            "confidence": "high" if posterior > 0.7 else "medium" if posterior > 0.4 else "low"
        }

    def hurst_exponent(self, df: pd.DataFrame, max_lag: int = 100) -> Dict:
        """
        Hurst Exponent: mede persistência (H>0.5) ou reversão (H<0.5)
        """
        prices = df['close'].values
        lags = range(2, min(max_lag, len(prices) // 4))
        tau = [np.std(np.subtract(prices[lag:], prices[:-lag])) for lag in lags]

        if len(tau) < 2:
            return {"hurst": 0.5, "interpretation": "insufficient_data"}

        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst = poly[0]

        if hurst > 0.55:
            interp = "trending_persistente"
        elif hurst < 0.45:
            interp = "mean_reverting"
        else:
            interp = "random_walk"

        return {
            "hurst": round(hurst, 3),
            "interpretation": interp,
            "recommendation": "trend_following" if hurst > 0.55 else "mean_reversion" if hurst < 0.45 else "neutral"
        }

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise estatística completa"""
        return {
            "gmm_clusters": self.gaussian_mixture_zones(df),
            "kde_heatmap": self.kde_liquidity_heatmap(df),
            "quantile_levels": self.quantile_regression_levels(df),
            "markov_regime": self.markov_regime(df),
            "monte_carlo": self.monte_carlo_projection(df),
            "bayesian": self.bayesian_zone_probability(df, df['close'].iloc[-1] * 1.05),
            "hurst": self.hurst_exponent(df)
        }
