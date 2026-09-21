@echo off
chcp 65001 >nul
echo ==========================================
echo   ORACULO DE ZONAS - Setup Windows
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale em https://python.org
    pause
    exit /b 1
)

REM Verificar Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado. Instale em https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados
echo.

REM Criar pasta de dados
if not exist "data" mkdir data

REM Backend
echo 📦 Instalando backend...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Baixar dados reais
echo.
echo 📡 Baixando dados reais da Binance...
python fetch_real_data.py

echo.
echo ✅ Backend pronto!
echo.
echo Para iniciar o backend, rode:
echo    cd backend
echo    call venv\Scripts\activate.bat
echo    uvicorn app.main:app --reload --port 8000
echo.

REM Frontend
cd ..\frontend
echo 📦 Instalando frontend...
npm install

echo.
echo ✅ Frontend pronto!
echo.
echo Para iniciar o frontend, rode:
echo    cd frontend
echo    npm run dev
echo.

echo ==========================================
echo   Setup completo! 🎉
echo ==========================================
echo.
echo Proximos passos:
echo 1. Abra 2 terminais no VS Code
echo 2. Terminal 1: cd backend ^&^& call venv\Scripts\activate.bat ^&^& uvicorn app.main:app --reload
echo 3. Terminal 2: cd frontend ^&^& npm run dev
echo 4. Acesse http://localhost:3000
echo.
pause
