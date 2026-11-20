 
from flask import Flask, request, redirect, session, render_template_string
from database import create_table, register_user, verify_user
import re
import os

app = Flask(__name__)

# Secret key for session security
app.secret_key = os.environ.get(
    "SECRET_KEY",
    os.urandom(32)
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

# Create database table
create_table()


# Common HTML design
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Login System</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #141e30, #243b55);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }

        .container {
            background: white;
            color: #222;
            padding: 35px;
            border-radius: 18px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 30px #0005;
        }

        h2 {
            text-align: center;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 13px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 15px;
        }

        button {
            width: 100%;
            padding: 13px;
            background: #1769ff;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }

        button:hover {
            background: #004dcc;
        }

        a {
            color: #1769ff;
        }

        .message {
            text-align: center;
            color: #d22;
            margin: 12px 0;
        }

        .success {
            color: green;
        }

        .footer {
            text-align: center;
            margin-top: 20px;
        }

        .welcome {
            text-align: center;
        }
    </style>
</head>

<body>

<div class="container">

    {% if page == "register" %}

        <h2>Create Account 🔐</h2>

        {% if message %}
            <p class="message">{{ message }}</p>
        {% endif %}

        <form method="POST">

            <input
                type="text"
                name="username"
                placeholder="Username"
                maxlength="50"
                required
            >

            <input
                type="email"
                name="email"
                placeholder="Email"
                maxlength="254"
                required
            >

            <input
                type="password"
                name="password"
                placeholder="Password (8+ characters)"
                required
            >

            <button type="submit">Create Account</button>

        </form>

        <p class="footer">
            Already registered?
            <a href="/login">Login</a>
        </p>


    {% elif page == "login" %}

        <h2>Secure Login 🔐</h2>

        {% if message %}
            <p class="message">{{ message }}</p>
        {% endif %}

        <form method="POST">

            <input
                type="email"
                name="email"
                placeholder="Email"
                required
            >

            <input
                type="password"
                name="password"
                placeholder="Password"
                required
            >

            <button type="submit">Login</button>

        </form>

        <p class="footer">
            New user?
            <a href="/register">Create account</a>
        </p>


    {% elif page == "home" %}

        <div class="welcome">

            <h2>Welcome! 🎉</h2>

            <h3>Hello, {{ username }}!</h3>

            <p>You are securely logged in.</p>

            <p>Your account is active.</p>

            <a href="/logout">
                <button>Logout</button>
            </a>

        </div>

    {% endif %}

</div>

</body>
</html>
"""


# Home page
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    return render_template_string(
        HTML,
        page="home",
        username=session.get("username", "User"),
        message=""
    )


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if not username or len(username) > 50:

            message = "Enter a valid username (maximum 50 characters)."

        elif len(email) > 254 or not re.fullmatch(
            r"[^\s@]+@[^\s@]+\.[^\s@]+",
            email
        ):

            message = "Enter a valid email address."

        elif (
            len(password) < 8
            or len(password.encode("utf-8")) > 72
        ):

            message = "Password must be at least 8 characters and at most 72 bytes."

        else:

            success = register_user(
                username,
                email,
                password
            )

            if success:

                return redirect("/login")

            else:

                message = "Username or email already exists."

    return render_template_string(
        HTML,
        page="register",
        message=message
    )


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        user = verify_user(
            email,
            password
        )

        if user:

            session.clear()

            session["user_id"] = user[0]

            session["username"] = user[1]

            return redirect("/")

        else:

            message = "Invalid email or password."

    return render_template_string(
        HTML,
        page="login",
        message=message
    )


# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# Run application
if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
