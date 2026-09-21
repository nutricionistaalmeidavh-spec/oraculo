# ◈ Oráculo de Zonas

**SaaS de identificação de zonas de interesse em criptoativos** usando análise estatística avançada, Fibonacci multi-timeframe, Market Makers, Gann e Wyckoff.

---

## 🎯 O que é o Oráculo?

O **Oráculo de Zonas** é um sistema que detecta automaticamente zonas de alta probabilidade de reação em **BTC, ETH e SOL**. Ele cruza **múltiplos horizontes temporais** (ciclo completo, 1 ano, 6 meses, 3 meses, 1 mês, semanal) e exige **confluência de pelo menos 3 níveis Fibonacci** na mesma região de preço para gerar um sinal.

### Conceito Central: Confluência Fibonacci

Em vez de traçar uma única retração Fibonacci, o Oráculo:
1. Calcula Fibonaccis em **6 horizontes temporais diferentes**
2. Busca **sobreposição** entre níveis de horizontes diferentes
3. Atribui um **score 0-100** baseado em:
   - Quantos Fibs convergem (40%)
   - Diversidade de horizontes (30%)
   - Proximidade com preço atual (20%)
   - Força estatística (10%)

---

## 📁 Estrutura do Projeto

```
oraculo-zonas/
├── backend/                 # FastAPI + Algoritmos
│   ├── app/
│   │   ├── algorithms/      # Motor do Oráculo
│   │   │   └── fibonacci_oracle.py   # ⭐ CORAÇÃO DO SISTEMA
│   │   ├── api/             # Endpoints REST
│   │   │   ├── zones.py
│   │   │   ├── analysis.py
│   │   │   ├── alerts.py
│   │   │   └── backtest.py
│   │   ├── services/        # Ingestão de dados
│   │   │   └── data_ingestion.py
│   │   └── main.py          # Entry point FastAPI
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/                # Next.js 14 + React
│   ├── app/
│   │   ├── components/      # UI Components
│   │   │   ├── AssetSelector.tsx
│   │   │   ├── ZoneChart.tsx
│   │   │   ├── ZonesPanel.tsx
│   │   │   └── ZoneStats.tsx
│   │   ├── page.tsx         # Dashboard principal
│   │   ├── layout.tsx
│   │   └── types.ts
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml       # Orquestra tudo
└── README.md
```

---

## 🚀 Instalação Rápida

### Opção 1: Docker (Recomendado)

```bash
# 1. Clone/extraia o projeto
cd oraculo-zonas

# 2. Suba tudo com Docker Compose
docker-compose up --build

# 3. Acesse:
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Opção 2: VS Code (Desenvolvimento)

#### Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Rodar
npm run dev

# Acesse: http://localhost:3000
```

---

## 🔬 Algoritmo Principal: `fibonacci_oracle.py`

O coração do sistema está em `backend/app/algorithms/fibonacci_oracle.py`.

### Como funciona:

```python
from app.algorithms.fibonacci_oracle import FibonacciOracle
import pandas as pd

# Carregar dados OHLCV
df = pd.read_csv("btc_daily.csv")

# Inicializar o Oráculo
oracle = FibonacciOracle(tolerance=0.015)  # 1.5% de tolerância

# Analisar
result = oracle.analyze(df, current_price=118000)

# Resultado
print(result['critical_zones'])
# Zonas onde 4+ Fibonaccis de horizontes diferentes convergem
```

### Horizontes Temporais Analisados:

| Horizonte | Candles (Diário) | Descrição |
|-----------|------------------|-----------|
| Ciclo Completo | 1000 | ~3 anos de histórico |
| 1 Ano | 365 | Último ano |
| 6 Meses | 180 | Semestre |
| 3 Meses | 90 | Trimestre |
| 1 Mês | 30 | Mês atual |
| Semanal | 7 | Últimas 4 semanas |

### Níveis Fibonacci Calculados:

**Retrações:** 0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0

**Extensões:** 1.0, 1.272, 1.618, 2.0, 2.618, 3.618, 4.236

---

## 📡 API Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/zones/{symbol}` | Todas as zonas detectadas |
| `GET /api/v1/zones/{symbol}/fusion` | Apenas zonas de alta confluência |
| `GET /api/v1/zones/{symbol}/horizons` | Análise por horizonte temporal |
| `GET /api/v1/analysis/{symbol}/wyckoff` | Fase Wyckoff atual |
| `GET /api/v1/analysis/{symbol}/market-makers` | Order Blocks, FVGs, Liquidity |
| `GET /api/v1/analysis/{symbol}/gann` | Níveis Gann |
| `POST /api/v1/alerts/` | Criar alerta de zona |
| `POST /api/v1/backtest/` | Backtest de estratégia |

---

## 🎨 Dashboard

O frontend mostra:
- **Mapa de Zonas**: Chart com zonas sobrepostas e cores por criticidade
- **Score de Confluência**: Barra de 0-100 para cada zona
- **Timeframes**: Dots coloridos indicando quais horizontes convergem
- **Painel Lateral**: Lista detalhada de todas as zonas com descrição

---

## 🔮 Roadmap

- [x] Motor Fibonacci multi-timeframe
- [x] Detecção de confluência (3+ Fibs)
- [x] Score 0-100 por zona
- [x] Dashboard com visualização
- [ ] Integração com dados reais da Binance
- [ ] Zonas de Market Makers (OB, FVG, Liquidity)
- [ ] Análise Wyckoff automática
- [ ] Níveis Gann (Square of 9, Angles)
- [ ] Gaussian Mixture Models para clusters
- [ ] KDE Heatmap de liquidez
- [ ] Alertas em tempo real
- [ ] Backtest engine

---

## 📄 Licença

MIT License - Use à vontade para construir seu próprio Oráculo.

---

**Desenvolvido com ◈ para traders que enxergam além das linhas.**
