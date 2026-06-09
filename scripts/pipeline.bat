@echo off
cd /d "%~dp0\.."
set PYTHONPATH=%CD%
D:\anaconda\anaconda3\python.exe src/pipeline/pipeline.py %*
