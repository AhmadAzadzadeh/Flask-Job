from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from passlib.hash import sha256_crypt

from data import Articles

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

Articles = Articles()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
    return render_template("articles.html", articles = Articles)

@app.route("/article/<string:id>/")
def article(id):
    return render_template("article.html", id = id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', 'Passwords Do Not Match')
    ])   
    confirm = PasswordField('Confirm Password')

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

if __name__ == "__main__":
    app.run(debug=True)
