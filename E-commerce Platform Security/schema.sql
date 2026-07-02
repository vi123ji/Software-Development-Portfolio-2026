-- schema.sql
-- Drop tables if they exist 
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    is_admin    INTEGER NOT NULL DEFAULT 0,
    is_seller   INTEGER NOT NULL DEFAULT 0,
    is_suspended INTEGER NOT NULL DEFAULT 0);

-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    price       REAL NOT NULL,
    description TEXT NOT NULL,
    seller_name TEXT NOT NULL,
    inventory   INTEGER NOT NULL DEFAULT 10,
    page_views INTEGER NOT NULL DEFAULT 0);

-- Reviews table
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    comment     TEXT NOT NULL,
    image_url   TEXT);

-- Cart items table
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
