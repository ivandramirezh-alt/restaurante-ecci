from flask import Flask, render_template, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret')

# MySQL config
app.config['MYSQL_HOST']     = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER']     = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB']       = os.getenv('MYSQL_DB', 'restaurante_db')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT']     = int(os.getenv('MYSQL_PORT', 23828)) 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql  = MySQL(app)
bcrypt = Bcrypt(app)

# Importar rutas
from routes.auth    import auth_bp
from routes.pedidos import pedidos_bp
from routes.menu    import menu_bp
from routes.mesas   import mesas_bp
from routes.factura import factura_bp
from routes.admin   import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(pedidos_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(mesas_bp)
app.register_blueprint(factura_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('pedidos.lista'))

if __name__ == '__main__':
    app.run(debug=True)
