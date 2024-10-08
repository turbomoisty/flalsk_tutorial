import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')



@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required'
            
        elif not password:
            error = 'Password is required'
            
        elif not email:
            error = 'Email is requiredd'
            
        if error is None:
            try:
                db.execute("INSERT INTO user (username, password, email) VALUES (?, ?, ?)", 
                           (username, generate_password_hash(password), email),)
                db.commit()
            except db.IntegrityError:
                error = f"User {username} already exists"
                
            else:
                return redirect(url_for('auth.login'))
            
        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None
        
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone() # returns one row from query.
            # If the query doesn't return a result, it returns None
        if user is None:
            error = 'Incorrect Username'
        elif not check_password_hash(user[password], password): # check_password_hash hashes submitted pw in the same manner as the
            # stored hash, and if they match, the PW is valid.
            error = 'Incorrect Password'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
        
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id)).fetchone()
        
        
@bp.route('/logout')
def log_out():
    session.clear()
    return redirect(url_for('index'))