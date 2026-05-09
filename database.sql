-- ============================================
-- RESTAURANTE "EL BUEN SABOR" - Base de Datos
-- Universidad ECCI - Gestión Base de Datos
-- Barón 61986 | Ramírez 83427 | Andrade 151451
-- ============================================

CREATE DATABASE IF NOT EXISTS restaurante_db;
USE restaurante_db;

-- TABLA USUARIO (login y roles)
CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin','mesero','cajero','cocinero') NOT NULL,
    activo TINYINT(1) DEFAULT 1
);

-- TABLA CLIENTE
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE,
    fecha_registro DATE DEFAULT (CURDATE())
);

-- TABLA MESA
CREATE TABLE mesa (
    id_mesa INT AUTO_INCREMENT PRIMARY KEY,
    numero INT UNIQUE NOT NULL,
    capacidad INT NOT NULL,
    estado ENUM('disponible','ocupada') DEFAULT 'disponible'
);

-- TABLA EMPLEADO
CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cargo ENUM('mesero','cocinero','cajero','administrador') NOT NULL,
    telefono VARCHAR(20)
);

-- TABLA CATEGORIA
CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- TABLA PLATO
CREATE TABLE plato (
    id_plato INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    disponible TINYINT(1) DEFAULT 1,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
);

-- TABLA PEDIDO
CREATE TABLE pedido (
    num_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_mesa INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha_hora DATETIME DEFAULT NOW(),
    estado ENUM('pendiente','en preparacion','servido','pagado') DEFAULT 'pendiente',
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    FOREIGN KEY (id_mesa) REFERENCES mesa(id_mesa),
    FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
);

-- TABLA DETALLE_PEDIDO
CREATE TABLE detalle_pedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    num_pedido INT NOT NULL,
    id_plato INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad >= 1),
    precio_unit DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (num_pedido) REFERENCES pedido(num_pedido),
    FOREIGN KEY (id_plato) REFERENCES plato(id_plato)
);

-- TABLA FACTURA
CREATE TABLE factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    num_pedido INT UNIQUE NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    iva DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_pago DATETIME DEFAULT NOW(),
    metodo_pago ENUM('efectivo','tarjeta','transferencia') NOT NULL,
    FOREIGN KEY (num_pedido) REFERENCES pedido(num_pedido)
);

-- ============================================
-- DATOS DE PRUEBA
-- ============================================

INSERT INTO usuario (nombre, correo, password_hash, rol) VALUES
('Administrador', 'admin@restaurante.com', '$2b$12$placeholder_hash', 'admin'),
('Carlos Mesero', 'carlos@restaurante.com', '$2b$12$placeholder_hash', 'mesero'),
('María Cajero', 'maria@restaurante.com', '$2b$12$placeholder_hash', 'cajero');

INSERT INTO categoria (nombre, descripcion) VALUES
('Entradas', 'Platos para comenzar'),
('Platos Fuertes', 'Platos principales'),
('Postres', 'Dulces y postres'),
('Bebidas', 'Bebidas frías y calientes');

INSERT INTO mesa (numero, capacidad, estado) VALUES
(1, 4, 'disponible'),(2, 2, 'disponible'),
(3, 6, 'disponible'),(4, 4, 'disponible'),(5, 8, 'disponible');

INSERT INTO empleado (nombre, cargo, telefono) VALUES
('Carlos Ruiz', 'mesero', '3001234567'),
('María López', 'cajero', '3109876543'),
('Pedro García', 'cocinero', '3205551234');

INSERT INTO plato (id_categoria, nombre, descripcion, precio, disponible) VALUES
(1, 'Sopa del día', 'Sopa casera con verduras', 8000, 1),
(2, 'Bandeja Paisa', 'Plato típico colombiano', 25000, 1),
(2, 'Pollo a la Plancha', 'Pollo con ensalada', 18000, 1),
(3, 'Tres Leches', 'Postre casero', 6000, 1),
(4, 'Jugo Natural', 'Jugo de fruta fresca', 4000, 1);

INSERT INTO cliente (nombre, telefono, correo) VALUES
('Ana Torres', '3001111111', 'ana@mail.com'),
('Luis Vera', '3102222222', 'luis@mail.com');
