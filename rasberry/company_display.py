import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import board
import busio
import adafruit_bme280.advanced as adafruit_bme280
import datetime
from connect_to_db import connect_to_database

class CompanyDisplay:
    def __init__(self):
        self.disp = SSD1331.SSD1331()
        self.disp.Init()
        self.disp.clear()
        
        i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
        
        self.image = Image.new("RGB", (self.disp.width, self.disp.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)
        self.font_large = ImageFont.truetype('./lib/oled/Font.ttf', 20)
        self.font_small = ImageFont.truetype('./lib/oled/Font.ttf', 13)

    def clear_display(self):
        self.draw.rectangle([(0, 0), (self.disp.width, self.disp.height)], fill="WHITE")

    def show_waiting_screen(self, company_id):
        self.clear_display()
        self.draw.text((10, 0), f"Company #{company_id}", font=self.font_small, fill="BLACK")
        self.draw.text((10, 15), "Scan Card", font=self.font_small, fill="BLACK")
        self.disp.ShowImage(self.image, 0, 0)

    def show_no_active_session(self, card_id):
        self.clear_display()
        self.draw.text((10, 0), "No Active", font=self.font_small, fill="BLACK")
        self.draw.text((10, 15), "Parking", font=self.font_small, fill="BLACK")
        self.draw.text((10, 30), "Session", font=self.font_small, fill="BLACK")
        self.draw.text((10, 45), f"Card: {card_id[-4:]}", font=self.font_small, fill="BLACK")
        self.disp.ShowImage(self.image, 0, 0)

    def show_already_checked_in(self, company_id):
        self.clear_display()
        self.draw.text((10, 0), "Already", font=self.font_large, fill="BLACK")
        self.draw.text((10, 25), f"Checked In", font=self.font_small, fill="BLACK")
        self.draw.text((10, 45), f"Company #{company_id}", font=self.font_small, fill="BLACK")
        self.disp.ShowImage(self.image, 0, 0)

    def show_check_in_success(self, company_id):
        self.clear_display()
        self.draw.text((10, 0), "Welcome!", font=self.font_small, fill="BLACK")
        self.draw.text((10, 25), "Check-in", font=self.font_small, fill="BLACK")
        self.draw.text((10, 45), f"Company #{company_id}", font=self.font_small, fill="BLACK")
        self.disp.ShowImage(self.image, 0, 0)

    def show_error(self, error_msg):
        self.clear_display()
        self.draw.text((10, 0), "Error!", font=self.font_large, fill="BLACK")
        words = error_msg.split()
        lines = []
        current_line = []
        for word in words:
            if len(' '.join(current_line + [word])) <= 20:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        for i, line in enumerate(lines[:2]):  
            self.draw.text((10, 25 + i*20), line, font=self.font_small, fill="BLACK")
        self.disp.ShowImage(self.image, 0, 0)

    def show_edit_mode(self, current_hours):
        lines = [
            "EDITING",
            f"Current: {current_hours}h",
            "Press green"
        ]
        self.display_message(lines)
    
    def show_confirmation(self, message):
        lines = [message, "Saved!"]
        self.display_message(lines)

    def display_message(self, lines):
        self.clear_display()
        for i, line in enumerate(lines):
            y_position = i * 20
            self.draw.text((10, y_position), line, font=self.font_small, fill="BLACK")
        self.disp.ShowImage(self.image, 0, 0)