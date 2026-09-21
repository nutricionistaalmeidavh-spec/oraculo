"""
Time Series Engine
ARIMA, GARCH, Prophet para previsão de preços
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta


class TimeSeriesEngine:
    """Engine de séries temporais para previsão"""

    def arima_forecast(self, df: pd.DataFrame, forecast_days: int = 7) -> Dict:
        """
        ARIMA simplificado (AutoRegressive Integrated Moving Average)
        Em produção usar statsmodels.tsa.arima.model.ARIMA
        """
        prices = df['close'].values
        returns = np.diff(np.log(prices))

        # Média móvel simples como proxy AR(1)
        mu = np.mean(returns)
        sigma = np.std(returns)

        last_price = prices[-1]
        forecasts = []

        for i in range(1, forecast_days + 1):
            predicted_return = np.random.normal(mu, sigma)
            predicted_price = last_price * np.exp(predicted_return)
            forecasts.append({
                "day": i,
                "predicted_price": round(predicted_price, 2),
                "confidence_low": round(predicted_price * 0.95, 2),
                "confidence_high": round(predicted_price * 1.05, 2)
            })
            last_price = predicted_price

        return {
            "model": "ARIMA(1,1,1) - simplified",
            "forecast_days": forecast_days,
            "forecasts": forecasts,
            "drift": round(mu * 100, 4),
            "volatility": round(sigma * 100, 4)
        }

    def garch_volatility(self, df: pd.DataFrame, period: int = 20) -> Dict:
        """
        GARCH(1,1) simplificado para modelagem de volatilidade
        """
        returns = df['close'].pct_change().dropna()

        # EWMA como proxy GARCH
        lambda_param = 0.94
        variance = returns.iloc[0] ** 2
        variances = []

        for r in returns.iloc[1:]:
            variance = lambda_param * variance + (1 - lambda_param) * (r ** 2)
            variances.append(variance)

        current_var = variances[-1] if variances else returns.var()
        current_vol = np.sqrt(current_var)

        # Forecast de volatilidade
        long_run_var = returns.var()
        forecast_var = current_var * 0.94 + long_run_var * 0.06

        return {
            "model": "GARCH(1,1) - EWMA proxy",
            "current_volatility": round(current_vol * 100, 2),
            "forecast_volatility": round(np.sqrt(forecast_var) * 100, 2),
            "annualized_vol": round(current_vol * np.sqrt(365) * 100, 2),
            "vol_regime": "high" if current_vol > returns.std() * 1.5 else "normal" if current_vol > returns.std() * 0.5 else "low"
        }

    def prophet_forecast(self, df: pd.DataFrame, forecast_days: int = 7) -> Dict:
        """
        Prophet-style forecast (simplificado)
        Decomposição em tendência + sazonalidade
        """
        prices = df['close'].values
        n = len(prices)

        # Tendência linear
        x = np.arange(n)
        slope, intercept = np.polyfit(x, prices, 1)
        trend = slope * x + intercept

        # Residual (sazonalidade + ruído)
        residual = prices - trend

        # Forecast
        forecasts = []
        for i in range(1, forecast_days + 1):
            future_x = n + i
            trend_pred = slope * future_x + intercept
            # Adicionar sazonalidade média
            seasonal = np.mean(residual[-30:]) if len(residual) >= 30 else np.mean(residual)
            pred = trend_pred + seasonal

            forecasts.append({
                "day": i,
                "predicted_price": round(pred, 2),
                "trend_component": round(trend_pred, 2),
                "seasonal_component": round(seasonal, 2)
            })

        return {
            "model": "Prophet-style (simplified)",
            "trend_slope": round(slope, 2),
            "trend_direction": "up" if slope > 0 else "down",
            "forecasts": forecasts
        }

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise completa de séries temporais"""
        return {
            "arima": self.arima_forecast(df),
            "garch": self.garch_volatility(df),
            "prophet": self.prophet_forecast(df)
        }
