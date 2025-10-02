@echo off
echo Fixing spaCy installation for Windows...
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo No virtual environment found. Please run setup_windows.bat first.
    pause
    exit /b 1
)

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Uninstall and reinstall spaCy with proper Windows dependencies
echo.
echo Reinstalling spaCy...
pip uninstall -y spacy
pip install spacy==3.7.6

REM Download the English language model
echo.
echo Downloading spaCy English language model...
python -m spacy download en_core_web_sm

REM Verify installation
echo.
echo Verifying spaCy installation...
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy successfully installed with en_core_web_sm model!')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: spaCy and language model installed correctly!
    echo Semantic analysis should now work properly.
) else (
    echo.
    echo ERROR: spaCy installation verification failed.
    echo Please try the manual installation steps below:
    echo.
    echo 1. Activate your virtual environment:
    echo    .venv\Scripts\activate
    echo.
    echo 2. Install Microsoft C++ Build Tools if not already installed:
    echo    Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo 3. Install spaCy:
    echo    pip install --no-cache-dir spacy==3.7.6
    echo.
    echo 4. Download the language model:
    echo    python -m spacy download en_core_web_sm
)

echo.
pause