@echo off
echo Starting Blockchain Voting System...
echo.
echo Activating virtual environment...
call .venv\Scripts\activate
echo.
echo Starting Flask application...
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
