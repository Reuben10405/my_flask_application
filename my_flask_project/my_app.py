from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 🔹 Flask App Initialization
app = Flask(__name__)

# 🔹 Environment Variables (Use .env or system variables in production)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "98fda4095617f1")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "b7a40d6fb09c62")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@yourdomain.com")

# Function to switch email accounts
def send_email(recipient, subject, body, use_support=False):
    if use_support:
        app.config["MAIL_USERNAME"] = os.getenv("MAIL_SUPPORT_USERNAME")
        app.config["MAIL_PASSWORD"] = os.getenv("MAIL_SUPPORT_PASSWORD")
    
    msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[recipient])
    msg.body = body

    with app.app_context():
        mail.send(msg)

# 🔹 Extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# 🔹 MongoDB Collections
users_collection = mongo.db.users
contacts_collection = mongo.db.contacts

# 🔹 User Model
class User(UserMixin):
    def __init__(self, user_id):
        self.id = str(user_id)

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    return User(user_id) if user else None

# 🔹 Home Route
@app.route('/')
def home():
    return render_template('index.html')

# 🔹 Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))
        if users_collection.find_one({"email": email}):
            flash("Email already exists! Try logging in.", "danger")
            return redirect(url_for('login'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({"email": email, "password": hashed_password})
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# 🔹 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})
        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(user["_id"]))
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')

# 🔹 Dashboard (Protected Route)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# 🔹 Forgot Password (Send Reset Email)
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = users_collection.find_one({"email": email})
        if user:
            token = serializer.dumps(email, salt="password-reset-salt")
            reset_link = url_for('reset_password', token=token, _external=True)
            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_link}\n\nThis link expires in 1 hour."
            try:
                mail.send(msg)
                flash("A password reset email has been sent!", "success")
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "danger")
            return redirect(url_for('login'))
        else:
            flash("No account found with this email.", "danger")
    return render_template('forgot_password.html')

# 🔹 Reset Password Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except SignatureExpired:
        flash("The password reset link has expired. Request a new one.", "danger")
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash("Invalid password reset link.", "danger")
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
        flash("Password reset successful! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

# 🔹 Search Contacts Route
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    contact = None
    if request.method == 'POST':
        reg_number = request.form['registration_number']
        contact = contacts_collection.find_one({"registration_number": reg_number})

        if not contact:
            flash("No contact found with this registration number.", "danger")

    return render_template('search.html', contact=contact)
# 🔹 Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# 🔹 Run Flask App
if __name__ == '__main__':
    app.run(debug=True)

