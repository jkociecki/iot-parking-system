import mysql.connector
from functools import wraps
from flask import session, redirect, url_for

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  
        user="root",       
        password="",      
        database="parking" 
    )
    return conn

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'company_manager':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def gate_operator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'gate_operator':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

