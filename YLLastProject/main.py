from flask import Flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from flask import render_template, redirect, make_response
from flask import session
from data import Posts, User
from forms.user import RegisterForm
from forms.add_note import AddNoteForm
from forms.login import LoginForm
import posts_resources

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

api.add_resource(posts_resources.NotesListResource, '/api/v2/notes')

api.add_resource(posts_resources.NotesResource, '/api/v2/notes/<int:notes_id>')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    form = AddNoteForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        note = Posts(
            content=form.text.data,
            user_id=current_user.id,
        )
        db_sess.add(note)
        db_sess.commit()
        return redirect('/')
    notes = db_sess.query(Posts)
    return render_template("index.html", notes=notes, form=form, title="Стена")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init("db/posts.db")
    app.run(port=8000, debug=True)


if __name__ == '__main__':
    main()
