import RPi.GPIO as GPIO
from mfrc522 import MFRC522
from buzzer import test as buzz
from connect_to_db import connect_to_database
from company_display import CompanyDisplay
from config import *
import datetime
import time

class CompanyCheckInSystem:
    def __init__(self, company_id=1):
        self.company_id = company_id
        self.display = CompanyDisplay()
        self.reader = MFRC522()
        
        self.editing_mode = False
        self.current_hours = 0
        self.max_hours = 0
        

        self.encoder_left = encoderLeft
        self.encoder_right = encoderRight

        GPIO.setup(self.encoder_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.encoder_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.encoder_left_previous_state = GPIO.input(self.encoder_left)
        self.encoder_right_previous_state = GPIO.input(self.encoder_right)
        # Rejestracja zdarzeń
        GPIO.add_event_detect(buttonGreen, GPIO.FALLING, self.button_callback, bouncetime=5000)
        GPIO.add_event_detect(self.encoder_left, GPIO.FALLING, callback=self.encoder_callback, bouncetime=100)
        GPIO.add_event_detect(self.encoder_right, GPIO.FALLING, callback=self.encoder_callback, bouncetime=100)

    def connect_db(self):
        return connect_to_database()

    def button_callback(self, channel):
        print("bttn")
        if not self.editing_mode:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT max_bonus_hours FROM companies WHERE id = %s", (self.company_id,))
                result = cursor.fetchone()
                self.max_hours = result[0] if result else 0
                self.current_hours = self.max_hours
            
            self.editing_mode = True
            self.display.show_edit_mode(self.current_hours)
        else:
            self.save_hours_to_db()
            self.display.show_confirmation(f"NEW: {self.current_hours}H")
            time.sleep(2)
            self.editing_mode = False

    def encoder_callback(self, channel):
        encoder_left_current_state = GPIO.input(self.encoder_left)
        encoder_right_current_state = GPIO.input(self.encoder_right)
        
        if self.editing_mode:
            if self.encoder_left_previous_state == 1 and encoder_left_current_state == 0:
                self.current_hours = min(self.current_hours + 1, 24)
                self.display.show_edit_mode(self.current_hours)
                time.sleep(0.1)  # Small delay to prevent screen flickering
            elif self.encoder_right_previous_state == 1 and encoder_right_current_state == 0:
                self.current_hours = max(self.current_hours - 1, 0)
                self.display.show_edit_mode(self.current_hours)
                time.sleep(0.1)  # Small delay to prevent screen flickering
            print(self.current_hours)
                
        self.encoder_left_previous_state = encoder_left_current_state
        self.encoder_right_previous_state = encoder_right_current_state

    def save_hours_to_db(self):
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE companies 
                    SET max_bonus_hours = %s 
                    WHERE id = %s
                """, (self.current_hours, self.company_id))
                conn.commit()
        except Exception as e:
            print(f"Error saving hours: {e}")
            self.display.show_error("Save failed!")

    def process_check_in(self, conn, card_id):
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, company_checkin_id 
                FROM parking_entries 
                WHERE rfid_tag = %s AND exit_time IS NULL
            """, (card_id,))
            active_parking = cursor.fetchone()

            if not active_parking:
                return "NO_ACTIVE_SESSION"

            if active_parking[1] == self.company_id:
                return "ALREADY_CHECKED_IN"

            cursor.execute("""
                UPDATE parking_entries 
                SET company_checkin_id = %s
                WHERE id = %s
            """, (self.company_id, active_parking[0]))
            
            conn.commit()
            return "CHECK_IN_SUCCESS"

        except Exception as e:
            print(f"Error processing check-in: {e}")
            return "ERROR"

    def handle_no_active_session(self, card_id):
        print(f"Vehicle {card_id} has no active parking session.")
        self.display.show_no_active_session(card_id)
        time.sleep(2)

    def handle_already_checked_in(self, card_id):
        print(f"Vehicle {card_id} is already checked in at company {self.company_id}.")
        self.display.show_already_checked_in(self.company_id)
        time.sleep(2)

    def handle_check_in_success(self, card_id):
        print(f"Vehicle {card_id} successfully checked in at company {self.company_id}.")
        self.display.show_check_in_success(self.company_id)
        time.sleep(2)

    def handle_error(self, card_id, error):
        error_msg = f"Error processing card ID {card_id}: {error}"
        print(error_msg)
        self.display.show_error(str(error))
        time.sleep(2)


    def run(self):
        try:
            print("Company check-in system ready. Please scan card.")
            while True:
                if not self.editing_mode:
                    self.display.show_waiting_screen(self.company_id)
                    status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
                    if status == self.reader.MI_OK:
                        status, uid = self.reader.MFRC522_Anticoll()
                        if status == self.reader.MI_OK:
                            card_id = "".join([str(x) for x in uid])
                            buzz()
                            try:
                                with self.connect_db() as conn:
                                    check_in_status = self.process_check_in(conn, card_id)
                                    
                                    if check_in_status == "NO_ACTIVE_SESSION":
                                        self.handle_no_active_session(card_id)
                                    elif check_in_status == "ALREADY_CHECKED_IN":
                                        self.handle_already_checked_in(card_id)
                                    elif check_in_status == "CHECK_IN_SUCCESS":
                                        self.handle_check_in_success(card_id)
                                    else:
                                        self.handle_error(card_id, check_in_status)

                            except Exception as e:
                                self.handle_error(card_id, e)

        except KeyboardInterrupt:
            print("Program terminated.")
        finally:
            GPIO.cleanup()

def main():
    company = CompanyCheckInSystem(company_id=2)
    company.run()


if __name__ == "__main__":
    main()