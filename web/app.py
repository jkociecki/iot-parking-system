from flask import Flask, render_template
from routes import auth
from routes import admin
from routes import company
from routes import gate

import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Rejestracja blueprintów
app.register_blueprint(admin.admin_bp)
app.register_blueprint(auth.auth_bp)
app.register_blueprint(company.company_bp)
app.register_blueprint(gate.gate_bp)

@app.route('/')
def home():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)