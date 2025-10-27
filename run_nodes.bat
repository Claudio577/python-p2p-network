@echo off
echo Iniciando rede SmartFin Blockchain P2P...
start cmd /k "python node.py 5000"
start cmd /k "python node.py 5001 5000"
start cmd /k "python node.py 5002 5000"
pause
