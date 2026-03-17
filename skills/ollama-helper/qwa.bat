@echo off
chcp 65001 >nul
cd /d "C:\Users\Administrator\.claude\skills\ollama-helper"
py ollama_auto.py %*
