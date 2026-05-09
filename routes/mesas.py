from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps
from app import mysql

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
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, COUNT(p.num_pedido) as pedidos_activos
        FROM mesa m
        LEFT JOIN pedido p ON m.id_mesa = p.id_mesa AND p.estado != 'pagado'
        GROUP BY m.id_mesa
        ORDER BY m.numero
    """)
    mesas = cur.fetchall()
    cur.close()
    return render_template('mesas.html', mesas=mesas)
