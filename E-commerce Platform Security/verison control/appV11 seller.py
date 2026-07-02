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
    else:
        username = None
        is_admin = 0
        is_seller = 0

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

    # Get product
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        conn.close()
        return "<h1>Product not found</h1><p><a href='" + url_for('home') + "'>Back to home</a></p>"

    # Get reviews
    reviews = conn.execute(
        "SELECT * FROM reviews WHERE product_id = ? ORDER BY id DESC",
        (product_id,)
    ).fetchall()

    # Increment page views
    conn.execute(
        "UPDATE products SET page_views = page_views + 1 WHERE id = ?",
        (product_id,))
    
    conn.commit()
    conn.close()

    # Build HTML
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
            f" | <a href='{url_for('cart')}'>View cart</a></p>")

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
                f"- £{line_total:.2f}</li>")

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
            (item['id'],))
        
    else:
        conn.execute(
            "INSERT INTO cart_items (username, product_id, quantity) VALUES (?, ?, 1)",
            (username, product_id))
        

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

    if not items:
        conn.close()
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Checkout</title></head>
        <body>
            <h1>Checkout</h1>
            <p>Your cart is empty.</p>
            <p><a href='""" + url_for('home') + """'>Back to home</a></p>
        </body>
        </html>
        """
        return html

    # Adjust inventory and record orders
    for item in items:
        new_inventory = item['inventory'] - item['quantity']
        conn.execute(
            "UPDATE products SET inventory = ? WHERE id = ?",
            (new_inventory, item['product_id'])
        )

        # Record purchase in orders
        conn.execute(
            "INSERT INTO orders (username, product_id, quantity) VALUES (?, ?, ?)",
            (username, item['product_id'], item['quantity']))

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
        (product_id, username, comment))
    
    conn.commit()
    conn.close()

    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/admin')
def admin_dashboard():
    user = get_current_user()
    if not user or not user['is_admin']:
        return "<h1>Access denied</h1><p>You have to be an admin to view this page.</p>", 403

    conn = get_db_connection()
    users = conn.execute(
        "SELECT username, is_admin, is_seller FROM users ORDER BY username"
    ).fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Admin area</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('home') + "'>Home</a></p>"
    html += "<h1>Admin dashboard</h1>"
    html += "<h2>All users</h2>"

    if not users:
        html += "<p>No users found.</p>"
    else:
        html += "<ul>"
        for u in users:
            user_link = url_for('admin_view_user', username=u['username'])

            roles = []
            if u['is_admin']:
                roles.append("Admin")
            if u['is_seller']:
                roles.append("Seller")
            if not roles:
                roles.append("User")

            role_text = ", ".join(roles)

            html += (
                f"<li><a href='{user_link}'>{u['username']}</a> "
                f"- {role_text}</li>")

        html += "</ul>"

    html += """
    </body>
    </html>
    """

    return html

@app.route('/admin/user/<username>', methods=['GET', 'POST'])
def admin_view_user(username):
    current = get_current_user()
    if not current or not current['is_admin']:
        return "<h1>Access denied</h1><p>You must be an admin to view this page.</p>", 403

    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'make_seller':
            conn.execute(
                "UPDATE users SET is_seller = 1 WHERE username = ?",
                (username,))

        elif action == 'make_admin':
            # Admins should also have seller privileges
            conn.execute(
                "UPDATE users SET is_admin = 1, is_seller = 1 WHERE username = ?",
                (username,))
            
        elif action == 'demote_user':
            # Remove all extra roles
            conn.execute(
                "UPDATE users SET is_admin = 0, is_seller = 0 WHERE username = ?",
                (username,))

        elif action == 'demote_seller':
            # Demote from admin down to seller only
            conn.execute(
                "UPDATE users SET is_admin = 0, is_seller = 1 WHERE username = ?",
                (username,))

        elif action == 'delete':
            # Deletes user's reviews and cart items and the user
            conn.execute(
                "DELETE FROM reviews WHERE author_name = ?",
                (username,))

            conn.execute(
                "DELETE FROM cart_items WHERE username = ?",
                (username,))
            
            conn.execute(
                "DELETE FROM users WHERE username = ?",
                (username,))
            
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard'))

        conn.commit()


    # After changes, refresh users their reviews
    user_row = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)).fetchone()


    reviews = conn.execute("""
        SELECT reviews.id, reviews.comment, reviews.product_id,
               products.name AS product_name
        FROM reviews
        LEFT JOIN products ON reviews.product_id = products.id
        WHERE reviews.author_name = ?
        ORDER BY reviews.id DESC
    """, (username,)).fetchall()

    conn.close()

    if user_row is None:
        return "<h1>User not found</h1><p><a href='" + url_for('admin_dashboard') + "'>Back to admin</a></p>"

    is_admin = user_row['is_admin']
    is_seller = user_row['is_seller']

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Admin - User details</title></head>
    <body>
    """


    html += "<p><a href='" + url_for('home') + "'>Home</a> | "
    html += "<a href='" + url_for('admin_dashboard') + "'>Back to admin dashboard</a></p>"

    html += f"<h1>User: {user_row['username']}</h1>"

    html += "<h2>Account details</h2>"
    html += "<ul>"
    html += f"<li>Username: {user_row['username']}</li>"
    html += f"<li>Password (stored as plain text): {user_row['password']}</li>"
    html += f"<li>is_admin: {user_row['is_admin']}</li>"
    html += f"<li>is_seller: {user_row['is_seller']}</li>"
    html += "</ul>"


    html += "<h2>Admin actions</h2>"

    # Buttons baised on the user current role
    if not is_admin and not is_seller:
        # Regular user
        html += f"""
            <form method="post">
                <input type="hidden" name="action" value="make_seller">
                <button type="submit">Upgrade to seller</button>
            </form>

            <form method="post">
                <input type="hidden" name="action" value="make_admin">
                <button type="submit">Upgrade to admin</button>
            </form>
        """
    elif not is_admin and is_seller:
        # Seller
        html += f"""
            <form method="post">
                <input type="hidden" name="action" value="demote_user">
                <button type="submit">Demote to user</button>
            </form>

            <form method="post">
                <input type="hidden" name="action" value="make_admin">
                <button type="submit">Upgrade to admin</button>
            </form>
        """
    else:
        # Admin
        html += f"""
            <form method="post">
                <input type="hidden" name="action" value="demote_user">
                <button type="submit">Demote to user</button>
            </form>

            <form method="post">
                <input type="hidden" name="action" value="demote_seller">
                <button type="submit">Demote to seller</button>
            </form>
        """

    # Delete button always available
    html += f"""
        <form method="post" onsubmit="return confirm('Are you sure you want to delete this user and all their reviews and cart items?');">
            <input type="hidden" name="action" value="delete">
            <button type="submit">Delete account (and reviews/cart)</button>
        </form>
    """


    html += "<h2>User's reviews</h2>"

    if not reviews:
        html += "<p>This user has not written any reviews.</p>"
    else:
        html += "<ul>"
        for r in reviews:
            if r['product_name']:
                html += (
                    f"<li>On product <strong>{r['product_name']}</strong>: "
                    f"{r['comment']}</li>")

            else:
                html += f"<li>{r['comment']}</li>"
        html += "</ul>"

    html += """
    </body>
    </html>
    """

    return html




@app.route('/seller')
def seller_dashboard():
    user = get_current_user()
    if not user or not (user['is_seller'] or user['is_admin']):
        return "<h1>Access denied</h1><p>You must be a seller or admin to view this page.</p>", 403

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Seller dashboard</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('home') + "'>Home</a></p>"
    html += f"<h1>Seller dashboard - {user['username']}</h1>"

    html += f"""
        <ul>
            <li><a href="{url_for('seller_list_product')}">List new product</a></li>
            <li><a href="{url_for('seller_products')}">View / manage my products</a></li>
        </ul>
    """

    html += """
    </body>
    </html>
    """
    return html


@app.route('/seller/list', methods=['GET', 'POST'])
def seller_list_product():
    user = get_current_user()
    if not user or not (user['is_seller'] or user['is_admin']):
        return "<h1>Access denied</h1><p>You must be a seller or admin to list products.</p>", 403

    message = ""

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_raw = request.form.get('price', '').strip()
        description = request.form.get('description', '').strip()
        inventory_raw = request.form.get('inventory', '').strip()

        if not name or not price_raw or not description or not inventory_raw:
            message = "Please fill in all fields"
        else:
            try:
                price = float(price_raw)
                inventory = int(inventory_raw)
            except ValueError:
                message = "Price must be a number and inventory must be an integer"
            else:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO products (name, price, description, seller_name, inventory) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, price, description, user['username'], inventory)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('seller_products'))

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>List new product</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('seller_dashboard') + "'>Back to seller dashboard</a></p>"
    html += "<h1>List new product</h1>"

    if message:
        html += f"<p style='color:red;'>{message}</p>"

    html += f"""
        <form method="post">
            <label>Name:</label><br>
            <input type="text" name="name"><br><br>

            <label>Price (£):</label><br>
            <input type="text" name="price"><br><br>

            <label>Description:</label><br>
            <textarea name="description" rows="4" cols="50"></textarea><br><br>

            <label>Inventory:</label><br>
            <input type="text" name="inventory"><br><br>

            <button type="submit">Create product</button>
        </form>
    </body>
    </html>
    """
    return html

@app.route('/seller/products')
def seller_products():
    user = get_current_user()
    if not user or not (user['is_seller'] or user['is_admin']):
        return "<h1>Access denied</h1><p>You must be a seller or admin to view this page.</p>", 403

    conn = get_db_connection()

    if user['is_admin']:
        # Admin can see everything
        products = conn.execute(
            "SELECT * FROM products ORDER BY seller_name, name"
        ).fetchall()
    else:
        products = conn.execute(
            "SELECT * FROM products WHERE seller_name = ? ORDER BY name",
            (user['username'],)
        ).fetchall()

    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>My products</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('seller_dashboard') + "'>Back to seller dashboard</a></p>"
    html += "<h1>My products</h1>"

    if not products:
        html += "<p>You have no products</p>"
    else:
        html += "<ul>"
        for p in products:
            detail_link = url_for('seller_product_detail', product_id=p['id'])
            html += (
                f"<li><a href='{detail_link}'>{p['name']}</a> "
                f"(Inventory: {p['inventory']}, Seller: {p['seller_name']})</li>")
            
        html += "</ul>"

    html += """
    </body>
    </html>
    """
    return html

@app.route('/seller/product/<int:product_id>')
def seller_product_detail(product_id):
    user = get_current_user()
    if not user or not (user['is_seller'] or user['is_admin']):
        return "<h1>Access denied</h1><p>You must be a seller or admin to view this page.</p>", 403

    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return "<h1>Product not found</h1><p><a href='" + url_for('seller_products') + "'>Back to my products</a></p>"


    if (not user['is_admin']) and (product['seller_name'] != user['username']):
        conn.close()
        return "<h1>Access denied</h1><p>Not your product.</p>", 403

    # Total amount sold
    totals = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS total_qty FROM orders WHERE product_id = ?",
        (product_id,)
    ).fetchone()
    total_sold = totals['total_qty']

    # Transaction history
    transactions = conn.execute(
        "SELECT * FROM orders WHERE product_id = ? ORDER BY id DESC",
        (product_id,)
    ).fetchall()

    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Product analytics</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('seller_products') + "'>Back to my products</a></p>"

    html += f"<h1>{product['name']} - Analytics</h1>"

    html += "<h2>Summary</h2>"
    html += "<ul>"
    html += f"<li>Listing page views: {product['page_views']}</li>"
    html += f"<li>Total units sold: {total_sold}</li>"
    html += f"<li>Inventory left: {product['inventory']}</li>"
    html += "</ul>"

    html += "<h2>Transaction history</h2>"

    if not transactions:
        html += "<p>No bought yet.</p>"
    else:
        html += "<table border='1' cellpadding='5' cellspacing='0'>"
        html += "<tr><th>Order ID</th><th>Buyer username</th><th>Quantity</th><th>Date/time</th></tr>"
        for t in transactions:
            html += (
                f"<tr>"
                f"<td>{t['id']}</td>"
                f"<td>{t['username']}</td>"
                f"<td>{t['quantity']}</td>"
                f"<td>{t['created_at']}</td>"
                f"</tr>")
            
        html += "</table>"

    
    edit_link = url_for('seller_edit_product', product_id=product_id)
    public_link = url_for('product_detail', product_id=product_id)

    html += f"""
        <hr>
        <p><a href="{edit_link}">Edit this product</a></p>
        <p><a href="{public_link}" target="_blank">View public product listing</a></p>
    """

    html += """
    </body>
    </html>
    """
    return html

@app.route('/seller/product/<int:product_id>/edit', methods=['GET', 'POST'])
def seller_edit_product(product_id):
    user = get_current_user()
    if not user or not (user['is_seller'] or user['is_admin']):
        return "<h1>Access denied</h1><p>You must be a seller or admin to edit products.</p>", 403

    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return "<h1>Product not found</h1><p><a href='" + url_for('seller_products') + "'>Back to my products</a></p>"

    # Only correct seller or admin
    if (not user['is_admin']) and (product['seller_name'] != user['username']):
        conn.close()
        return "<h1>Access denied</h1><p>You do not own this product.</p>", 403

    message = ""

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_raw = request.form.get('price', '').strip()
        description = request.form.get('description', '').strip()
        inventory_raw = request.form.get('inventory', '').strip()

        if not name or not price_raw or not description or not inventory_raw:
            message = "Please fill in all fields."
        else:
            try:
                price = float(price_raw)
                inventory = int(inventory_raw)
            except ValueError:
                message = "Price must be a number and inventory must be an integer."
            else:
                conn.execute(
                    "UPDATE products SET name = ?, price = ?, description = ?, inventory = ? "
                    "WHERE id = ?",
                    (name, price, description, inventory, product_id))
                
                conn.commit()
                conn.close()
                return redirect(url_for('seller_product_detail', product_id=product_id))

    # If GET or validation error then shows form with existing values
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Edit product</title></head>
    <body>
    """

    html += "<p><a href='" + url_for('seller_product_detail', product_id=product_id) + "'>Back to product analytics</a></p>"
    html += f"<h1>Edit product: {product['name']}</h1>"

    if message:
        html += f"<p style='color:red;'>{message}</p>"

    html += f"""
        <form method="post">
            <label>Name:</label><br>
            <input type="text" name="name" value="{product['name']}"><br><br>

            <label>Price (£):</label><br>
            <input type="text" name="price" value="{product['price']}"><br><br>

            <label>Description:</label><br>
            <textarea name="description" rows="4" cols="50">{product['description']}</textarea><br><br>

            <label>Inventory:</label><br>
            <input type="text" name="inventory" value="{product['inventory']}"><br><br>

            <button type="submit">Save changes</button>
        </form>
    </body>
    </html>
    """
    conn.close()
    return html




if __name__ == '__main__':
    app.run(debug=True)



