@echo off
title Heladería La Dulce 🍦
color 0D
echo ======================================================================
echo                  🍦 HELADERIA LA DULCE - GELATERIA
echo                 Iniciando Sistema de Ventas y Predicciones
echo ======================================================================
echo.
echo [1/2] Verificando e instalando dependencias (Streamlit, Plotly, Pandas)...
pip install -r requirements.txt
echo.
echo [2/2] Abriendo la aplicacion en tu navegador...
echo.
python -m streamlit run app.py
pause
