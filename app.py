from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# from data import Articles

app = Flask(__name__)

app.secret_key = "secret_key123456"
# Config MYSQL
app.config['MYSQL_HOST'] = "*"
app.config['MYSQL_USER'] = "*"
app.config['MYSQL_PASSWORD'] = '*'
app.config['MYSQL_DB'] = 'flaskapp',
app.config['MYSQL_CURSORCLASS'] = '*'

# init MYSQL
mysql = MySQL(app)

# Articles = Articles()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
     # Create Cursor
    cursor = mysql.connection.cursor()
    # Get articles
    result = cursor.execute("SELECT * FROM articles")
    articles = cursor.fetchall()
    if result > 0:
        return render_template("articles.html", articles = articles)
    else:
        msg = "No Article Found"
        return render_template("articles.html", msg = msg)
    # Close connection 
    cursor.close()


@app.route("/article/<string:id>/")
def article(id):
    # Create Cursor
    cursor = mysql.connection.cursor()
    # Get article
    result = cursor.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = cursor.fetchone()
    return render_template("article.html", article = article)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', 'Passwords Do Not Match')
    ])   
    confirm = PasswordField('Confirm Password')

# User Registration
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create a cursor
        cursor = mysql.connection.cursor()
        # Execute query
        cursor.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        # Commit to DB
        mysql.connection.commit()
        # close connection
        cursor.close()
        flash("You Are Now Registered", 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form = form)

# User Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password_candidate = request.form['password']
        # Create cursor
        cursor = mysql.connection.cursor()
        # Get user by username
        result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            # Get stored hash
            data = cursor.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                session["logged_in"] = True
                session["username"] = username
                flash("Your Are Logged In", 'success')
                return redirect(url_for("dashboard"))
            else:
                error = "InCorrect Password"
                return render_template("login.html", error = error)
            # close connection
            cursor.close()
        else:
            error = "Username Not Found"
            return render_template("login.html", error = error)
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap()

# Logout
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You Are Logged Out", "success")
    return redirect(url_for("login"))


# Dahboard
@app.route("/dashboard")
@is_logged_in
def dashboard():
    # Create Cursor
    cursor = mysql.connection.cursor()
    # Get articles
    result = cursor.execute("SELECT * FROM articles")
    articles = cursor.fetchall()
    if result > 0:
        return render_template("dashboard.html", articles = articles)
    else:
        msg = "No Article Found"
        return render_template("dashboard.html", msg = msg)
    # Close connection 
    cursor.close()

# Article Form class
class ArticleForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField("Body", [validators.Length(min=30)])

@app.route("/add_article", methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        # Create Cursor
        cursor = mysql.connection.cursor()
        # Execute
        cursor.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        # Commit to DB
        mysql.connection.commit()
        # Close Connection
        cursor.close()
        flash("Article Created", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_article.html", form = form)

if __name__ == "__main__":
    app.run(debug=True)
