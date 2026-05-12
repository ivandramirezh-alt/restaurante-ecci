from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps

mesas_bp = Blueprint('mesas', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@mesas_bp.route('/mesas')
@login_required
def lista():
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, 
               (SELECT COUNT(*) FROM pedido p WHERE p.id_mesa = m.id_mesa AND p.estado != 'pagado') as pedidos_activos
        FROM mesa m 
        ORDER BY numero
    """)
    mesas = cur.fetchall()
    cur.close()
    return render_template('mesas.html', mesas=mesas)

@mesas_bp.route('/mesas/mapa')
@login_required
def mapa():
    from app import mysql
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT m.*, 
                   (SELECT COUNT(*) FROM pedido p WHERE p.id_mesa = m.id_mesa AND p.estado != 'pagado') as pedidos_activos
            FROM mesa m 
            ORDER BY numero
        """)
    except:
        cur.execute("""
            SELECT id_mesa, numero, capacidad, estado, 0 as pos_x, 0 as pos_y,
                   (SELECT COUNT(*) FROM pedido p WHERE p.id_mesa = m.id_mesa AND p.estado != 'pagado') as pedidos_activos
            FROM mesa m 
            ORDER BY numero
        """)
    mesas = cur.fetchall()
    cur.close()
    return render_template('mesas_mapa.html', mesas=mesas)

@mesas_bp.route('/mesas/guardar-posiciones', methods=['POST'])
@login_required
def guardar_posiciones():
    from app import mysql
    data = request.get_json()
    positions = data.get('positions', [])
    
    cur = mysql.connection.cursor()
    for pos in positions:
        try:
            cur.execute("UPDATE mesa SET pos_x=%s, pos_y=%s WHERE id_mesa=%s", (pos['x'], pos['y'], pos['id']))
        except:
            # Si no existen las columnas, las creamos al vuelo
            cur.execute("ALTER TABLE mesa ADD COLUMN pos_x INT DEFAULT 0, ADD COLUMN pos_y INT DEFAULT 0")
            cur.execute("UPDATE mesa SET pos_x=%s, pos_y=%s WHERE id_mesa=%s", (pos['x'], pos['y'], pos['id']))
    
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True})
