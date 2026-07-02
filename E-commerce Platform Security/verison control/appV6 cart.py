from flask import Flask, request, redirect, url_for, make_response
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev-secret-key'  # used later to add sessions/flash


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # access columns by name 
    return conn


@app.route('/')
def home():
    
    username = request.cookies.get('username') # check if user is logged in (cookie) 
 
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()


    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Amazing Bargain Central</title>
    </head>
    <body>
        <h1>Welcome to Amazing Bargain Central</h1>
    """

    # Shows logged in status
    if username:
        html += (
            f"<p>Logged in as <strong>{username}</strong> "
            f"- <a href='{url_for('logout')}'>Logout</a>"
            f" | <a href='{url_for('cart')}'>View cart</a></p>")

    else:
        html += (
            f"<p><a href='{url_for('login')}'>Login</a> | "
            f"<a href='{url_for('register')}'>Register</a></p>")

    html += (
        "<p><a href='" + url_for('search') + "'>Search for product</a></p>"
        "<h2>Products</h2><ul>")


    for product in products:
        product_link = url_for('product_detail', product_id=product['id'])
        html += (
            f"<li>"
            f"<a href='{product_link}'>{product['name']}</a>"
            f" - £{product['price']:.2f}"
            f"</li>")
        

    html += """
        </ul>
    </body>
    </html>
    """

    return html


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            message = "Please enter a username and password."
        else:
            conn = get_db_connection()
            try:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password))
                
                conn.commit()
                conn.close()
                
                return redirect(url_for('login')) # send user to login page after successful registration
            except sqlite3.IntegrityError:
                conn.close()
                message = "Username is already taken."

    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Register</h1>
    """

    if message:
        html += f"<p style='color:red;'>{message}</p>"

    html += f"""
        <form method="post">
            <label>Username:</label><br>
            <input type="text" name="username"><br><br>

            <label>Password:</label><br>
            <input type="password" name="password"><br><br>

            <button type="submit">Register</button>
        </form>
        <p><a href="{url_for('home')}">Back to home</a></p>
    </body>
    </html>
    """

    return html


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            # Login success: set cookie and go home
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('username', username)
            return resp
        else:
            message = "Invalid username or password."

    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Login</h1>
    """

    if message:
        html += f"<p style='color:red;'>{message}</p>"

    html += f"""
        <form method="post">
            <label>Username:</label><br>
            <input type="text" name="username"><br><br>

            <label>Password:</label><br>
            <input type="password" name="password"><br><br>

            <button type="submit">Login</button>
        </form>
        <p><a href="{url_for('home')}">Back to home</a></p>
    </body>
    </html>
    """

    return html


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.delete_cookie('username')
    return resp

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    username = request.cookies.get('username')

    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()
    conn.close()

    if product is None:
        return "<h1>Product not found</h1><p><a href='" + url_for('home') + "'>Back to home</a></p>"

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Product Details</title>
    </head>
    <body>
    """

    # Top bar (back to home)
    html += "<p><a href='" + url_for('home') + "'>Home</a></p>"

    if username:
        html += (
            f"<p>Logged in as <strong>{username}</strong> "
            f"- <a href='{url_for('logout')}'>Logout</a></p>"
        )
    else:
        html += (
            f"<p><a href='{url_for('login')}'>Login</a> | "
            f"<a href='{url_for('register')}'>Register</a></p>")


    # Product details
    html += f"""
        <h1>{product['name']}</h1>
        <p><strong>Price:</strong> £{product['price']:.2f}</p>
        <p><strong>Description:</strong> {product['description']}</p>
        <p><strong>Seller:</strong> {product['seller_name']}</p>
        <p><strong>Inventory:</strong> {product['inventory']}</p>
    """

    # Add to Cart
    if username:
        html += f"""
            <form method="post" action="{url_for('add_to_cart', product_id=product_id)}">
                <button type="submit">Add to Cart</button>
            </form>
            <p><a href="{url_for('cart')}">View cart</a></p>
        """
    else:
        html += "<p><em>You have to log in to add to  cart.</em></p>"

    # Finish later for future reviews
    html += """
        <hr>
        <p><em>Reviews will go here.</em></p>
    </body>
    </html>
    """

    return html


@app.route('/search', methods=['GET', 'POST'])
def search():
    username = request.cookies.get('username')
    results = []
    query = ""

    if request.method == 'POST':
        query = request.form.get('query', '').strip()

        if query:
            conn = get_db_connection()
            results = conn.execute(
                "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{query}%",)
            ).fetchall()
            conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Search</title></head>
    <body>
    """

    # Top bar
    html += "<p><a href='" + url_for('home') + "'>Home</a></p>"

    if username:
        html += (
            f"<p>Logged in as <strong>{username}</strong> "
            f"- <a href='{url_for('logout')}'>Logout</a></p>")
        
    else:
        html += (
            f"<p><a href='{url_for('login')}'>Login</a> | "
            f"<a href='{url_for('register')}'>Register</a></p>")
        

    html += f"""
        <h1>Search Products</h1>
        <form method="post">
            <input type="text" name="query" value="{query}" placeholder="Search for product...">
            <button type="submit">Search</button>
        </form>
        <hr>
    """

    # Display results if any
    if query and not results:
        html += "<p>No products found.</p>"

    if results:
        html += "<ul>"
        for product in results:
            product_link = url_for('product_detail', product_id=product['id'])
            html += (
                f"<li>"
                f"<a href='{product_link}'>{product['name']}</a>"
                f" - £{product['price']:.2f}"
                f"</li>")
            
        html += "</ul>"

    html += """
    </body>
    </html>
    """

    return html

@app.route('/cart')
def cart():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_connection()
    items = conn.execute("""
        SELECT cart_items.id, cart_items.quantity, products.name, products.price
        FROM cart_items
        JOIN products ON cart_items.product_id = products.id
        WHERE cart_items.username = ?
    """, (username,)).fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Your Cart</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('home') + "'>Home</a></p>"

    html += f"<h1>Cart</h1>"

    if not items:
        html += "<p>Cart is empty.</p>"
    else:
        total = 0
        html += "<ul>"
        for item in items:
            line_total = item['price'] * item['quantity']
            total += line_total
            html += (
                f"<li>{item['name']} - Qty: {item['quantity']} "
                f"- £{line_total:.2f}</li>"
            )
        html += "</ul>"
        html += f"<h3>Total: £{total:.2f}</h3>"

        html += f"""
            <form method="post" action="{url_for('checkout')}">
                <button type="submit">Checkout</button>
            </form>

            <form method="post" action="{url_for('clear_cart')}">
                <button type="submit">Clear Cart</button>
            </form>
        """


    html += """
    </body>
    </html>
    """

    return html

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Checks if item already in cart
    item = conn.execute(
        "SELECT * FROM cart_items WHERE username = ? AND product_id = ?",
        (username, product_id)
    ).fetchone()

    if item:
        conn.execute(
            "UPDATE cart_items SET quantity = quantity + 1 WHERE id = ?",
            (item['id'],)
        )
    else:
        conn.execute(
            "INSERT INTO cart_items (username, product_id, quantity) VALUES (?, ?, 1)",
            (username, product_id)
        )

    conn.commit()
    conn.close()

    return redirect(url_for('cart'))


@app.route('/checkout', methods=['POST'])
def checkout():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_connection()

    items = conn.execute("""
        SELECT cart_items.product_id, cart_items.quantity, products.inventory
        FROM cart_items
        JOIN products ON cart_items.product_id = products.id
        WHERE cart_items.username = ?
    """, (username,)).fetchall()

    # Adjust inventory for each product
    for item in items:
        new_inventory = item['inventory'] - item['quantity']
        conn.execute(
            "UPDATE products SET inventory = ? WHERE id = ?",
            (new_inventory, item['product_id'])
        )

    # Clear cart
    conn.execute("DELETE FROM cart_items WHERE username = ?", (username,))

    conn.commit()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Checkout complete</title></head>
    <body>
        <h1>Checkout complete</h1>
        <p>Order has been placed.</p>
        <p><a href='""" + url_for('home') + """'>Back to home</a></p>
    </body>
    </html>
    """
    return html

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM cart_items WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    return redirect(url_for('cart'))



if __name__ == '__main__':
    app.run(debug=True)



