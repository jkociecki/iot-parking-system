# Parking Management System 🅿️

Comprehensive parking management system integrating Raspberry Pi hardware, a database, and web panels.  

---

## 📖 Project Overview
The system automates parking operations through:
- **Entry/exit registration** using RFID cards.
- **Real-time fee calculation** displayed on a Raspberry Pi screen at the exit.
- **Free-hour management** by companies located on the premises.
- Three dedicated web panels:
  - **Admin** (statistics monitoring, company management),
  - **Barrier Control** (visit registration, activity history),
  - **Company** (adding free hours for clients).

### System Components
- 🖥️ **Raspberry Pi** – controls barriers and RFID readers in companies.
- 🗄️ **Database** – stores user data, company details, and transactions.
- 🌐 **Web Application** – Flask (Python) with panels for admins, companies, and barrier control.

---

## 🚀 Features
### For Drivers
- RFID card scanning at entry/exit.
- Automated fee calculation (displayed at exit).
- Extend parking time by scanning their card at a company.

### For Companies
- **Management panel** – set maximum free hours for clients.
- Real-time registration of additional free hours.

### For Admins
- Monitor statistics: revenue, average parking time, vehicle count.
- Manage companies (add, edit, remove).
- View full visit history.

---

## ⚙️ Technical Requirements
- **Hardware:**
  - Raspberry Pi 4 (barriers + company devices).
  - RFID readers (e.g., RC522).
  - LCD display for Raspberry Pi at the exit.
- **Software:**
  - Python 3.8+.
  - Flask, SQLAlchemy, RPi.GPIO.
  - Database MySQL.

---

| ![att QYUFGkU23LhSbX0Ecb5EKe2mfQ4yIMhfyZ43giHrgbI](https://github.com/user-attachments/assets/d0a029cc-0504-47f6-ac02-4780bbd9c535) | ![att migL76S3U2AV9Gp6TvQO8y-78iwx8hTP9P7ALrQyCrs](https://github.com/user-attachments/assets/8f6689bf-716e-45e2-ac2e-c3122f51d1e2) | ![att Qy4fZOkx0M8geRl5PdBJI2UmfU3cqw8HS3A6OL7jFyk](https://github.com/user-attachments/assets/13853907-a866-41a3-8ae4-3b9c526a4a80) |
| :---:   | :---: | :---: |
| ![att qiKIbTtnbkuDZ0YVqhSjfFiGC_euJAUUbmdqog8rFyw](https://github.com/user-attachments/assets/14dc4a5f-602a-4347-9fc8-a1b4790bd50d) | ![att W23TWU8wHBPpk7keVLnS9A3WIjWzpD5VsWFG2H20Y0I](https://github.com/user-attachments/assets/b38fdee3-fc51-4738-b2e0-30f4fcc55661) | ![att s1r4d-bLrui_TxeamDtFZ2OTdRzi4pSt84XEekyxvrA](https://github.com/user-attachments/assets/4f364492-bcb2-4e52-85bf-37aeb95f1300) |

![att 1UDp7BaLN14hSD9Qhb6BsUXRBiVwuRv0scRU2i44NyE](https://github.com/user-attachments/assets/4f56516b-d235-4aaa-9948-c4ac2a5ccae9)
