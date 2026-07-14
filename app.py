import json
import os
import uuid
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')


def get_users_file():
    return app.config.get('USERS_FILE') or os.environ.get('USERS_FILE') or os.path.join(BASE_DIR, 'users.json')


def ensure_users_file():
    users_file = get_users_file()
    os.makedirs(os.path.dirname(users_file), exist_ok=True)
    if not os.path.exists(users_file):
        with open(users_file, 'w', encoding='utf-8') as handle:
            handle.write('[]')


def load_users():
    users_file = get_users_file()
    ensure_users_file()
    with open(users_file, 'r', encoding='utf-8') as handle:
        content = handle.read().strip()
        return json.loads(content) if content else []


def save_users(users):
    users_file = get_users_file()
    ensure_users_file()
    with open(users_file, 'w', encoding='utf-8') as handle:
        handle.write(json.dumps(users, ensure_ascii=False, indent=2))


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/index.html')
def index_html():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'images'), filename)


@app.route('/api/register', methods=['POST'])
def register_user():
    payload = request.get_json(silent=True) or {}
    name = (payload.get('name') or '').strip()
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password') or ''

    if not name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    users = load_users()
    if any(user['email'].lower() == email for user in users):
        return jsonify({'error': 'Email already exists'}), 409

    user = {
        'id': f'user-{uuid.uuid4().hex[:8]}',
        'name': name,
        'email': email,
        'password': password,
    }
    users.append(user)
    save_users(users)
    return jsonify({'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}})


@app.route('/api/login', methods=['POST'])
def login_user():
    payload = request.get_json(silent=True) or {}
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    users = load_users()
    user = next((item for item in users if item['email'].lower() == email and item['password'] == password), None)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}})


@app.route('/api/users', methods=['GET'])
def list_users():
    return jsonify(load_users())


@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)


#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
