@echo off

echo =====================================
echo Library Management System Launcher
echo =====================================

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

IF NOT EXIST library.db (
    echo Creating database...
    python -c "import sqlite3; conn = sqlite3.connect('library.db'); conn.executescript(open('final_schema.sql').read()); conn.commit(); conn.close()"
)

echo Starting Flask application...

start http://127.0.0.1:5000

python app.py