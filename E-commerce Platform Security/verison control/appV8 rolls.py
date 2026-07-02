from flask import Flask, request, redirect, url_for, make_response
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev-secret-key'  # used later to add sessions/flash


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # access columns by name 
    return conn


def get_current_user(): # Returns  logged in user row from the database, or None
    username = request.cookies.get('username')
    if not username:
        return None

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    return user



@app.route('/')
def home():
    user = get_current_user() # Get user info if logged in
    if user:
        username = user['username']
        is_admin = user['is_admin']
        is_seller = user['is_seller']
        is_suspended = user['is_suspended']
    else:
        username = None
        is_admin = 0
        is_seller = 0
        is_suspended = 0

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

    # Shows logged in status and role info
    if username:
        roles = []
        if is_admin:
            roles.append("Admin")
        if is_seller:
            roles.append("Seller")
        if not roles:
            roles.append("User")  # default role 

        role_text = ", ".join(roles)

        html += (
            f"<p>Logged in as <strong>{username}</strong> "
            f"({role_text}) "
            f"- <a href='{url_for('logout')}'>Logout</a>"
            f" | <a href='{url_for('cart')}'>View cart</a>")

        if is_admin:
            html += f" | <a href='{url_for('admin_dashboard')}'>Admin area</a>"
        if is_seller:
            html += f" | <a href='{url_for('seller_dashboard')}'>Seller area</a>"

        html += "</p>"
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

    reviews = conn.execute(
        "SELECT * FROM reviews WHERE product_id = ? ORDER BY id DESC",
        (product_id,)
    ).fetchall()

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
            f"- <a href='{url_for('logout')}'>Logout</a>"
            f" | <a href='{url_for('cart')}'>View cart</a></p>"
        )
    else:
        html += (
            f"<p><a href='{url_for('login')}'>Login</a> | "
            f"<a href='{url_for('register')}'>Register</a></p>"
        )

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
            <p><a href="{url_for('cart')}">View your cart</a></p>
        """
    else:
        html += "<p><em>Log in to add this item to your cart.</em></p>"

    # Reviews section
    html += """
        <hr>
        <h2>Reviews</h2>
    """

    # Show existing reviews
    if reviews:
        html += "<ul>"
        for review in reviews:
            html += (
                f"<li><strong>{review['author_name']}</strong>: "
                f"{review['comment']}</li>"
            )
        html += "</ul>"
    else:
        html += "<p>No reviews yet.</p>"

    # Review form
    if username:
        html += f"""
            <h3>Leave a review</h3>
            <form method="post" action="{url_for('add_review', product_id=product_id)}">
                <textarea name="comment" rows="4" cols="50"
                          placeholder="Write your review here..."></textarea><br><br>
                <button type="submit">Submit review</button>
            </form>
        """
    else:
        html += "<p><em>Log in to write a review.</em></p>"

    html += """
    </body>
    </html>
    """

    return html



'''
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    username = request.cookies.get('username')

    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    reviews = conn.execute(
        "SELECT * FROM reviews WHERE product_id = ? ORDER BY id DESC",
        (product_id,)
    ).fetchall()

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
        <hr>
        <h2>Reviews</h2>
    """

    # Shows reviews
    if reviews:
        html += "<ul>"
        for review in reviews:
            html += (
                f"<li><strong>{review['author_name']}</strong>: "
                f"{review['comment']}</li>"
            )
        html += "</ul>"
    else:
        html += "<p>No reviews yet.</p>"

    # Allows logged in users to leave a review
    if username:
        html += f"""
            <h3>Leave a review</h3>
            <form method="post" action="{url_for('add_review', product_id=product_id)}">
                <textarea name="comment" rows="4" cols="50"
                          placeholder="Write your review here..."></textarea><br><br>
                <button type="submit">Submit review</button>
            </form>
        """
    else:
        html += "<p><em>Log in to write a review.</em></p>"

    html += """
    </body>
    </html>
    """

    return html
'''


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

@app.route('/product/<int:product_id>/add_review', methods=['POST'])
def add_review(product_id):
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))

    comment = request.form.get('comment', '').strip()

    if not comment:
        # If no comment was entered then goes back to product page
        return redirect(url_for('product_detail', product_id=product_id))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO reviews (product_id, author_name, comment) VALUES (?, ?, ?)",
        (product_id, username, comment)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/admin')
def admin_dashboard():
    user = get_current_user()
    if not user or not user['is_admin']:
        return "<h1>Access denied</h1><p>You must be an admin to view this page.</p>", 403

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Admin area</title></head>
    <body>
        <p><a href='""" + url_for('home') + """'>Home</a></p>
        <h1>Admin dashboard</h1>
        <p>This is a placeholder for admin features (manage users, suspend accounts, etc.).</p>
    </body>
    </html>
    """
    return html


@app.route('/seller')
def seller_dashboard():
    user = get_current_user()
    if not user or not user['is_seller']:
        return "<h1>Access denied</h1><p>You must be a seller to view this page.</p>", 403

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Seller area</title></head>
    <body>
        <p><a href='""" + url_for('home') + """'>Home</a></p>
        <h1>Seller dashboard</h1>
        <p>This is a placeholder for seller features (add/edit products, manage inventory, etc.).</p>
    </body>
    </html>
    """
    return html



if __name__ == '__main__':
    app.run(debug=True)



