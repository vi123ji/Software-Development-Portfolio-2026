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
            f"- <a href='{url_for('logout')}'>Logout</a></p>"
        )
    else:
        html += (
            f"<p><a href='{url_for('login')}'>Login</a> | "
            f"<a href='{url_for('register')}'>Register</a></p>"
        )

    html += "<h2>Products</h2><ul>"

    for product in products:
        html += f"<li>{product['name']} - £{product['price']:.2f}</li>"

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
                    (username, password)
                )
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


if __name__ == '__main__':
    app.run(debug=True)



