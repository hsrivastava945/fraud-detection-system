from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('fraud.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 amount REAL,
                 location TEXT,
                 risk_score REAL,
                 status TEXT)''')
    conn.commit()
    conn.close()

def calculate_risk(amount, location):
    risk = 0
    if amount > 50000:
        risk += 40
    if location.lower() != "kanpur":
        risk += 30
    return risk

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        location = request.form['location']
        risk = calculate_risk(amount, location)
        status = "Fraud" if risk > 60 else "Safe"

        conn = sqlite3.connect('fraud.db')
        c = conn.cursor()
        c.execute("INSERT INTO transactions (amount, location, risk_score, status) VALUES (?,?,?,?)",
                  (amount, location, risk, status))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('transaction.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('fraud.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    data = c.fetchall()
    conn.close()
    return render_template('dashboard.html', data=data)

@app.route('/alerts')
def alerts():
    conn = sqlite3.connect('fraud.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE status='Fraud'")
    data = c.fetchall()
    conn.close()
    return render_template('alerts.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)