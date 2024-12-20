from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Database setup
DATABASE = 'init_db.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            symptom1 TEXT NOT NULL,
            symptom2 TEXT NOT NULL,
            symptom3 TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            # Insert user into the users table
            cursor.execute('''
                INSERT INTO users (username, password) VALUES (?, ?)
            ''', (username, password))
            conn.commit()
            return "Registration successful! <a href='/login'>Go to Login</a>"
        except sqlite3.IntegrityError:
            return "Username already exists. <a href='/register'>Try Again</a>"
        finally:
            conn.close()

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == password:
            session['username'] = username  # Set session for logged-in user
            return redirect('/')
        else:
            return "Invalid username or password. <a href='/login'>Try Again</a>"

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    return redirect('/login')

# Home route
@app.route('/')
def home():
    if 'username' in session:  # Check if user is logged in
        return render_template('index.html', username=session['username'])
    else:
        return redirect('/login')

# Submit form route
@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:  # Ensure the user is logged in
        return redirect('/login')

    # Get form data
    username = session['username']
    name = request.form['name']
    contact = request.form['contact']
    email = request.form['email']
    symptom1 = request.form['symptom1']
    symptom2 = request.form['symptom2']
    symptom3 = request.form['symptom3']

    # Dummy prediction logic (replace with ML model)
    predicted_disease = "flu"  # Replace this with your model's prediction

    # Debugging: Print details
    print(f"Predicted Disease: {predicted_disease}")

    # Save user details in the user_details table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_details (username, name, contact, email, symptom1, symptom2, symptom3)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, name, contact, email, symptom1, symptom2, symptom3))
    conn.commit()
    conn.close()

    # Render result.html with the predicted disease and user details
    return render_template(
        'result.html',
        name=name,
        contact=contact,
        email=email,
        symptom1=symptom1,
        symptom2=symptom2,
        symptom3=symptom3,
        disease=predicted_disease
    )

if __name__ == '__main__':
    init_db()  # Initialize the database tables
    app.run(debug=True)
