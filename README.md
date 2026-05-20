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


## Modelo de Base de Datos

8 tablas normalizadas hasta **3FN**:
`usuario` · `cliente` · `mesa` · `empleado` · `categoria` · `plato` · `pedido` · `detalle_pedido` · `factura`
