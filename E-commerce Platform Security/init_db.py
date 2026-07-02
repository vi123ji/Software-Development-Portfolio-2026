# Creates database.db using schema.sql and inserts example data
import sqlite3
from werkzeug.security import generate_password_hash


# Creates / connects the database file
connection = sqlite3.connect('database.db')

# Reads and executes the schema
with open('schema.sql', 'r') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Example data (sold by admin)
cur.execute(
    "INSERT INTO products (name, price, description, seller_name, inventory) "
    "VALUES (?, ?, ?, ?, ?)",
    ('Rolex Datejust', 10000.99, 'Gold, Fluted bezel, 41mm', 'admin', 5))

cur.execute(
    "INSERT INTO products (name, price, description, seller_name, inventory) "
    "VALUES (?, ?, ?, ?, ?)",
    ('Rolex Daytona', 20000.99, 'Rose gold, Cosmograph, 40mm', 'admin', 3))


# Admin user
cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 1, 1)",
    ("admin", generate_password_hash('password'))
)

# Normal users
cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 0)",
    ("user1", generate_password_hash('password'))
)

cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 0)",
    ("user2", generate_password_hash('password'))
)

# Sellers
cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 1)",
    ("seller1", generate_password_hash('password'))
)

cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 1)",
    ("seller2", generate_password_hash('password'))
)

connection.commit()
connection.close()

print("database.db initialised")
