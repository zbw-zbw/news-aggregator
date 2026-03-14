# Environment Setup Guide

This document provides a comprehensive guide for setting up the development environment for the News Aggregator project, including common issues and their solutions.

## Prerequisites

| Software | Required Version | How to Check |
|----------|------------------|--------------|
| Python | 3.12+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

---

## Environment Setup

### 1. Install Python (Windows)

If Python is not installed, use Windows Package Manager:

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```

After installation, **restart your terminal** or refresh the PATH:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Verify installation:
```powershell
python --version
```

### 2. Install Node.js

Download and install from [nodejs.org](https://nodejs.org/) or use winget:

```powershell
winget install OpenJS.NodeJS.LTS
```

Verify installation:
```powershell
node --version
npm --version
```

---

## Project Setup

### Backend Setup

1. Navigate to the backend directory and create a virtual environment:

```powershell
cd backend
python -m venv venv
```

2. Activate the virtual environment:

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run the backend server:

```powershell
python app.py
```

The backend will be available at `http://127.0.0.1:5001`

### Frontend Setup

1. Navigate to the frontend directory:

```powershell
cd frontend
```

2. Install dependencies:

```powershell
npm install
```

3. Run the development server:

```powershell
npm run dev
```

The frontend will be available at `http://localhost:3000`

---

## Common Issues and Solutions

### Issue 1: Python not found after installation

**Symptom:**
```
python : The term 'python' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Solution:**
- Restart your terminal/PowerShell
- Or manually refresh the PATH environment variable:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Issue 2: PowerShell script execution policy

**Symptom:**
```
.\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Rollup module not found (npm optional dependency bug)

**Symptom:**
```
Error: Cannot find module @rollup/rollup-win32-x64-msvc. npm has a bug related to optional dependencies
```

**Cause:** npm has a known bug with optional dependencies on Windows.

**Solution:**
Delete `node_modules` and `package-lock.json`, then reinstall:

```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Issue 4: Port already in use

**Symptom:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
Find and kill the process using the port:

```powershell
# Find process using port 5001
netstat -ano | findstr :5001

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 5: Virtual environment activation fails

**Symptom:**
```
activate : The term 'activate' is not recognized
```

**Solution:**
Make sure you're in the correct directory and use the full path:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

---

## Quick Start Commands

### Start Backend (from project root)
```powershell
cd backend; .\venv\Scripts\Activate.ps1; python app.py
```

### Start Frontend (from project root)
```powershell
cd frontend; npm run dev
```

---

## Project Structure

```
news-aggregator/
├── backend/
│   ├── app.py           # Flask application entry point
│   ├── crawler.py       # RSS crawler script
│   ├── models.py        # Database models
│   ├── requirements.txt # Python dependencies
│   ├── news.db          # SQLite database
│   └── venv/            # Virtual environment (created during setup)
├── frontend/
│   ├── src/             # Vue.js source code
│   ├── package.json     # Node.js dependencies
│   └── node_modules/    # Dependencies (created during setup)
└── SETUP.md             # This file
```

---

## Dependencies

### Backend (Python)
- flask==3.0.0
- flask-sqlalchemy==3.1.1
- flask-cors==4.0.0
- feedparser==6.0.10
- requests==2.31.0
- gunicorn==21.2.0
- python-dateutil==2.8.2

### Frontend (Node.js)
- vue: ^3.4.0
- vite: ^5.0.0
- @vitejs/plugin-vue: ^5.0.0

---

## Troubleshooting Checklist

- [ ] Python 3.12+ installed and accessible in PATH
- [ ] Node.js 18+ installed
- [ ] Backend virtual environment created and activated
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] No port conflicts (5001 for backend, 3000 for frontend)
- [ ] PowerShell execution policy allows script execution

---

## Additional Resources

- [Python Downloads](https://www.python.org/downloads/)
- [Node.js Downloads](https://nodejs.org/)
- [Vue.js Documentation](https://vuejs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
