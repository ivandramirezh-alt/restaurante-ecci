# 🍽️ Sistema de Gestión de Pedidos — Restaurante El Buen Sabor

**Universidad ECCI — Gestión Base de Datos**  
Barón 61986 | Ramírez 83427 | Andrade 151451

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3 + Flask |
| Base de datos | MySQL |

---

## Estructura del proyecto

```
restaurante/
├── app.py                  ← Aplicación principal Flask
├── database.sql            ← Script SQL completo (tablas + datos de prueba)
├── requirements.txt        ← Dependencias Python
├── .env                    ← Variables de entorno (NO subir a GitHub)
├── .gitignore
├── routes/
│   ├── auth.py             ← Login / Logout
│   ├── pedidos.py          ← CRUD pedidos
│   ├── menu.py             ← CRUD menú y platos
│   ├── mesas.py            ← Estado de mesas
│   └── factura.py          ← Generación de facturas
├── templates/
│   ├── base.html           ← Layout base con navbar
│   ├── login.html
│   ├── pedidos.html
│   ├── pedido_form.html
│   ├── menu.html
│   ├── menu_form.html
│   ├── mesas.html
│   ├── factura.html
│   └── factura_ver.html
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## Instalación y ejecución local

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/restaurante-ecci.git
cd restaurante-ecci
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar base de datos
```bash
# Crear la base de datos en MySQL
mysql -u root -p < database.sql
```

### 4. Configurar variables de entorno
Crea el archivo `.env` en la raíz:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DB=restaurante_db
SECRET_KEY=una_clave_secreta_larga
```

### 5. Ejecutar la aplicación
```bash
python app.py
```

Abrir en el navegador: **http://localhost:5000**

---

## Usuarios de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Admin | admin@restaurante.com | admin123 |
| Mesero | carlos@restaurante.com | mesero123 |
| Cajero | maria@restaurante.com | cajero123 |

> ⚠️ Ejecuta el script `create_users.py` para generar los hashes de contraseña correctamente.

---

## Funcionalidades

- ✅ Login con roles (admin, mesero, cajero, cocinero)
- ✅ Gestión de pedidos con detalle de platos
- ✅ Control de estado de mesas en tiempo real
- ✅ CRUD completo del menú por categorías
- ✅ Facturación automática con IVA (19%)
- ✅ Contraseñas encriptadas con bcrypt

---

## Modelo de Base de Datos

8 tablas normalizadas hasta **3FN**:
`usuario` · `cliente` · `mesa` · `empleado` · `categoria` · `plato` · `pedido` · `detalle_pedido` · `factura`
