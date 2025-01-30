from decimal import Decimal

def calculate_parking_fee(entry_time, current_time, company_checkin_id, max_bonus_hours):
    # Oblicz czas parkowania
    duration_hours = (current_time - entry_time).total_seconds() / 3600
    
    # Podstawowa stawka
    HOURLY_RATE = Decimal('10.00')  # 10 zł/h
    
    # Konwertuj duration_hours na Decimal dla spójnych obliczeń
    duration_decimal = Decimal(str(duration_hours))
    
    # Oblicz opłatę
    if company_checkin_id is not None and max_bonus_hours:
        # Jeśli jest przypisana firma, uwzględnij darmowe godziny
        free_hours = Decimal(str(max_bonus_hours))
        billable_hours = max(Decimal('0'), duration_decimal - free_hours)
    else:
        # Bez firmy - płaci za cały czas
        billable_hours = duration_decimal
    
    # Zaokrąglamy billable_hours w górę do pełnych godzin
    billable_hours = billable_hours.quantize(Decimal('1'), rounding='ROUND_UP')
    total_price = billable_hours * HOURLY_RATE
    
    return total_price, duration_hours