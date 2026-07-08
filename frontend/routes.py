from flask import render_template, request, jsonify, current_app
from app import app
import requests
import os
import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dicom', 'dcm'}
MAX_FILE_SIZE = 25 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_backend_url():
    return current_app.config.get('BACKEND_URL', os.getenv('BACKEND_URL', 'http://localhost:8000/api'))


def get_auth_headers():
    """Forward the Authorization token from the browser request to FastAPI."""
    token = request.headers.get('Authorization')
    if token:
        return {'Authorization': token}
    return {}


def render(template, **kwargs):
    kwargs.setdefault('current_year', datetime.datetime.now().year)
    return render_template(template, **kwargs)


# ─── Page Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Landing page — public marketing page"""
    return render("index.html")


@app.route("/login")
def login_page():
    """Login page"""
    return render("login.html")


@app.route("/register")
def register():
    return render("register.html")


@app.route("/dashboard")
def dashboard():
    return render("dashboard.html")


@app.route("/profile")
def profile():
    return render("profile.html")


@app.route("/upload")
def upload():
    return render("upload.html")


@app.route("/results")
def results():
    return render("result.html")


@app.route("/history")
def history():
    return render("history.html")


@app.route("/analytics")
def analytics():
    return render("analytics.html")


@app.route("/landing")
def landing():
    return render("index.html")


# ─── Auth API ─────────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=['POST'])
def auth_login():
    try:
        backend_url = get_backend_url()

        data = request.get_json(force=True)

        print("LOGIN DATA RECEIVED:", data)

        email = data.get("email_id") or data.get("username")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "detail": "Missing email/username or password"
            }), 400

        response = requests.post(
            f'{backend_url}/auth/login',
            data={
                "username": email,
                "password": password
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({
            "detail": str(e)
        }), 500


@app.route("/api/auth/register", methods=['POST'])
def auth_register():
    try:
        backend_url = get_backend_url()
        response = requests.post(
            f'{backend_url}/auth/register',
            json=request.get_json(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'detail': 'Cannot connect to server.'}), 503
    except Exception as e:
        return jsonify({'detail': str(e)}), 500


@app.route("/api/auth/logout", methods=['POST'])
def auth_logout():
    try:
        backend_url = get_backend_url()
        response = requests.post(
            f'{backend_url}/auth/logout',
            json=request.get_json(),
            headers=get_auth_headers(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'detail': 'Cannot connect to server.'}), 503
    except Exception as e:
        return jsonify({'detail': str(e)}), 500


@app.route("/api/auth/profile", methods=['GET'])
def get_profile():
    try:
        backend_url = get_backend_url()
        user_id = request.args.get('user_id')
        response = requests.get(
            f'{backend_url}/auth/profile',
            headers=get_auth_headers(),
            params={'user_id': user_id},
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'detail': 'Cannot connect to server.'}), 503
    except Exception as e:
        return jsonify({'detail': str(e)}), 500


@app.route("/api/auth/profile", methods=['PUT'])
def update_profile():
    try:
        backend_url = get_backend_url()
        user_id = request.args.get('user_id')
        response = requests.put(
            f'{backend_url}/auth/profile',
            headers=get_auth_headers(),
            params={'user_id': user_id},
            json=request.get_json(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'detail': 'Cannot connect to server.'}), 503
    except Exception as e:
        return jsonify({'detail': str(e)}), 500


@app.route("/api/auth/change-password", methods=['POST'])
def change_password():
    try:
        backend_url = get_backend_url()
        user_id = request.args.get('user_id')
        response = requests.post(
            f'{backend_url}/auth/change-password',
            headers=get_auth_headers(),
            params={'user_id': user_id},
            json=request.get_json(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'detail': 'Cannot connect to server.'}), 503
    except Exception as e:
        return jsonify({'detail': str(e)}), 500


# ─── Prediction API ───────────────────────────────────────────────────────────

@app.route("/predict", methods=['POST'])
def predict():
    try:
        backend_url = get_backend_url()

        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided in request'}), 400

        file = request.files['file']

        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not supported.'}), 400

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File too large. Maximum 25 MB.'}), 413

        filename = secure_filename(file.filename)
        files = {'file': (filename, file.stream, file.content_type or 'application/octet-stream')}

        patient_name   = request.form.get('patient_name', 'Anonymous')
        patient_age    = request.form.get('patient_age', '0') or '0'
        patient_gender = request.form.get('patient_gender', 'Unknown')

        form_data = {
            'patient_name':   patient_name,
            'patient_age':    patient_age,
            'patient_gender': patient_gender,
        }

        predict_url = f'{backend_url}/disease_pred_ml/predict'
        response = requests.post(
            predict_url,
            files=files,
            data=form_data,
            headers=get_auth_headers(),
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            data['success'] = True
            return jsonify(data), 200

        error_msg = f'Backend returned status {response.status_code}'
        try:
            err_body = response.json()
            error_msg = err_body.get('detail', err_body.get('message', error_msg))
        except Exception:
            if response.text:
                error_msg = response.text[:300]

        return jsonify({'success': False, 'error': error_msg}), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timed out.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to AI backend.'}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network error: {str(e)}'}), 502
    except Exception as e:
        app.logger.exception("Unexpected error in /predict")
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500


# ─── History API ──────────────────────────────────────────────────────────────

@app.route("/api/history", methods=['GET'])
def get_history():
    try:
        backend_url = get_backend_url()

        params = {}
        if request.args.get('patient_name'):
            params['patient_name'] = request.args.get('patient_name')
        if request.args.get('detected_disease'):
            params['detected_disease'] = request.args.get('detected_disease')

        params['limit']  = request.args.get('limit',  10,  type=int)
        params['offset'] = request.args.get('offset', 0,   type=int)

        response = requests.get(
            f'{backend_url}/history',
            headers=get_auth_headers(),
            params=params,
            timeout=10
        )
        return jsonify(response.json()), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/history/count", methods=['GET'])
def get_history_count():
    try:
        backend_url = get_backend_url()

        params = {}
        if request.args.get('patient_name'):
            params['patient_name'] = request.args.get('patient_name')
        if request.args.get('detected_disease'):
            params['detected_disease'] = request.args.get('detected_disease')

        response = requests.get(
            f'{backend_url}/history/count',
            headers=get_auth_headers(),
            params=params,
            timeout=10
        )
        return jsonify(response.json()), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/history/<int:history_id>", methods=['GET'])
def get_history_by_id(history_id):
    try:
        backend_url = get_backend_url()
        response = requests.get(
            f'{backend_url}/history/{history_id}',
            headers=get_auth_headers(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/history/<int:history_id>", methods=['DELETE'])
def delete_history(history_id):
    try:
        backend_url = get_backend_url()
        response = requests.delete(
            f'{backend_url}/history/{history_id}',
            headers=get_auth_headers(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Dashboard API ────────────────────────────────────────────────────────────

@app.route("/api/dashboard/stats")
def dashboard_stats():
    try:
        backend_url = get_backend_url()
        response = requests.get(
            f'{backend_url}/dashboard/stats',
            headers=get_auth_headers(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/history/export/pdf", methods=['GET'])
def export_history_pdf():
    try:
        backend_url = get_backend_url()
        response = requests.get(
            f'{backend_url}/history/export/pdf',
            headers=get_auth_headers(),
            timeout=30
        )
        if response.status_code == 200:
            from flask import Response
            return Response(
                response.content,
                status=response.status_code,
                headers=dict(response.headers)
            )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/report/download/<int:history_id>", methods=['GET'])
def download_report(history_id):
    try:
        backend_url = get_backend_url()
        response = requests.get(
            f'{backend_url}/report/download/{history_id}',
            headers=get_auth_headers(),
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to backend.'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ─── Health & Status ──────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({'status': 'ok', 'service': 'pneumoai-frontend', 'version': '2.4.0'}), 200


@app.route("/api/backend-status")
def backend_status():
    backend_url = get_backend_url()
    try:
        probe_url = backend_url.rstrip('/api').rstrip('/') + '/'
        resp = requests.get(probe_url, timeout=4)
        is_online = resp.status_code < 500
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        is_online = False
    except Exception:
        is_online = False
    return jsonify({
        'frontend': 'online',
        'backend': 'online' if is_online else 'offline',
        'backend_url': backend_url
    }), 200


# ─── Error Handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    if request.accept_mimetypes.best == 'application/json':
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return render("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    if request.accept_mimetypes.best == 'application/json':
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return render("500.html"), 500