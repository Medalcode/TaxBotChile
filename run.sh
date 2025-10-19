#!/bin/bash
echo "=== TaxBot Chile MVP ==="
echo ""
echo "1) Instalando dependencias..."
cd "$(dirname "$0")"
pip install -r backend/requirements.txt -q
pip install -r dashboard/requirements.txt -q
echo ""
echo "2) Iniciando Backend (FastAPI) en http://localhost:8000..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..
echo ""
echo "3) Iniciando Dashboard (Streamlit) en http://localhost:8501..."
cd dashboard
streamlit run app.py --server.port 8501 &
DASHBOARD_PID=$!
cd ..
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Dashboard PID: $DASHBOARD_PID"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios"
wait
