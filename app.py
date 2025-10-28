from flask import Flask, request, jsonify, render_template, redirect, url_for
from database import db, User, Project
import hashlib
import threading, time, requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- UTIL ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------- API ----------------
@app.route('/api/user/add', methods=['POST'])
def add_user_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    key = hash_password(password)
    if User.query.filter_by(key=key).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(key=key, username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User added", "key": key}), 201


@app.route('/api/user/fetch', methods=['GET'])
def fetch_user_api():
    key = request.args.get('key')
    user = User.query.filter_by(key=key).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@app.route('/api/service/ping')
def ping():
    return jsonify({"status": "ok"}), 200


# ---------------- PROJECT API ----------------
@app.route('/api/project/add', methods=['POST'])
def add_project():
    data = request.json
    key = data.get('key')
    name = data.get('name')
    desc = data.get('description', '')
    short_url = data.get('short_url')
    long_url = data.get('long_url')

    user = User.query.filter_by(key=key).first()
    if not user:
        return jsonify({"error": "Invalid user key"}), 400

    project = Project(
        name=name,
        description=desc,
        short_url=short_url,
        long_url=long_url,
        owner=user
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"message": "Project added", "project": project.to_dict()}), 201


@app.route('/project/<int:pid>/<shortlink>', methods=['GET', 'POST'])
def proxy_to_long_url(pid, shortlink):
    """Handles calls to shortlinks and proxies them to the long URL"""
    project = Project.query.filter_by(id=pid, short_url=shortlink).first()
    if not project or not project.long_url:
        return jsonify({"error": "Project or long URL not found"}), 404

    try:
        # Forward the incoming request to the project's long_url
        if request.method == 'POST':
            resp = requests.post(project.long_url, json=request.json, headers=request.headers)
        else:
            resp = requests.get(project.long_url, headers=request.headers)

        return (resp.text, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- HTML Pages ----------------
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        key = hash_password(password)
        if User.query.filter_by(key=key).first():
            message = "User already exists!"
        else:
            user = User(key=key, username=username)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('signup.html', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        key = hash_password(password)
        user = User.query.filter_by(key=key, username=username).first()
        if user:
            return redirect(url_for('profile', key=key))
        else:
            message = "Invalid username or password"
    return render_template('login.html', message=message)


@app.route('/profile/<key>', methods=['GET', 'POST'])
def profile(key):
    user = User.query.filter_by(key=key).first()
    if not user:
        return "User not found", 404

    message = ""
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        project_desc = request.form.get('project_desc', '')
        if project_name:
            new_project = Project(name=project_name, description=project_desc, owner=user)
            db.session.add(new_project)
            db.session.commit()
            message = f"Project '{project_name}' added!"
    return render_template('profile.html', user=user, message=message)


# ---------------- SELF PING ----------------
def self_ping():
    time.sleep(5)  # wait for server to start
    while True:
        try:
            requests.get("http://127.0.0.1:5000/api/service/ping")
            print("[SELF-PING] ✅ Alive")
        except Exception as e:
            print(f"[SELF-PING] ❌ Failed: {e}")
        time.sleep(30)


# ---------------- RUN ----------------
if __name__ == '__main__':
    threading.Thread(target=self_ping, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
@app.route('/api/user/fetch', methods=['GET'])
def fetch_user_api():
    key = request.args.get('key')
    user = User.query.filter_by(key=key).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@app.route('/api/service/ping')
def ping():
    return jsonify({"status": "ok"}), 200


# ---------------- HTML Pages ----------------
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        key = hash_password(password)
        if User.query.filter_by(key=key).first():
            message = "User already exists!"
        else:
            user = User(key=key, username=username)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('signup.html', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        key = hash_password(password)
        user = User.query.filter_by(key=key, username=username).first()
        if user:
            return redirect(url_for('profile', key=key))
        else:
            message = "Invalid username or password"
    return render_template('login.html', message=message)


@app.route('/profile/<key>', methods=['GET', 'POST'])
def profile(key):
    user = User.query.filter_by(key=key).first()
    if not user:
        return "User not found", 404

    message = ""
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        project_desc = request.form.get('project_desc', '')
        if project_name:
            new_project = Project(name=project_name, description=project_desc, owner=user)
            db.session.add(new_project)
            db.session.commit()
            message = f"Project '{project_name}' added!"
    return render_template('profile.html', user=user, message=message)


# ---------------- SELF PING ----------------
def self_ping():
    time.sleep(5)  # wait for server to start
    while True:
        try:
            requests.get("http://127.0.0.1:5000/api/service/ping")
            print("[SELF-PING] ✅ Alive")
        except Exception as e:
            print(f"[SELF-PING] ❌ Failed: {e}")
        time.sleep(30)


# ---------------- RUN ----------------
if __name__ == '__main__':
    threading.Thread(target=self_ping, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
