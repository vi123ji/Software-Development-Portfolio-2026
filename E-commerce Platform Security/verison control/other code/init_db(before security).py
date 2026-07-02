# Creates database.db using schema.sql and inserts example data
import sqlite3


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

# Creates admin user
cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES ('admin', 'password', 1, 1)")


# Extra users and sellers for testing 
# Normal users
cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 0)",
    ("user1", "password")
)

cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 0)",
    ("user2", "password")
)

# Sellers
cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 1)",
    ("seller1", "password")
)

cur.execute(
    "INSERT INTO users (username, password, is_admin, is_seller) "
    "VALUES (?, ?, 0, 1)",
    ("seller2", "password")
)



connection.commit()
connection.close()

print("database.db initialised")
