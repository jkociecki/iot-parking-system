from flask import Blueprint, render_template, request, jsonify, session
from config import get_db_connection, admin_required
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get companies with current parking usage
    cursor.execute("""
    SELECT 
        c.*,
        COALESCE(COUNT(CASE WHEN pe.exit_time IS NULL THEN pe.id END), 0) as current_vehicles,
        COALESCE(COUNT(DISTINCT pe.rfid_tag), 0) as total_vehicles
    FROM companies c 
    LEFT JOIN parking_entries pe ON c.id = pe.company_checkin_id
    WHERE pe.entry_time >= CURDATE() OR pe.entry_time IS NULL
    GROUP BY c.id
    """)
    
    companies = []
    for row in cursor.fetchall():
        companies.append({
            'id': row['id'],
            'name': row['name'],
            'free_hours': row['max_bonus_hours'],
            'is_active': True,
            'current_vehicles': row['current_vehicles'],
            'total_vehicles': row['total_vehicles']
        })
    
    # Get general statistics
    cursor.execute("""
    SELECT 
        COUNT(*) as total_entries,
        COUNT(DISTINCT rfid_tag) as total_vehicles,
        SUM(CASE WHEN exit_time IS NULL THEN 1 ELSE 0 END) as current_vehicles,
        AVG(TIMESTAMPDIFF(HOUR, entry_time, COALESCE(exit_time, NOW()))) as avg_stay_time,
        SUM(total_price) as today_revenue,
        100 as revenue_change  -- placeholder, możesz dodać prawdziwe obliczenia
    FROM parking_entries
    WHERE entry_time >= CURDATE()
    """)
    stats = cursor.fetchone()
    
    stats = {
        'total_vehicles': stats.get('current_vehicles', 0),
        'today_revenue': stats.get('today_revenue', 0),
        'revenue_change': stats.get('revenue_change', 0),
        'avg_stay_time': round(stats.get('avg_stay_time', 0), 1)
    }
    
    # Get hourly usage data
    cursor.execute("""
    SELECT 
        HOUR(entry_time) AS hour, 
        COUNT(*) AS count
    FROM parking_entries
    WHERE entry_time >= NOW() - INTERVAL 24 HOUR
    GROUP BY HOUR(entry_time)
    ORDER BY hour
    """)
    parking_usage_data = cursor.fetchall()
    
    conn.close()

    return render_template('admin.html',
                         companies=companies,
                         stats=stats,
                         parking_usage_data=parking_usage_data,
                         user={'username': session.get('username'),
                               'role': session.get('role')})

@admin_bp.route('/admin/companies/<int:company_id>/bonus_hours', methods=['PUT'])
@admin_required
def update_company_bonus_hours(company_id):
    data = request.json
    max_bonus_hours = data.get('max_bonus_hours')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE companies 
            SET max_bonus_hours = %s 
            WHERE id = %s
        """, (max_bonus_hours, company_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        conn.close()

@admin_bp.route('/admin/companies', methods=['POST'])
@admin_required
def add_company():
    data = request.json
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Brak danych w żądaniu'
        }), 400
    
    name = data.get('name')
    max_bonus_hours = data.get('max_bonus_hours')
    
    if not name or max_bonus_hours is None:
        return jsonify({
            'success': False,
            'error': 'Brak wymaganych pól: name, max_bonus_hours'
        }), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Wstawiamy nową firmę
        cursor.execute("""
            INSERT INTO companies (name, max_bonus_hours) 
            VALUES (%s, %s)
        """, (name, max_bonus_hours))
        
        # Pobieramy ID ostatnio wstawionego wiersza
        company_id = cursor.lastrowid
        
        # Commitujemy transakcję
        conn.commit()
        
        # Pobieramy dane nowo utworzonej firmy
        cursor.execute("""
            SELECT id, name, max_bonus_hours
            FROM companies
            WHERE id = %s
        """, (company_id,))
        
        company = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'company': {
                'id': company[0],
                'name': company[1],
                'max_bonus_hours': company[2]
            }
        })
    except Exception as e:
        conn.rollback()
        print(f"Error adding company: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/admin/companies/<int:company_id>', methods=['DELETE'])
@admin_required
def delete_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if company has active parking entries
        print("company_id ", company_id)
        cursor.execute("""
            SELECT COUNT(*) FROM parking_entries 
            WHERE company_checkin_id = %s AND exit_time IS NULL
        """, (company_id,))
        
        active_entries = cursor.fetchone()[0]
        
        if active_entries > 0:
            return jsonify({
                'success': False, 
                'error': 'Nie można usunąć firmy z aktywnymi pojazdami na parkingu'
            }), 400
            
        cursor.execute("DELETE FROM companies WHERE id = %s", (company_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        conn.close()