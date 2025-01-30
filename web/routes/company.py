from flask import Blueprint, request, jsonify, render_template, session, flash, redirect, url_for
from config import get_db_connection, company_required
from datetime import datetime

company_bp = Blueprint('company', __name__)

@company_bp.route('/company')
@company_required
def index():
    company_id = session.get('company_id')  
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(company_id)

    # select visits from today
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT rfid_tag) as today_visits,
            SUM(CASE WHEN exit_time IS NULL THEN 1 ELSE 0 END) as active_vehicles,
            AVG(duration) as avg_visit_time
        FROM parking_entries
        WHERE entry_time >= CURDATE()
        AND company_checkin_id = %s
    """, (company_id,))
    stats = cursor.fetchone()

    # select last 20 visits
    cursor.execute("""
        SELECT 
            rfid_tag,
            entry_time,
            exit_time,
            duration,
            exit_time IS NULL as is_active
        FROM parking_entries
        WHERE company_checkin_id = %s
        ORDER BY entry_time DESC
        LIMIT 20
    """, (company_id,))
    visits = cursor.fetchall()

    conn.close()

    user = {
        'username': session.get('username'),
        'role': session.get('role')
    }
    
    return render_template('company.html', stats=stats, visits=visits, user=user)

@company_bp.route('/company/register_visit', methods=['POST'])
@company_required
def register_visit():
    company_id = session.get('company_id')
    rfid_tag = request.form.get('rfid_tag')
    
    if not rfid_tag:
        flash('Brak numeru karty', 'error')
        return redirect(url_for('company.index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # check if there is an active entry for this rfid tag
        cursor.execute("""
            SELECT id, company_checkin_id 
            FROM parking_entries 
            WHERE rfid_tag = %s AND exit_time IS NULL
            ORDER BY entry_time DESC 
            LIMIT 1
        """, (rfid_tag,))
        
        active_entry = cursor.fetchone()
        
        if not active_entry:
            flash('Nie znaleziono aktywnego wjazdu dla tej karty', 'error')
            return redirect(url_for('company.index'))
        
        if active_entry['company_checkin_id'] is not None:
            flash('Ta karta jest już przypisana do firmy', 'error')
            return redirect(url_for('company.index'))
            
        cursor.execute("""
            UPDATE parking_entries 
            SET company_checkin_id = %s 
            WHERE id = %s
        """, (company_id, active_entry['id']))
        
        conn.commit()
        flash('Wizyta zarejestrowana pomyślnie', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Wystąpił błąd: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('company.index'))