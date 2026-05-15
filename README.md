# Library Management System

## Project Description

This project is a web-based Library Management System developed using Python and Flask. The application is designed to help manage books, library members, and loan records using a relational database.

The system supports CRUD operations, relationship handling between tables, transaction logic for loans, server-side validation, and a dashboard displaying summary statistics.

---

## Features

- Add, update, and delete books
- Manage library members
- Create and manage book loans
- Prevent unavailable books from being loaned again
- Dashboard with summary statistics
- Server-side validation
- Relational database structure in 3NF

---

## Technologies Used

- Python 3
- Flask
- SQLite
- SQLAlchemy
- HTML5
- CSS3
- Bootstrap

---

## Installation Instructions

## Quick Start (Windows)

Windows users can run the application directly using:

```text
run_project.bat
```

This automatically:
- creates the virtual environment
- installs dependencies
- creates the database if needed
- starts the Flask server
- opens the application in the browser

### 1. Clone the Repository

```bash
git clone https://github.com/Gungn1r-G/Library-Management-System.git
cd Library-Management-System
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv venv
```

Mac/Linux:

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

The SQL schema file included in the project is:

```text
final_schema.sql
```

If the `library.db` file already exists, the project can usually be started immediately after installing dependencies.

To create the database manually from the schema file:

Start Python:

```bash
python
```

Then run:

```python
import sqlite3

conn = sqlite3.connect("library.db")

with open("final_schema.sql") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()

exit()
```

---

## Running the Application

Start the Flask server:

```bash
python app.py
```

Open the application in a browser:

```text
http://127.0.0.1:5000
```

---

## Application Navigation

### Dashboard
View summary statistics for books, members, and active loans.

### Books
Add, edit, update, and delete books.

### Members
Manage library member records.

### Loans
Create and view book loan records.

---

## Validation and Transactions

- Empty fields are restricted through server-side validation.
- Loan transactions update book availability when a loan is created.
- Unavailable books cannot be loaned again until returned.

---

## Additional Files

- `NORMALIZATION.md` → 3NF normalization report
- `AI_LOG.md` → AI usage disclosure
- `final_schema.sql` → final relational database schema

---

## Notes

The `.gitignore` file excludes unnecessary folders such as:

```text
venv/
__pycache__/
```