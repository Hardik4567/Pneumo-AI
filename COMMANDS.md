# 🫁 PneumoAI - Quick Reference & Commands

## 🚀 Quick Start Commands

### First Time Setup
```bash
# Navigate to project
cd pneumonia_detection_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
pip install -r frontend/requirements.txt
```

### Start Application
```bash
# Run both backend and frontend (RECOMMENDED)
python run_all.py

# Or run separately:

# Terminal 1 - Backend
python startup.py

# Terminal 2 - Frontend
cd frontend
python -m flask run
```

### Access Application
```
Frontend:    http://localhost:5000
Backend API: http://localhost:8000/docs
Health Check: http://localhost:5000/api/health
```

---

## 📋 Important URLs

| URL | Purpose | Status |
|-----|---------|--------|
| http://localhost:5000 | Frontend home | ✅ Working |
| http://localhost:5000/upload | Upload page | ✅ Working |
| http://localhost:5000/results | Results page | ✅ Working |
| http://localhost:5000/history | History page | ✅ Working |
| http://localhost:8000 | Backend root | ✅ Working |
| http://localhost:8000/docs | API documentation | ✅ Working |
| http://localhost:8000/redoc | Alternative API docs | ✅ Working |

---

## 🔧 Environment Configuration

### .env File Location
```
pneumonia_detection_project/.env
```

### Key Settings
```bash
# Backend API URL
BACKEND_URL=http://localhost:8000/api

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=frontend/app.py

# Server Ports
FRONTEND_PORT=5000
BACKEND_PORT=8000
```

---

## 📁 Important File Locations

### Frontend Routes
```
frontend/routes.py
- /               (Home)
- /upload         (Upload page)
- /predict        (Prediction API)
- /results        (Results page)
- /history        (History page)
- /api/health     (Health check)
```

### Frontend Assets
```
static/js/
- upload.js       (File upload handler)
- prediction.js   (Results display)
- history.js      (History manager)

frontend/templates/
- upload.html     (Upload page)
- result.html     (Results page)
- history.html    (History page)
- 404.html        (Error page)
- 500.html        (Error page)
```

### Configuration Files
```
.env              (Environment variables)
frontend/app.py   (Flask config)
frontend/routes.py (Frontend routes)
run_all.py        (Startup script)
```

---

## 🧪 Testing Commands

### Test Backend Connection
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Health check
curl http://localhost:5000/api/health
```

### Test File Upload
```bash
# Upload a test image (Linux/macOS)
curl -X POST http://localhost:5000/predict \
  -F "file=@path/to/image.jpg"

# Or use Python
python -c "
import requests
with open('image.jpg', 'rb') as f:
    r = requests.post('http://localhost:5000/predict', files={'file': f})
    print(r.json())
"
```

---

## 🐛 Debugging Commands

### Check Python Version
```bash
python --version
```

### Check Installed Packages
```bash
pip list
pip list | grep Flask
pip list | grep requests
```

### Check Backend Logs
```bash
# In backend terminal, you'll see logs like:
# INFO: Uvicorn running on http://0.0.0.0:8000
# INFO: Application startup complete
```

### Check Frontend Logs
```bash
# In frontend terminal, you'll see logs like:
# WARNING in app.run(): This is a development server.
# * Running on http://0.0.0.0:5000
```

### Python Interactive Debug
```bash
# Start Python REPL
python

# Test imports
>>> import flask
>>> import requests
>>> print("All imports OK")
```

---

## 📊 Database Configuration

### Check MySQL Connection
```bash
# Verify database settings in .env
cat .env | grep MYSQL

# Test MySQL connection (if installed)
mysql -u root -p -h 127.0.0.1 new_db
```

### Expected Database Settings
```
MYSQL_DB_HOST=127.0.0.1
MYSQL_DB_PORT=3306
MYSQL_DB_USER=root
MYSQL_DB_PASSWORD=root
MYSQL_DB_NAME=new_db
```

---

## 🛑 Stopping Services

### Stop All Services
```bash
# If using run_all.py:
# Press Ctrl+C in the terminal

# If running separately:
# Terminal 1: Ctrl+C (stops backend)
# Terminal 2: Ctrl+C (stops frontend)
```

### Kill Port Processes (If Stuck)

**Windows:**
```cmd
# Find process on port 5000
netstat -ano | findstr :5000

# Kill process by PID
taskkill /PID <PID> /F

# Same for port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
# Find process on port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Same for port 8000
lsof -i :8000
kill -9 <PID>
```

---

## 🔄 Restart Services

```bash
# Deactivate virtual environment
deactivate

# Activate again
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Restart services
python run_all.py
```

---

## 📦 Installing Additional Packages

```bash
# Install new package for backend
pip install package_name
pip freeze >> requirements.txt

# Install new package for frontend
pip install package_name
# Then update frontend/requirements.txt manually
```

---

## 🌐 Accessing from Other Machines

### Configure Host in .env
```bash
FRONTEND_HOST=0.0.0.0  # Accept connections from anywhere
BACKEND_HOST=0.0.0.0   # Accept connections from anywhere
```

### Access from Another Machine
```
Replace 'localhost' with your machine's IP address
Example: http://192.168.1.100:5000
```

### Finding Your IP Address
```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
# or
hostname -I
```

---

## 📝 Useful File Commands

### View File Contents
```bash
cat static/js/upload.js
cat frontend/app.py
cat .env
```

### Edit Files
```bash
# Using VS Code
code static/js/upload.js

# Using nano (Linux/macOS)
nano .env

# Using notepad (Windows)
notepad .env
```

### Create New File
```bash
# Windows
type nul > new_file.py

# Linux/macOS
touch new_file.py
```

---

## 🔍 Common Issues & Solutions

### Issue: Port Already in Use
```bash
# Stop the service using the port
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>

# Or change port in .env
FRONTEND_PORT=5001
BACKEND_PORT=8001
```

### Issue: Module Not Found
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check if module is installed
pip show requests
pip show flask
```

### Issue: Backend Not Responding
```bash
# Check if service is running
curl http://localhost:8000/docs

# Restart the service
# Press Ctrl+C and run: python startup.py
```

### Issue: Frontend Page Blank
```bash
# Clear browser cache (Ctrl+Shift+Del or Cmd+Shift+Del)
# Check browser console (F12 > Console tab)
# Restart Flask: Ctrl+C and run: python -m flask run
```

---

## 📚 Documentation Files

```
SETUP_GUIDE.md          # Complete setup instructions
QUICKSTART.md           # 5-minute quick start
COMPLETION_SUMMARY.md   # Detailed completion report
CHANGES.md              # All changes made
COMMANDS.md             # This file - Quick reference
```

---

## 🎯 Development Workflow

```
1. Make code changes
   ↓
2. Restart affected service (Ctrl+C, rerun)
   ↓
3. Test in browser
   ↓
4. Check console for errors (F12)
   ↓
5. Commit changes
```

---

## ✅ Pre-Deployment Checklist

- [ ] All dependencies installed
- [ ] .env configured correctly
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] Can upload test image
- [ ] Predictions working correctly
- [ ] History saving properly
- [ ] No console errors
- [ ] All pages accessible
- [ ] Mobile responsive

---

## 🚀 Production Deployment

```bash
# 1. Set environment to production
FLASK_ENV=production
FLASK_DEBUG=0

# 2. Use production WSGI server
pip install gunicorn

# 3. Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 frontend.app:app

# 4. Backend with production server
pip install uvicorn

# 5. Run backend with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📞 Quick Help

### Get Help with Flask
```bash
python -c "import flask; print(flask.__version__)"
flask --version
```

### Get Help with Requests
```bash
python -c "import requests; print(requests.__version__)"
```

### Get Help with pip
```bash
pip --version
pip help
pip help install
```

---

## 🎓 Learning Resources

- **Flask:** https://flask.palletsprojects.com/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Bootstrap 5:** https://getbootstrap.com/
- **JavaScript:** https://developer.mozilla.org/en-US/docs/Web/JavaScript

---

**Keep this file handy for quick reference!**

**Version:** 2.4.0 | **Last Updated:** 2024
