@echo off
set VENV_PYTHON=resume_agent\.venv\Scripts\python.exe

echo Starting Resume Screening Agent...
echo Using Python at: %VENV_PYTHON%

%VENV_PYTHON% -c "import pdfplumber" 2>NUL
if %errorlevel% neq 0 (
    echo Installing missing pdfplumber...
    %VENV_PYTHON% -m pip install pdfplumber
)

%VENV_PYTHON% -c "import sentence_transformers" 2>NUL
if %errorlevel% neq 0 (
    echo Installing missing sentence-transformers...
    %VENV_PYTHON% -m pip install sentence-transformers
)

%VENV_PYTHON% -c "import streamlit" 2>NUL
if %errorlevel% neq 0 (
    echo Installing missing streamlit...
    %VENV_PYTHON% -m pip install streamlit
)

echo Launching Streamlit App...
%VENV_PYTHON% -m streamlit run resume_agent/app.py
pause
