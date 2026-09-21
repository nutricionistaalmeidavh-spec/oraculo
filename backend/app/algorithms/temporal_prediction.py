"""
Temporal Prediction Engine
Previsão de dias prováveis de fundos/topos com tabela cruzada
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from collections import defaultdict
from datetime import datetime


class TemporalPredictionEngine:
    """Engine de previsão temporal de reversões"""

    def analyze_seasonality(self, df: pd.DataFrame) -> Dict:
        """
        Analisa sazonalidade por dia da semana e dia do mês
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
        df['day_of_week'] = df['date'].dt.dayofweek  # 0=Seg, 6=Dom
        df['day_of_month'] = df['date'].dt.day
        df['returns'] = df['close'].pct_change()

        # Dia da semana
        dow_stats = df.groupby('day_of_week')['returns'].agg(['mean', 'std', 'count']).to_dict()
        dow_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

        # Dia do mês
        dom_stats = df.groupby('day_of_month')['returns'].agg(['mean', 'std']).to_dict()

        return {
            "day_of_week": {dow_names[k]: {"avg_return": round(v['mean']*100, 3), "volatility": round(v['std']*100, 3)} 
                           for k, v in dow_stats['mean'].items()},
            "day_of_month": {k: {"avg_return": round(dom_stats['mean'][k]*100, 3)} 
                            for k in list(dom_stats['mean'].keys())[:15]}
        }

    def reversal_calendar(self, df: pd.DataFrame) -> Dict:
        """
        Tabela cruzada: dia do mês × dia da semana
        Identifica células com maior probabilidade de fundo/topo
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
        df['dow'] = df['date'].dt.dayofweek
        df['dom'] = df['date'].dt.day
        df['returns'] = df['close'].pct_change()

        # Detectar fundos e topos locais
        df['is_low'] = (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))
        df['is_high'] = (df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))

        # Tabela cruzada para fundos
        low_table = pd.crosstab(df['dom'], df['dow'], values=df['is_low'], aggfunc='sum').fillna(0)
        high_table = pd.crosstab(df['dom'], df['dow'], values=df['is_high'], aggfunc='sum').fillna(0)

        # Encontrar células mais frequentes
        low_max = low_table.stack().idxmax() if not low_table.empty else (1, 0)
        high_max = high_table.stack().idxmax() if not high_table.empty else (15, 0)

        dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        return {
            "most_likely_bottom": {
                "day_of_month": int(low_max[0]),
                "day_of_week": dow_names[int(low_max[1])],
                "confidence": "high"
            },
            "most_likely_top": {
                "day_of_month": int(high_max[0]),
                "day_of_week": dow_names[int(high_max[1])],
                "confidence": "high"
            },
            "seasonal_bottoms": self._get_top_cells(low_table, dow_names, n=5),
            "seasonal_tops": self._get_top_cells(high_table, dow_names, n=5)
        }

    def _get_top_cells(self, table, dow_names, n=5) -> List[Dict]:
        """Extrai top N células da tabela cruzada"""
        stacked = table.stack().sort_values(ascending=False).head(n)
        results = []
        for (dom, dow), count in stacked.items():
            results.append({
                "day_of_month": int(dom),
                "day_of_week": dow_names[int(dow)],
                "frequency": int(count)
            })
        return results

    def next_probable_reversals(self, df: pd.DataFrame, days_ahead: int = 30) -> List[Dict]:
        """
        Lista os próximos dias com maior probabilidade de reversão
        """
        calendar = self.reversal_calendar(df)

        now = datetime.now()
        predictions = []

        for i in range(1, days_ahead + 1):
            future = now + pd.Timedelta(days=i)
            dom = future.day
            dow = future.weekday()

            # Score baseado no calendário
            score = 0
            if calendar['most_likely_bottom']['day_of_month'] == dom:
                score += 3
            if calendar['most_likely_top']['day_of_month'] == dom:
                score += 3

            for bottom in calendar['seasonal_bottoms']:
                if bottom['day_of_month'] == dom:
                    score += 1
            for top in calendar['seasonal_tops']:
                if top['day_of_month'] == dom:
                    score += 1

            if score >= 3:
                predictions.append({
                    "date": future.strftime("%Y-%m-%d"),
                    "day_of_week": future.strftime("%A"),
                    "day_of_month": dom,
                    "score": score,
                    "type": "bottom" if any(b['day_of_month'] == dom for b in calendar['seasonal_bottoms'][:3]) else "top",
                    "confidence": "high" if score >= 4 else "medium"
                })

        return sorted(predictions, key=lambda x: x['score'], reverse=True)[:10]

    def analyze(self, df: pd.DataFrame) -> Dict:
        """Análise temporal completa"""
        return {
            "seasonality": self.analyze_seasonality(df),
            "reversal_calendar": self.reversal_calendar(df),
            "next_probable_reversals": self.next_probable_reversals(df)
        }
