from flask import Flask, url_for
from flask import render_template, redirect
from forms import LoginForm
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)


from models import User

# Routes

@app.route('/')
def main_page():
    user = {'username': 'Ryan', 'password': '********'}
    title = "User Details"
    return render_template('index.html', user=user, pagetitle=title)

@app.route('/user')
def user_details():
    return render_template("user.html", title="User Details", user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main_page'))
    return render_template('login.html', title='Sign In', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main_page"))

if __name__ == '__main__':
    app.run()
