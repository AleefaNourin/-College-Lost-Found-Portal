from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- Helper: Check file extension ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Database connection ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Home Page ---
@app.route('/')
def index():
    return render_template('index.html')

# --- View Approved Items ---
@app.route('/items')
def view_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items WHERE approved = 1').fetchall()
    conn.close()
    return render_template('view_items.html', items=items)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Post New Item ---
@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        item_type = request.form['type']
        contact_info = request.form['contact_info']
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            conn.execute('INSERT INTO items (title, description, type, image, contact_info, approved) VALUES (?, ?, ?, ?, ?, ?)',
                         (title, description, item_type, filename, contact_info, 0))
            conn.commit()
            conn.close()

            flash('Your post has been submitted for approval.')
            return redirect(url_for('index'))

    return render_template('post_item.html')


# --- Admin Login ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# --- Admin Dashboard ---
@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', items=items)

# --- Approve or Delete Posts ---
@app.route('/approve/<int:id>')
def approve_post(id):
    conn = get_db_connection()
    conn.execute('UPDATE items SET approved = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:id>')
def delete_post(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# --- Start the App ---
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
