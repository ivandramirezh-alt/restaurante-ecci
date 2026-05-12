from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps

factura_bp = Blueprint('factura', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@factura_bp.route('/factura/<int:id>', methods=['GET', 'POST'])
@login_required
def generar(id):
    from app import mysql
    cur = mysql.connection.cursor()

    # Verificar si ya existe una factura para este pedido (evita el IntegrityError)
    cur.execute("SELECT id_factura FROM factura WHERE num_pedido=%s", (id,))
    if cur.fetchone():
        # SI YA EXISTE (por un error previo), forzamos la actualización del estado para que no se quede trabado
        cur.execute("UPDATE pedido SET estado='pagado' WHERE num_pedido=%s", (id,))
        cur.execute("SELECT id_mesa FROM pedido WHERE num_pedido=%s", (id,))
        mesa = cur.fetchone()
        if mesa:
            cur.execute("UPDATE mesa SET estado='disponible' WHERE id_mesa=%s", (mesa['id_mesa'],))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('factura.ver', id=id))

    if request.method == 'POST':
        cur.execute("""
            SELECT SUM(cantidad * precio_unit) as subtotal
            FROM detalle_pedido WHERE num_pedido=%s
        """, (id,))
        subtotal = float(cur.fetchone()['subtotal'])
        iva      = round(subtotal * 0.19, 2)
        total    = round(subtotal + iva, 2)
        cur.execute("""
            INSERT INTO factura (num_pedido, subtotal, iva, total, metodo_pago)
            VALUES (%s, %s, %s, %s, %s)
        """, (id, subtotal, iva, total, request.form['metodo_pago']))
        cur.execute("UPDATE pedido SET estado='pagado' WHERE num_pedido=%s", (id,))
        cur.execute("SELECT id_mesa FROM pedido WHERE num_pedido=%s", (id,))
        mesa = cur.fetchone()
        cur.execute("UPDATE mesa SET estado='disponible' WHERE id_mesa=%s", (mesa['id_mesa'],))
        mysql.connection.commit()
        cur.close()
        flash('Factura generada exitosamente', 'success')
        return redirect(url_for('pedidos.lista'))

    cur.execute("""
        SELECT p.*, c.nombre as cliente, m.numero as mesa
        FROM pedido p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN mesa m    ON p.id_mesa    = m.id_mesa
        WHERE p.num_pedido=%s
    """, (id,))
    pedido = cur.fetchone()
    cur.execute("""
        SELECT dp.*, pl.nombre as plato
        FROM detalle_pedido dp JOIN plato pl ON dp.id_plato = pl.id_plato
        WHERE dp.num_pedido=%s
    """, (id,))
    detalle = cur.fetchall()
    cur.close()
    subtotal = sum(float(d['cantidad']) * float(d['precio_unit']) for d in detalle)
    iva      = round(subtotal * 0.19, 2)
    total    = round(subtotal + iva, 2)
    return render_template('factura.html', pedido=pedido, detalle=detalle,
                           subtotal=subtotal, iva=iva, total=total)

@factura_bp.route('/factura/ver/<int:id>')
@login_required
def ver(id):
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.*, c.nombre as cliente, m.numero as mesa
        FROM factura f
        JOIN pedido p  ON f.num_pedido = p.num_pedido
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN mesa m    ON p.id_mesa    = m.id_mesa
        WHERE f.num_pedido=%s
    """, (id,))
    factura = cur.fetchone()
    cur.execute("""
        SELECT dp.*, pl.nombre as plato
        FROM detalle_pedido dp JOIN plato pl ON dp.id_plato = pl.id_plato
        WHERE dp.num_pedido=%s
    """, (id,))
    detalle = cur.fetchall()
    cur.close()
    return render_template('factura_ver.html', factura=factura, detalle=detalle)
