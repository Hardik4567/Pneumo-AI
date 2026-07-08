# 🫁 PneumoAI - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### 1. **Install Dependencies**
```bash
# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
pip install -r frontend/requirements.txt
```

### 2. **Run the Application**
```bash
# Run both backend and frontend together
python run_all.py
```

### 3. **Access the System**
- **Frontend:** http://localhost:5000
- **Backend API Docs:** http://localhost:8000/docs

### 4. **Upload Your First X-ray**
1. Click "Start Analysis" or go to `/upload`
2. Drag and drop or select a chest X-ray image
3. Click "Analyze using AI Engine"
4. Wait for results (~5-10 seconds)
5. View predictions and Grad-CAM visualization

---

## 🎯 Key Pages

| Page | URL | Purpose |
|------|-----|---------|
| Home | `/` | Application overview & information |
| Upload | `/upload` | X-ray analysis interface |
| Results | `/results` | Prediction results & visualization |
| History | `/history` | Previous analyses & statistics |

---

## 🔧 API Endpoints

### Main Prediction Endpoint
```bash
POST /predict
Content-Type: multipart/form-data

file: <image_file>

# Response
{
  "dataResponse": {
    "returnCode": "SUCCESS",
    "description": "Prediction completed successfully"
  },
  "data": {
    "prediction": "PNEUMONIA" or "NORMAL",
    "confidence": 95.42,
    "gradcam": "base64_image_data",
    ...
  }
}
```

---

## ✨ Features

✅ **Drag-and-Drop Upload**
- Easy file selection
- Real-time validation
- Progress tracking

✅ **AI-Powered Predictions**
- DenseNet-121 deep learning model
- 95.4% accuracy
- < 2s analysis time

✅ **Visual Explanations**
- Grad-CAM attention maps
- Highlight important regions
- Confidence scores

✅ **History & Analytics**
- Track all predictions
- View statistics
- Export results

---

## 🐛 Troubleshooting

### Can't connect to backend?
- Check if backend is running: `curl http://localhost:8000/docs`
- Verify BACKEND_URL in `.env` is correct
- Restart services with `python run_all.py`

### Upload failing?
- File must be PNG, JPG, or JPEG
- Maximum file size: 25MB
- Image must be at least 128x128 pixels

### Results page not showing?
- Clear browser cache (Ctrl+Shift+Del)
- Check browser console for errors (F12)
- Ensure both services are running

---

## 📊 System Architecture

```
User Browser
     ↓
  Frontend (Flask)
  ├─ Upload handling
  ├─ Form validation
  ├─ Results display
     ↓
  Backend (FastAPI)
  ├─ Image processing
  ├─ Model inference
  ├─ Grad-CAM generation
     ↓
  ML Pipeline
  ├─ DenseNet-121 model
  ├─ Preprocessing
  ├─ Classification
```

---

## 🔒 Security & Privacy

- ✅ File size validation (max 25MB)
- ✅ File type validation (PNG, JPG, JPEG only)
- ✅ MIME type verification
- ✅ Encrypted communication (can enable SSL)
- ✅ Ephemeral data storage

---

## 📝 Medical Disclaimer

⚠️ **IMPORTANT:** This system is for **informational purposes only**.

This AI system is designed to assist healthcare professionals and should NOT be used as:
- Primary diagnostic tool
- Substitute for professional medical advice
- Autonomous decision-making system

**Always consult with qualified medical professionals for diagnosis and treatment.**

---

## 🚀 Next Steps

1. ✅ **Try Demo Upload** - Test with provided sample images
2. ✅ **Check Results** - Review prediction accuracy
3. ✅ **Explore API** - Visit `/docs` for interactive API testing
4. ✅ **View History** - See analysis trends

---

## 💬 Support

**Documentation:**
- Full setup guide: See `SETUP_GUIDE.md`
- API documentation: Visit http://localhost:8000/docs
- Frontend code: Check `frontend/routes.py`
- Backend code: Check `app/main.py`

**Commands:**
```bash
# Start services
python run_all.py

# Stop services
Ctrl+C

# View logs
# Check terminal output for detailed logs
```

---

## 📋 System Requirements

- ✅ Python 3.8+
- ✅ 4GB RAM minimum
- ✅ 500MB disk space
- ✅ Modern web browser
- ✅ MySQL database (configured in .env)

---

**Status:** ✅ Ready to Use | **Version:** 2.4.0 | **Last Updated:** 2024
