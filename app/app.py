from flask import Flask, request, render_template, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='db',
            user='myuser',
            password='mypassword',
            database='user_auth'
        )
        print("Connected to database successfully.")
        return conn
    except Error as e:
        print("Unable to connect to the database:", str(e))
        return None

@app.route('/')
def index():
    return render_template('auth/login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    user_record = None

    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('index'))
    
    try:
        with conn.cursor(dictionary=True) as cur:
            # Utilisez 'type' au lieu de 'username' pour la requête SQL
            cur.execute("SELECT mot_de_passe FROM utilisateurs WHERE type = %s", (username,))
            user_record = cur.fetchone()
    except Error as e:
        flash('An error occurred while fetching user data.', 'error')
        print("Query failed: ", str(e))
    finally:
        if conn.is_connected():
            conn.close()

    if user_record and user_record['mot_de_passe'] == password:
        session['user_id'] = username  # Setting session after successful login
        return redirect(url_for('calendar'))  # Redirect to the calendar page
    else:
        flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
        return redirect(url_for('index'))


@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in
    return render_template('event_calendar/calendar.html', username=session['user_id'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
