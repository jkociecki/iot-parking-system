from flask import Blueprint, request, render_template, redirect, url_for, session
from config import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  
        
        try:
            cursor.execute("""
                SELECT id, username, role, company_id 
                FROM system_users 
                WHERE username = %s AND password = %s
            """, (username, password))
            
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_role'] = user['role']
                session['company_id'] = user['company_id']  
                
                if user['role'] == 'admin':
                    return redirect(url_for('admin.index'))
                elif user['role'] == 'company_manager':
                    return redirect(url_for('company.index'))
                else:
                    return redirect(url_for('gate.index'))

            error = "Nieprawidłowy login lub hasło"
            return render_template('login.html', error=error)
            
        except Exception as e:
            print(f"Database error: {e}")
            error = "Błąd bazy danych"
            return render_template('login.html', error=error)
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

