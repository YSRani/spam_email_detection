from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

# Operation Model
class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Content being checked
    result = db.Column(db.String(50), nullable=False)  # Result of the spam check
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Home Page
@app.route('/')
def index():
    return render_template("index.html")

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')  # Hash and salt password

        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "User already exists! Try a different email."

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("signup.html")

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Debugging: Print form data
        print(request.form)

        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return "Email and password are required.", 400

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials, please try again."

    return render_template("login.html")

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("dashboard.html", username=session['username'])

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/test-db')
def test_db():
    try:
        # Query the database
        users = User.query.all()
        return f"Database connected! Found {len(users)} users."
    except Exception as e:
        return f"Database connection failed: {str(e)}"

# Example spam keywords
SPAM_KEYWORDS = ["win", "prize", "free", "money", "click here", "urgent", "lottery", "spam"]

# Route to log spam check
@app.route('/check-spam', methods=['POST'])
def check_spam():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return "User not found.", 404

    # Get the content to check for spam
    content = request.form.get('content')
    if not content:
        return "No content provided for spam check.", 400

    # Enhanced spam check logic
    result = "Spam" if any(keyword in content.lower() for keyword in SPAM_KEYWORDS) else "Not Spam"

    # Log the operation
    log = Operation(user_id=user.id, content=content, result=result)
    db.session.add(log)
    db.session.commit()

    # Render the result in a styled template
    return render_template("check_spam_result.html", result=result)

# Route to view all data
@app.route('/view-data')
def view_data():
    try:
        # Query all users and operations
        users = User.query.all()
        operations = Operation.query.all()

        # Format user data
        user_data = [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in users
        ]

        # Format operation data
        operation_data = [
            {
                "id": op.id,
                "user_id": op.user_id,
                "username": User.query.get(op.user_id).username,
                "content": op.content,
                "result": op.result,
                "timestamp": op.timestamp,
            }
            for op in operations
        ]

        # Pass data to the template
        return render_template("view_data.html", users=user_data, operations=operation_data)
    except Exception as e:
        return f"Error fetching data: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates database tables
    app.run(debug=True)
