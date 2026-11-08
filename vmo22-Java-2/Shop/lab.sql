-- Создаем базу данных
CREATE DATABASE inventory_db;

-- Подключаемся к базе данных
\c inventory_db

-- Создаем таблицу категорий
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Создаем таблицу производителей
CREATE TABLE manufacturer (
    manufacturer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    website VARCHAR(100)
);

-- Создаем таблицу товаров
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INTEGER REFERENCES category(category_id),
    manufacturer_id INTEGER REFERENCES manufacturer(manufacturer_id)
);

-- Создаем таблицу склада
CREATE TABLE warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES product(product_id),
    quantity INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставляем тестовые данные
INSERT INTO category (name, description) VALUES 
('Комплектующие ПК', 'Компоненты для сборки компьютера'),
('Сетевое оборудование', 'Оборудование для построения сетей'),
('Компьютерная периферия', 'Дополнительные устройства для компьютера');

INSERT INTO manufacturer (name, country, website) VALUES 
('ASUS', 'Тайвань', 'https://www.asus.com'),
('Intel', 'США', 'https://www.intel.com'),
('Logitech', 'Швейцария', 'https://www.logitech.com');

INSERT INTO product (name, description, price, category_id, manufacturer_id) VALUES 
('Материнская плата ASUS Prime', 'ATX материнская плата для Intel', 12000, 1, 1),
('Процессор Intel Core i7', 'Процессор 11 поколения', 25000, 1, 2),
('Беспроводная мышь Logitech', 'Мышь с Bluetooth подключением', 3500, 3, 3);

INSERT INTO warehouse (product_id, quantity) VALUES 
(1, 15),
(2, 8),
(3, 25);
