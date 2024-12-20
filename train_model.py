from flask import Flask, render_template, request, redirect, session
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Database setup
DATABASE = 'init_db.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Example dataset for prediction model
data = {
    'symptom1': ['fever', 'cough', 'rash', 'nausea'],
    'symptom2': ['headache', 'sore throat', 'itchy skin', 'vomiting'],
    'symptom3': ['body ache', 'runny nose', None, None],
    'disease': ['flu', 'cold', 'allergy', 'food poisoning']
}

df = pd.DataFrame(data)

# Preprocess the dataset
df.fillna('', inplace=True)  # Replace NaN with empty strings
X = df[['symptom1', 'symptom2', 'symptom3']]
y = df['disease']

# Convert text data to numeric using one-hot encoding
X_encoded = pd.get_dummies(X)
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'model.pkl')

# Predict disease based on symptoms
def predict_disease(symptom1, symptom2, symptom3):
    try:
        # Load the saved model
        loaded_model = joblib.load('model.pkl')

        # Create input data for prediction
        input_data = pd.DataFrame({
            'symptom1': [symptom1],
            'symptom2': [symptom2],
            'symptom3': [symptom3]
        })

        # Perform one-hot encoding to match training data structure
        input_encoded = pd.get_dummies(input_data)
        input_encoded = input_encoded.reindex(columns=X_encoded.columns, fill_value=0)

        # Debugging: Print input data
        print("Input Data for Prediction:", input_encoded)

        # Make prediction
        prediction = loaded_model.predict(input_encoded)
        print("Predicted Disease:", prediction[0])  # Debugging
        return prediction[0]
    except Exception as e:
        print("Error during prediction:", str(e))
        return None

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            # Insert user data into the database
            cursor.execute('''
                INSERT INTO users (username, password, name, contact, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, name, contact, email))
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

        # Check if the user exists and the password matches
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == password:
            # Login successful
            session['username'] = username
            return redirect('/')
        else:
            return "Invalid username or password. <a href='/login'>Try Again</a>"

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# Home route
@app.route('/')
def home():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session['username'])

# Submit form route
@app.route('/submit', methods=['POST'])
def submit():
    # Check if user is logged in
    if 'username' not in session:
        return redirect('/login')

    # Get form data
    name = request.form['name']
    contact = request.form['contact']
    email = request.form['email']
    symptom1 = request.form['symptom1']
    symptom2 = request.form['symptom2']
    symptom3 = request.form['symptom3']

    # Make prediction using the trained model
    predicted_disease = predict_disease(symptom1, symptom2, symptom3)

    # Debugging: Print disease value
    if predicted_disease is None:
        predicted_disease = "Unable to predict disease. Please try again."

    print("Predicted Disease in Submit Route:", predicted_disease)

    # Pass all details to the result.html
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
    init_db()  # Initialize database
    app.run(debug=True)
