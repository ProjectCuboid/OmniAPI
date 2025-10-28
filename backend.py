from flask import Flask, request, jsonify, render_template, redirect, url_for
from database import db, User, Project
import hashlib

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
        # Add a new project
        project_name = request.form.get('project_name')
        project_desc = request.form.get('project_desc', '')
        if project_name:
            new_project = Project(name=project_name, description=project_desc, owner=user)
            db.session.add(new_project)
            db.session.commit()
            message = f"Project '{project_name}' added!"

    return render_template('profile.html', user=user, message=message)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    while(1):
        #make it ping itself repeatedly each 30 seconds
