from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps


pedidos_bp = Blueprint('pedidos', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@pedidos_bp.route('/pedidos')
@login_required
def lista():
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, c.nombre as cliente, m.numero as mesa, e.nombre as empleado
        FROM pedido p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN mesa m    ON p.id_mesa    = m.id_mesa
        JOIN empleado e ON p.id_empleado = e.id_empleado
        ORDER BY p.fecha_hora DESC
    """)
    pedidos = cur.fetchall()
    cur.close()
    return render_template('pedidos.html', pedidos=pedidos)

@pedidos_bp.route('/pedidos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    from app import mysql
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        nuevo_cliente_nombre = request.form.get('nuevo_cliente_nombre')
        
        # Si se ingresó un nuevo cliente, lo registramos
        if nuevo_cliente_nombre:
            cur.execute("INSERT INTO cliente (nombre) VALUES (%s)", (nuevo_cliente_nombre,))
            id_cliente = cur.lastrowid
            mysql.connection.commit()

        cur.execute("""
            INSERT INTO pedido (id_cliente, id_mesa, id_empleado, estado)
            VALUES (%s, %s, %s, 'pendiente')
        """, (id_cliente, request.form['id_mesa'], request.form['id_empleado']))
        num_pedido = cur.lastrowid
        platos     = request.form.getlist('id_plato[]')
        cantidades = request.form.getlist('cantidad[]')
        for id_plato, cantidad in zip(platos, cantidades):
            if id_plato and int(cantidad) > 0:
                cur.execute("SELECT precio FROM plato WHERE id_plato=%s", (id_plato,))
                precio = cur.fetchone()['precio']
                cur.execute("""
                    INSERT INTO detalle_pedido (num_pedido, id_plato, cantidad, precio_unit)
                    VALUES (%s, %s, %s, %s)
                """, (num_pedido, id_plato, cantidad, precio))
        cur.execute("UPDATE mesa SET estado='ocupada' WHERE id_mesa=%s", (request.form['id_mesa'],))
        mysql.connection.commit()
        cur.close()
        flash('Pedido creado exitosamente', 'success')
        return redirect(url_for('pedidos.lista'))

    cur.execute("SELECT * FROM cliente ORDER BY nombre")
    clientes = cur.fetchall()
    cur.execute("SELECT * FROM mesa WHERE estado='disponible' ORDER BY numero")
    mesas = cur.fetchall()
    cur.execute("SELECT * FROM empleado WHERE cargo='mesero' ORDER BY nombre")
    empleados = cur.fetchall()
    cur.execute("""
        SELECT p.*, c.nombre as categoria FROM plato p
        JOIN categoria c ON p.id_categoria = c.id_categoria
        WHERE p.disponible = 1 ORDER BY c.nombre, p.nombre
    """)
    platos = cur.fetchall()
    cur.close()
    return render_template('pedido_form.html',
                           clientes=clientes, mesas=mesas,
                           empleados=empleados, platos=platos)

@pedidos_bp.route('/pedidos/comanda/<int:id>')
@login_required
def comanda(id):
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, m.numero as mesa, e.nombre as empleado
        FROM pedido p
        JOIN mesa m ON p.id_mesa = m.id_mesa
        JOIN empleado e ON p.id_empleado = e.id_empleado
        WHERE p.num_pedido=%s
    """, (id,))
    pedido = cur.fetchone()
    
    cur.execute("""
        SELECT dp.*, pl.nombre as plato, pl.descripcion
        FROM detalle_pedido dp
        JOIN plato pl ON dp.id_plato = pl.id_plato
        WHERE dp.num_pedido=%s
    """, (id,))
    detalle = cur.fetchall()
    cur.close()
    return render_template('comanda.html', pedido=pedido, detalle=detalle)

@pedidos_bp.route('/pedidos/agregar-item/<int:id>', methods=['GET', 'POST'])
@login_required
def agregar_item(id):
    from app import mysql
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        platos     = request.form.getlist('id_plato[]')
        cantidades = request.form.getlist('cantidad[]')
        for id_plato, cantidad in zip(platos, cantidades):
            if id_plato and int(cantidad) > 0:
                cur.execute("SELECT precio FROM plato WHERE id_plato=%s", (id_plato,))
                precio = cur.fetchone()['precio']
                # Verificamos si ya existe el plato en el pedido para sumar cantidad
                cur.execute("SELECT id_detalle FROM detalle_pedido WHERE num_pedido=%s AND id_plato=%s", (id, id_plato))
                existente = cur.fetchone()
                if existente:
                    cur.execute("UPDATE detalle_pedido SET cantidad = cantidad + %s WHERE id_detalle=%s", (cantidad, existente['id_detalle']))
                else:
                    cur.execute("""
                        INSERT INTO detalle_pedido (num_pedido, id_plato, cantidad, precio_unit)
                        VALUES (%s, %s, %s, %s)
                    """, (id, id_plato, cantidad, precio))
        mysql.connection.commit()
        cur.close()
        flash('Platos añadidos al pedido exitosamente', 'success')
        return redirect(url_for('pedidos.lista'))

    cur.execute("""
        SELECT p.*, c.nombre as cliente, m.numero as mesa
        FROM pedido p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN mesa m ON p.id_mesa = m.id_mesa
        WHERE p.num_pedido=%s
    """, (id,))
    pedido = cur.fetchone()
    
    cur.execute("SELECT p.*, c.nombre as categoria FROM plato p JOIN categoria c ON p.id_categoria = c.id_categoria WHERE p.disponible = 1 ORDER BY c.nombre, p.nombre")
    platos = cur.fetchall()
    cur.close()
    return render_template('pedido_agregar.html', pedido=pedido, platos=platos)

@pedidos_bp.route('/pedidos/estado/<int:id>/<estado>')
@login_required
def cambiar_estado(id, estado):
    from app import mysql
    estados_validos = ['pendiente', 'en preparacion', 'servido', 'pagado']
    if estado in estados_validos:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE pedido SET estado=%s WHERE num_pedido=%s", (estado, id))
        if estado == 'pagado':
            cur.execute("SELECT id_mesa FROM pedido WHERE num_pedido=%s", (id,))
            mesa = cur.fetchone()
            cur.execute("UPDATE mesa SET estado='disponible' WHERE id_mesa=%s", (mesa['id_mesa'],))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('pedidos.lista'))
