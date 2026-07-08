from flask import Flask, render_template
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
    static_url_path="/static"
)

# Configuration
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', True)
app.config['BACKEND_URL'] = os.getenv('BACKEND_URL', 'http://localhost:8000/api')
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB max file size


# ====================== ROOT ROUTE - SHOW LOGIN PAGE ======================



# Import routes
from routes import *

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)