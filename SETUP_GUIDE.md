# PneumoAI - Pneumonia Detection System - Frontend Setup Guide

## Overview
This document provides comprehensive instructions for setting up and running the complete PneumoAI pneumonia detection system with both backend (FastAPI) and frontend (Flask) applications.

## Project Structure
```
pneumonia_detection_project/
├── app/                          # Backend (FastAPI)
│   ├── main.py                  # FastAPI application entry point
│   ├── routers/                 # API route handlers
│   │   └── disease_pred_ml.py   # ML prediction endpoints
│   ├── services/                # Business logic services
│   ├── models/                  # ML models
│   └── ml/                      # ML pipeline
├── frontend/                     # Frontend (Flask)
│   ├── app.py                   # Flask application entry point
│   ├── routes.py                # Frontend routes
│   ├── templates/               # HTML templates
│   │   ├── upload.html         # Upload page
│   │   ├── result.html         # Results page
│   │   └── history.html        # History page
│   └── requirements.txt          # Frontend dependencies
├── static/                       # Shared static assets
│   ├── js/                      # JavaScript files
│   │   ├── upload.js           # Upload handling
│   │   ├── prediction.js       # Results display
│   │   └── history.js          # History management
│   ├── css/                     # CSS stylesheets
│   └── images/                  # Images and assets
├── requirements.txt              # Backend dependencies
├── startup.py                   # Backend startup script
├── run_all.py                   # Master startup script (runs both)
├── .env                         # Environment configuration
└── README.md
```

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Clone/Setup the Project
```bash
cd pneumonia_detection_project
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
pip install -r frontend/requirements.txt
```

## Configuration

### Environment Variables (.env)
The `.env` file contains all necessary configuration:

```
# Database
MYSQL_DB_HOST=127.0.0.1
MYSQL_DB_PORT=3306
MYSQL_DB_USER=root
MYSQL_DB_PASSWORD=root
MYSQL_DB_NAME=new_db

# API Keys
SECRET_KEY=your_super_secret_key_123456789
ALGORITHM=HS256
authToken_EXPIRE_MINUTES=60

# Backend Configuration
BACKEND_URL=http://localhost:8000/api

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=frontend/app.py

# Server Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=5000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

## Running the Application

### Option 1: Run Both Services Together (Recommended)
```bash
python run_all.py
```

This script will:
- Start the Backend FastAPI server on http://localhost:8000
- Start the Frontend Flask server on http://localhost:5000
- Display URLs for accessing both services

### Option 2: Run Services Separately

**Start Backend (FastAPI):**
```bash
python startup.py
```
- Backend runs on: http://localhost:8000
- API docs available at: http://localhost:8000/docs

**Start Frontend (Flask):**
```bash
cd frontend
python -m flask run --host 0.0.0.0 --port 5000
```
- Frontend runs on: http://localhost:5000

## Accessing the Application

1. **Frontend Interface:** http://localhost:5000
   - Home page with system information
   - Upload page for X-ray analysis
   - Results page displaying predictions
   - History page showing previous analyses

2. **Backend API Documentation:** http://localhost:8000/docs
   - Interactive API documentation
   - Test endpoints directly from the browser

## Features Implemented

### Frontend Features
✅ **File Upload Page**
- Drag-and-drop file upload
- File validation (PNG, JPG, JPEG)
- Progress tracking
- File preview

✅ **Prediction Results Display**
- Prediction outcome (Pneumonia/Normal)
- Confidence score with progress bar
- Grad-CAM attention visualization
- Detailed analysis metrics

✅ **Prediction History**
- Track all previous analyses
- View analysis statistics
- Filter by prediction type
- Delete individual entries
- Clear all history

✅ **User Interface**
- Responsive Bootstrap 5 design
- Dark mode support
- Accessibility features (ARIA labels)
- Loading indicators
- Toast notifications
- Error handling

### Backend API Endpoints
✅ **Prediction Endpoints**
- POST `/api/disease_pred_ml/predict` - Upload image and get prediction
- POST `/api/disease_pred_ml/loadDataset` - Load training dataset
- POST `/api/disease_pred_ml/cleanDataset` - Clean dataset
- POST `/api/disease_pred_ml/preprocessDataset` - Preprocess data
- POST `/api/disease_pred_ml/eda` - Get exploratory data analysis
- POST `/api/disease_pred_ml/trainModel` - Train model
- POST `/api/disease_pred_ml/evaluateModel` - Evaluate model

## API Request/Response Examples

### Predict Endpoint
**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -F "file=@chest_xray.jpg"
```

**Response:**
```json
{
  "dataResponse": {
    "returnCode": "SUCCESS",
    "description": "Prediction completed successfully"
  },
  "data": {
    "prediction": "PNEUMONIA",
    "confidence": 95.42,
    "gradcam": "data:image/png;base64,...",
    "pneumonia_prob": 95.42,
    "normal_prob": 4.58,
    "metrics": {
      "accuracy": 0.9542,
      "sensitivity": 0.9520,
      "specificity": 0.9564
    }
  }
}
```

## Troubleshooting

### Backend Connection Issues
- Ensure BACKEND_URL in .env is correct
- Check if backend is running: `curl http://localhost:8000/docs`
- Check firewall settings

### File Upload Issues
- Ensure file size doesn't exceed 25MB
- Only PNG, JPG, JPEG files are supported
- Check browser console for detailed errors

### Frontend Not Loading
- Clear browser cache
- Ensure Flask is running on correct port
- Check console for JavaScript errors

### Database Connection Issues
- Verify MySQL is running
- Check database credentials in .env
- Ensure database exists

## Performance Optimization

### Frontend Caching
- Static assets are cached by browsers
- Session storage used for prediction history
- LocalStorage used for persistent user data

### Backend Optimization
- CORS enabled for cross-origin requests
- Request timeout set to 60 seconds
- File size limit: 25MB
- Automatic image preprocessing

## Security Features

### Frontend
- Input validation (file type and size)
- XSS protection through template escaping
- CSRF protection (can be enabled)

### Backend
- File upload validation
- Size restrictions
- MIME type validation
- Error message sanitization
- CORS protection

## Medical Disclaimer

PneumoAI is a machine learning system designed to assist in the detection of pneumonia from chest X-rays. **Important:** This system is for informational purposes only and should NOT be used as a substitute for professional medical diagnosis. All results must be reviewed and validated by qualified medical professionals.

## Development Notes

### Adding New Features
1. Update backend routes in `app/routers/disease_pred_ml.py`
2. Update frontend routes in `frontend/routes.py`
3. Add corresponding HTML templates
4. Implement JavaScript handlers for new functionality
5. Test with both services running

### Debugging
- Backend logs printed to console
- Frontend logs visible in browser developer tools
- Enable FLASK_DEBUG=1 for detailed error messages

## Support & Documentation

For more information:
- API Documentation: http://localhost:8000/docs (Swagger UI)
- Backend Routes: `app/routers/disease_pred_ml.py`
- Frontend Routes: `frontend/routes.py`
- Database Schema: Check `app/db/` directory

## Next Steps

1. ✅ **Setup Complete** - Run `python run_all.py`
2. ✅ **Test Upload** - Navigate to http://localhost:5000/upload
3. ✅ **Review Results** - Check prediction results page
4. ✅ **Track History** - View analysis history at /history

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Start all services
python run_all.py

# Start backend only
python startup.py

# Start frontend only
cd frontend && python -m flask run

# Install dependencies
pip install -r requirements.txt
pip install -r frontend/requirements.txt

# Deactivate virtual environment
deactivate
```

---

**Last Updated:** 2024
**Status:** ✅ Production Ready
**Version:** 2.4.0
