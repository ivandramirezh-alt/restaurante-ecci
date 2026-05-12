from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps


menu_bp = Blueprint('menu', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@menu_bp.route('/menu')
@login_required
def lista():
    from app import mysql
    cur = mysql.connection.cursor()
    # Intentamos traer imagen_url, si falla es que el usuario no ha corrido el SQL
    try:
        cur.execute("""
            SELECT p.*, c.nombre as categoria FROM plato p
            JOIN categoria c ON p.id_categoria = c.id_categoria
            ORDER BY c.nombre, p.nombre
        """)
    except:
        cur.execute("""
            SELECT p.*, c.nombre as categoria, NULL as imagen_url FROM plato p
            JOIN categoria c ON p.id_categoria = c.id_categoria
            ORDER BY c.nombre, p.nombre
        """)
        
    platos = cur.fetchall()
    cur.execute("SELECT * FROM categoria ORDER BY nombre")
    categorias = cur.fetchall()
    cur.close()
    return render_template('menu.html', platos=platos, categorias=categorias)

@menu_bp.route('/menu/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    from app import mysql
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        imagen_url = request.form.get('imagen_url')
        try:
            cur.execute("""
                INSERT INTO plato (id_categoria, nombre, descripcion, precio, disponible, imagen_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.form['id_categoria'], request.form['nombre'],
                  request.form['descripcion'], request.form['precio'],
                  1 if 'disponible' in request.form else 0, imagen_url))
        except:
             cur.execute("""
                INSERT INTO plato (id_categoria, nombre, descripcion, precio, disponible)
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['id_categoria'], request.form['nombre'],
                  request.form['descripcion'], request.form['precio'],
                  1 if 'disponible' in request.form else 0))
                  
        mysql.connection.commit()
        cur.close()
        flash('Plato agregado exitosamente', 'success')
        return redirect(url_for('menu.lista'))
    cur.execute("SELECT * FROM categoria ORDER BY nombre")
    categorias = cur.fetchall()
    cur.close()
    return render_template('menu_form.html', categorias=categorias, plato=None)

@menu_bp.route('/menu/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    from app import mysql
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        imagen_url = request.form.get('imagen_url')
        try:
            cur.execute("""
                UPDATE plato SET id_categoria=%s, nombre=%s, descripcion=%s,
                precio=%s, disponible=%s, imagen_url=%s WHERE id_plato=%s
            """, (request.form['id_categoria'], request.form['nombre'],
                  request.form['descripcion'], request.form['precio'],
                  1 if 'disponible' in request.form else 0, imagen_url, id))
        except:
            cur.execute("""
                UPDATE plato SET id_categoria=%s, nombre=%s, descripcion=%s,
                precio=%s, disponible=%s WHERE id_plato=%s
            """, (request.form['id_categoria'], request.form['nombre'],
                  request.form['descripcion'], request.form['precio'],
                  1 if 'disponible' in request.form else 0, id))
                  
        mysql.connection.commit()
        cur.close()
        flash('Plato actualizado', 'success')
        return redirect(url_for('menu.lista'))
        
    try:
        cur.execute("SELECT * FROM plato WHERE id_plato=%s", (id,))
    except:
        # Fallback si no existe la columna
        cur.execute("SELECT *, NULL as imagen_url FROM plato WHERE id_plato=%s", (id,))
        
    plato = cur.fetchone()
    cur.execute("SELECT * FROM categoria ORDER BY nombre")
    categorias = cur.fetchall()
    cur.close()
    return render_template('menu_form.html', categorias=categorias, plato=plato)

@menu_bp.route('/menu/toggle/<int:id>')
@login_required
def toggle(id):
    from app import mysql
    cur = mysql.connection.cursor()
    cur.execute("UPDATE plato SET disponible = NOT disponible WHERE id_plato=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('menu.lista'))
