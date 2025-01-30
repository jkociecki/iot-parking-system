from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from config import get_db_connection, login_required
from datetime import datetime
from utils.parking import calculate_parking_fee

gate_bp = Blueprint('gate', __name__)

# Stała konfiguracyjna dla limitu miejsc
PARKING_CAPACITY = 12  # Możesz dostosować tę wartość

@gate_bp.route('/gate')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get active vehicles - zmieniona kolejność sortowania
    cursor.execute("""
        SELECT pe.*, c.name as company_name 
        FROM parking_entries pe
        LEFT JOIN companies c ON pe.company_checkin_id = c.id
        WHERE pe.exit_time IS NULL
        ORDER BY pe.entry_time DESC  # Zmienione sortowanie
    """)
    active_vehicles = cursor.fetchall()
    
    # Get last scanned card
    cursor.execute("""
        SELECT rfid_tag, entry_time
        FROM parking_entries
        ORDER BY entry_time DESC
        LIMIT 1
    """)
    last_card = cursor.fetchone()
    
    # Get current parking occupancy
    occupied_spaces = len(active_vehicles)
    available_spaces = PARKING_CAPACITY - occupied_spaces
    
    conn.close()
    user = {
        'username': session.get('username'),
        'role': session.get('role')
    }
    return render_template('gate.html',
                         active_vehicles=active_vehicles,
                         last_card=last_card,
                         user=user,
                         parking_capacity=PARKING_CAPACITY,
                         occupied_spaces=occupied_spaces,
                         available_spaces=available_spaces)

@gate_bp.route('/gate/last-card')
@login_required
def get_last_card():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT rfid_tag, entry_time
        FROM parking_entries
        ORDER BY entry_time DESC
        LIMIT 1
    """)
    last_card = cursor.fetchone()
    conn.close()
    
    if last_card:
        return jsonify({
            'success': True,
            'rfid_tag': last_card['rfid_tag'],
            'entry_time': last_card['entry_time'].strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'success': False})

@gate_bp.route('/gate/entry', methods=['POST'])
@login_required
def register_entry():
    rfid_tag = request.form.get('rfid_tag')
    
    if not rfid_tag:
        return jsonify({
            'success': False,
            'error': 'Brak numeru karty',
            'message': 'Proszę wprowadzić numer karty'
        }), 400
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Sprawdź czy karta nie jest już używana (nie ma niezakończonego wjazdu)
        cursor.execute("""
            SELECT id FROM parking_entries 
            WHERE rfid_tag = %s AND exit_time IS NULL
        """, (rfid_tag,))
        
        existing_entry = cursor.fetchone()
        if existing_entry:
            return jsonify({
                'success': False,
                'error': 'duplicate_entry',
                'message': 'Ta karta jest już zarejestrowana na parkingu. Najpierw należy zarejestrować wyjazd.'
            }), 409

        # Sprawdź dostępność miejsc
        cursor.execute("SELECT COUNT(*) as count FROM parking_entries WHERE exit_time IS NULL")
        current_count = cursor.fetchone()['count']
        
        if current_count >= PARKING_CAPACITY:
            return jsonify({
                'success': False,
                'error': 'parking_full',
                'message': 'Brak wolnych miejsc parkingowych'
            }), 409
        
        # Register entry
        current_time = datetime.now()
        cursor.execute("""
            INSERT INTO parking_entries (rfid_tag, entry_time) 
            VALUES (%s, %s)
        """, (rfid_tag, current_time))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Wjazd zarejestrowany pomyślnie o {current_time.strftime("%H:%M:%S")}',
            'entry_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'error': 'server_error',
            'message': 'Wystąpił błąd podczas rejestracji wjazdu',
            'details': str(e)
        }), 500
    finally:
        conn.close()

@gate_bp.route('/gate/exit', methods=['POST'])
@login_required
def register_exit():
    rfid_tag = request.json.get('rfid_tag')
    
    if not rfid_tag:
        return jsonify({'error': 'Brak numeru karty'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get entry info with company bonus hours
        cursor.execute("""
            SELECT pe.*, c.max_bonus_hours, c.name as company_name
            FROM parking_entries pe
            LEFT JOIN companies c ON pe.company_checkin_id = c.id
            WHERE pe.rfid_tag = %s AND pe.exit_time IS NULL
        """, (rfid_tag,))
        
        entry = cursor.fetchone()
        if not entry:
            return jsonify({'error': 'Nie znaleziono aktywnego wjazdu'}), 404
            
        current_time = datetime.now()
        
        # Oblicz opłatę używając funkcji z utils
        total_price, duration_hours = calculate_parking_fee(
            entry['entry_time'],
            current_time,
            entry['company_checkin_id'],
            entry['max_bonus_hours']
        )
        
        # Update parking entry
        cursor.execute("""
            UPDATE parking_entries 
            SET exit_time = %s,
                duration = %s,
                total_price = %s
            WHERE id = %s
        """, (current_time, duration_hours, total_price, entry['id']))
        
        conn.commit()
        
        message = f"Do zapłaty: {total_price:.2f} PLN"
        if entry['company_name']:
            message += f"\nFirma: {entry['company_name']}"
            if entry['max_bonus_hours']:
                message += f"\nDarmowe godziny: {entry['max_bonus_hours']}"
        
        return jsonify({
            'success': True,
            'duration': round(duration_hours, 2),
            'total_price': float(total_price),
            'message': message
        })
        
    except Exception as e:
        conn.rollback()
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500
        
    finally:
        conn.close()

@gate_bp.route('/gate/parking-status')
@login_required
def get_parking_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Pobierz aktualny stan parkingu
    cursor.execute("SELECT COUNT(*) as occupied FROM parking_entries WHERE exit_time IS NULL")
    occupied = cursor.fetchone()['occupied']
    
    conn.close()
    print(occupied)
    print(PARKING_CAPACITY)
    print(PARKING_CAPACITY - occupied)
    
    return jsonify({
        'occupied': occupied,
        'available': PARKING_CAPACITY - occupied,
        'total': PARKING_CAPACITY
    })