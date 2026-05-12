from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('user_rol') != 'admin':
            flash('Acceso restringido solo para administradores', 'danger')
            return redirect(url_for('pedidos.lista'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin/reporte/ventas')
@admin_required
def reporte_ventas():
    from app import mysql
    import csv
    from io import StringIO
    from flask import make_response
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id_factura, f.num_pedido, f.fecha_pago, f.total, f.metodo_pago, 
               c.nombre as cliente, m.numero as mesa
        FROM factura f
        JOIN pedido p ON f.num_pedido = p.num_pedido
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN mesa m ON p.id_mesa = m.id_mesa
        ORDER BY f.fecha_pago DESC
    """)
    ventas = cur.fetchall()
    cur.close()

    # Generar CSV en memoria
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID Factura', 'Num Pedido', 'Fecha', 'Total', 'Metodo Pago', 'Cliente', 'Mesa'])
    
    for v in ventas:
        cw.writerow([
            v['id_factura'], 
            v['num_pedido'], 
            v['fecha_pago'], 
            v['total'], 
            v['metodo_pago'], 
            v['cliente'], 
            v['mesa']
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=reporte_ventas.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    from app import mysql
    from datetime import date
    cur = mysql.connection.cursor()
    
    # 1. Ventas de hoy
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total_hoy 
        FROM factura 
        WHERE DATE(fecha_pago) = CURDATE()
    """)
    ventas_hoy = cur.fetchone()['total_hoy']
    
    # 2. Pedidos activos (no pagados)
    cur.execute("SELECT COUNT(*) as activos FROM pedido WHERE estado != 'pagado'")
    pedidos_activos = cur.fetchone()['activos']
    
    # 3. Plato más vendido (TOP 5)
    cur.execute("""
        SELECT pl.nombre, SUM(dp.cantidad) as total_vendido
        FROM detalle_pedido dp
        JOIN plato pl ON dp.id_plato = pl.id_plato
        GROUP BY pl.id_plato
        ORDER BY total_vendido DESC
        LIMIT 5
    """)
    top_platos = cur.fetchall()
    
    # 4. Ventas por categoría
    cur.execute("""
        SELECT c.nombre, SUM(dp.cantidad * dp.precio_unit) as total
        FROM detalle_pedido dp
        JOIN plato pl ON dp.id_plato = pl.id_plato
        JOIN categoria c ON pl.id_categoria = c.id_categoria
        GROUP BY c.id_categoria
    """)
    ventas_categoria = cur.fetchall()
    
    cur.close()
    return render_template('admin/dashboard.html', 
                           ventas_hoy=ventas_hoy, 
                           pedidos_activos=pedidos_activos,
                           top_platos=top_platos,
                           ventas_categoria=ventas_categoria)

@admin_bp.route('/admin/usuarios')
@admin_required
def usuarios_lista():
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario, nombre, correo, rol, activo FROM usuario ORDER BY rol, nombre")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@admin_required
def usuarios_nuevo():
    from app import mysql, bcrypt
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        rol = request.form['rol']
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuario (nombre, correo, password_hash, rol)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, hashed_pw, rol))
        mysql.connection.commit()
        cur.close()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin.usuarios_lista'))
    return render_template('admin/usuario_form.html', usuario=None)

@admin_bp.route('/admin/usuarios/eliminar/<int:id>')
@admin_required
def usuarios_eliminar(id):
    from app import mysql
    if id == session.get('user_id'):
        flash('No puedes eliminarte a ti mismo', 'danger')
        return redirect(url_for('admin.usuarios_lista'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuario WHERE id_usuario=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado', 'warning')
    return redirect(url_for('admin.usuarios_lista'))

@admin_bp.route('/admin/meseros')
@admin_required
def meseros_lista():
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM empleado WHERE cargo='mesero' ORDER BY nombre")
    meseros = cur.fetchall()
    cur.close()
    return render_template('admin/meseros.html', meseros=meseros)

@admin_bp.route('/admin/meseros/nuevo', methods=['GET', 'POST'])
@admin_required
def meseros_nuevo():
    from app import mysql
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO empleado (nombre, cargo, telefono)
            VALUES (%s, 'mesero', %s)
        """, (nombre, telefono))
        mysql.connection.commit()
        cur.close()
        flash('Mesero agregado correctamente', 'success')
        return redirect(url_for('admin.meseros_lista'))
    return render_template('admin/mesero_form.html', mesero=None)

@admin_bp.route('/admin/meseros/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def meseros_editar(id):
    from app import mysql
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        cur.execute("""
            UPDATE empleado SET nombre=%s, telefono=%s WHERE id_empleado=%s
        """, (nombre, telefono, id))
        mysql.connection.commit()
        cur.close()
        flash('Datos del mesero actualizados', 'success')
        return redirect(url_for('admin.meseros_lista'))
    
    cur.execute("SELECT * FROM empleado WHERE id_empleado=%s", (id,))
    mesero = cur.fetchone()
    cur.close()
    return render_template('admin/mesero_form.html', mesero=mesero)

@admin_bp.route('/admin/meseros/eliminar/<int:id>')
@admin_required
def meseros_eliminar(id):
    from app import mysql
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM empleado WHERE id_empleado=%s", (id,))
        mysql.connection.commit()
        flash('Mesero eliminado', 'warning')
    except:
        flash('No se puede eliminar el mesero porque tiene pedidos asociados', 'danger')
    cur.close()
    return redirect(url_for('admin.meseros_lista'))
