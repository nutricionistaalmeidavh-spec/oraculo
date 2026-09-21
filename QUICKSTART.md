# ⚡ Quick Start - Oráculo de Zonas

## Passo 1: Baixar dados REAIS da Binance

```bash
cd backend
python fetch_real_data.py
```

Isso baixa **dados reais** de BTC, ETH, SOL (diário, 4h, 1h) da API pública da Binance.

> Não precisa de API key! É a API pública.

## Passo 2: Rodar o Backend

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Passo 3: Rodar o Frontend

```bash
cd frontend
npm install
npm run dev
```

## Passo 4: Acessar

- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## ⚠️ Windows: Script Automático

Clique duas vezes em `setup_windows.bat` — ele instala tudo automaticamente.

## 📡 Dados em Tempo Real?

Atualmente: **dados históricos** (atualizados ao rodar `fetch_real_data.py`).

Para dados **em tempo real** (WebSocket), precisamos adicionar o módulo de streaming. Quer que eu implemente?
