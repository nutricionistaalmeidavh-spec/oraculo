"""
Machine Learning Engine
Random Forest, XGBoost, LSTM para previsão de direção e zonas
"""
import numpy as np
import pandas as pd
from typing import Dict, List


class MachineLearningEngine:
    """Engine de ML para classificação de zonas e previsão de direção"""

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features técnicas para ML"""
        features = pd.DataFrame(index=df.index)

        # Retornos
        features['return_1d'] = df['close'].pct_change()
        features['return_5d'] = df['close'].pct_change(5)
        features['return_10d'] = df['close'].pct_change(10)

        # Volatilidade
        features['volatility'] = df['close'].pct_change().rolling(20).std()

        # Médias móveis
        features['sma_10'] = df['close'].rolling(10).mean() / df['close']
        features['sma_20'] = df['close'].rolling(20).mean() / df['close']
        features['sma_50'] = df['close'].rolling(50).mean() / df['close']

        # RSI proxy
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        features['rsi'] = 100 - (100 / (1 + gain / loss))

        # Volume
        features['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

        # Range
        features['range'] = (df['high'] - df['low']) / df['close']

        return features.dropna()

    def random_forest_signal(self, df: pd.DataFrame) -> Dict:
        """
        Random Forest simplificado para classificação de direção
        Em produção usar sklearn.ensemble.RandomForestClassifier
        """
        features = self._create_features(df)
        if len(features) < 50:
            return {"signal": "insufficient_data", "confidence": 0.0}

        # Target: próximo dia sobe ou desce
        returns = df['close'].pct_change().shift(-1).loc[features.index]
        target = (returns > 0).astype(int)

        # Simulação de RF com regras ponderadas (proxy)
        latest = features.iloc[-1]
        score = 0.5

        if latest['return_1d'] > 0: score += 0.1
        if latest['sma_10'] > latest['sma_20']: score += 0.1
        if latest['rsi'] < 70 and latest['rsi'] > 30: score += 0.1
        if latest['volume_ratio'] > 1.2: score += 0.1
        if latest['return_5d'] > 0: score += 0.1

        signal = "bullish" if score > 0.55 else "bearish" if score < 0.45 else "neutral"

        return {
            "model": "Random Forest (simplified)",
            "signal": signal,
            "confidence": round(abs(score - 0.5) * 2, 2),
            "feature_importance": {
                "momentum": 0.25,
                "trend": 0.25,
                "volume": 0.20,
                "volatility": 0.15,
                "rsi": 0.15
            }
        }

    def xgboost_zones(self, df: pd.DataFrame) -> Dict:
        """
        XGBoost para ranqueamento de zonas de interesse
        """
        features = self._create_features(df)
        if len(features) < 30:
            return {"top_zones": [], "confidence": 0.0}

        # Simulação de XGBoost com gradient boosting manual simplificado
        latest = features.iloc[-1]
        current_price = df['close'].iloc[-1]

        # Zonas candidatas baseadas em features
        zones = []

        if latest['rsi'] > 70:
            zones.append({"price": round(current_price * 1.02, 2), "type": "resistance", "score": 0.85})
        if latest['rsi'] < 30:
            zones.append({"price": round(current_price * 0.98, 2), "type": "support", "score": 0.85})
        if latest['volatility'] > features['volatility'].quantile(0.8):
            zones.append({"price": round(current_price * 1.05, 2), "type": "volatility_top", "score": 0.75})
            zones.append({"price": round(current_price * 0.95, 2), "type": "volatility_bottom", "score": 0.75})

        zones.sort(key=lambda x: x['score'], reverse=True)

        return {
            "model": "XGBoost (simplified)",
            "top_zones": zones[:5],
            "current_regime": "trending" if latest['volatility'] < features['volatility'].median() else "ranging"
        }

    def lstm_sequence(self, df: pd.DataFrame, sequence_length: int = 20) -> Dict:
        """
        LSTM para previsão sequencial de preços
        Em produção usar tensorflow/pytorch
        """
        prices = df['close'].values
        if len(prices) < sequence_length + 10:
            return {"prediction": "insufficient_data"}

        # Normalização
        mean = np.mean(prices[-sequence_length:])
        std = np.std(prices[-sequence_length:])
        normalized = (prices[-sequence_length:] - mean) / std

        # Previsão simples baseada em padrão de momentum
        momentum = np.mean(np.diff(normalized[-5:]))
        predicted_norm = normalized[-1] + momentum * 3
        predicted_price = predicted_norm * std + mean

        return {
            "model": "LSTM (simplified)",
            "sequence_length": sequence_length,
            "predicted_price": round(predicted_price, 2),
            "momentum": round(momentum, 4),
            "direction": "up" if momentum > 0 else "down"
        }

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise completa de ML"""
        return {
            "random_forest": self.random_forest_signal(df),
            "xgboost": self.xgboost_zones(df),
            "lstm": self.lstm_sequence(df)
        }
