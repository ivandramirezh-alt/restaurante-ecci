"""
create_users.py — Ejecutar una sola vez para crear usuarios con contraseñas encriptadas
Uso: python create_users.py
"""
from flask_bcrypt import Bcrypt
import MySQLdb
from dotenv import load_dotenv
import os

load_dotenv()
bcrypt = Bcrypt()

usuarios = [
    ('Administrador', 'admin@restaurante.com',  'admin123',   'admin'),
    ('Carlos Mesero', 'carlos@restaurante.com', 'mesero123',  'mesero'),
    ('María Cajero',  'maria@restaurante.com',  'cajero123',  'cajero'),
    ('Pedro Cocinero','pedro@restaurante.com',  'cocina123',  'cocinero'),
]

db = MySQLdb.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    passwd=os.getenv('MYSQL_PASSWORD', ''),
    db=os.getenv('MYSQL_DB', 'restaurante_db'),
    port=int(os.getenv('PORT', 3306))
)
cur = db.cursor()

# Limpiar usuarios anteriores
cur.execute("DELETE FROM usuario")

for nombre, correo, password, rol in usuarios:
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute("""
        INSERT INTO usuario (nombre, correo, password_hash, rol, activo)
        VALUES (%s, %s, %s, %s, 1)
    """, (nombre, correo, hashed, rol))
    print(f"✓ Usuario creado: {correo} [{rol}]")

db.commit()
cur.close()
db.close()
print("\n✅ Usuarios creados exitosamente.")
print("Ya puedes ejecutar: python app.py")
