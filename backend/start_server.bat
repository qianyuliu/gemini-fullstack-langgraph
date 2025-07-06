@echo off
echo 🚀 Starting LangGraph server with RAGFlow support...
echo ==================================================

cd /d "%~dp0"
echo Working directory: %CD%

echo Running: langgraph dev --host 0.0.0.0 --port 2024 --allow-blocking
echo ==================================================

langgraph dev --host 0.0.0.0 --port 2024 --allow-blocking

pause 