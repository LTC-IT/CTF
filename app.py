from flask import Flask, url_for, Markup
from flask import render_template, redirect, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy import text


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'


from models import User, CTFSubSystems
from forms import LoginForm, RegistrationForm, CTFSubsystemForm

# Routes

@app.route('/')
def main_page():
    user = {'username': 'Ryan', 'password': '********'}
    title = "Home"
    return render_template('index.html', user=user, pagetitle=title)


@app.route('/user')
@login_required
def user_details():
    return render_template("user.html", pagetitle="User Details", user=current_user)


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
    return render_template('login.html', pagetitle='Sign In', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main_page"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for('login'))
    return render_template('register.html', pagetitle='Register', form=form)


@app.route('/registersubsystem', methods=['GET', 'POST'])
def registerCTFSubsystem():
    form = CTFSubsystemForm()
    if form.validate_on_submit():
        newSubSystem = CTFSubSystems(title=form.title.data, description=form.description.data, score=form.score.data, Owner="None")
        db.session.add(newSubSystem)
        db.session.commit()
        flash('Congratulations, you have registered a new CTF Subsystem!')
        return redirect(url_for('login'))
    return render_template('registersubsystem.html', pagetitle='Register Sub System', form=form)


@app.route("/report/showallsubsystems")
def showallsubsystems():
    subsystems = text('select title, description from ctf_sub_systems')
    result = db.engine.execute(subsystems)
    html_output = Markup("<table class='table'><thead><tr><th>Subsystem name</th><th>Description</th></tr></thead><tbody>")
    for record in result:
        subsystem_name = record[0]
        subsystem_description = record[1]
        html_output = Markup("{}<tr><td>{}:</td><td>{}</td></tr>".format(html_output, subsystem_name, subsystem_description))
    html_output = Markup("{}</tbody></table>".format(html_output))
    return render_template('report.html', pagetitle='Subsystem Details', data=html_output)


if __name__ == '__main__':
    app.run()
