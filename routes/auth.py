from flask import Blueprint, render_template, request, redirect, url_for, flash, session


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import mysql, bcrypt
    if request.method == 'POST':
        correo   = request.form['correo']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE correo=%s AND activo=1", (correo,))
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id']     = user['id_usuario']
            session['user_nombre'] = user['nombre']
            session['user_rol']    = user['rol']
            flash('Bienvenido ' + user['nombre'], 'success')
            return redirect(url_for('pedidos.lista'))
        flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
