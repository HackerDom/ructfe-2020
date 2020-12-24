import os

from flask import Flask, abort, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from sqlalchemy.sql.expression import exists

from forms import LoginForm, RegisterForm, SignForm, VerifyForm
from models import db, User, Document
from cryptography import verify_signature


DB_URI = 'sqlite:///data.db'
DOCS_PER_PAGE = 5
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SECRET_KEY'] = '1234'
    login_manager.init_app(app)
    db.init_app(app)
    return app


app = create_app()
# static_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == str(user_id)).first()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect('/profile')

    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if db.session.query(exists().where(User.name == request.form['username'])).scalar():
            form.username.errors.append('This username is taken')
        else:
            user = User(
                name=request.form['username'],
                phone=request.form['phone'],
                address=request.form['address'])
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('.profile'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(name=request.form['username']).first()
        if user is not None and user.privkey == request.form['privkey']:
            login_user(user)
            flash('You were logged in.')
            return redirect(url_for('.profile'))
        else:
            form.privkey.errors.append('Incorrect username or private key')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('.index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/doc/<int:doc_id>')
def doc(doc_id):
    doc = Document.query.get(doc_id)
    if doc is None:
        return abort(404)
    return render_template('doc.html', doc=doc)


@app.route('/')
def recent_docs():
    page = request.args.get('page', 1, type=int)
    docs = Document.query.order_by(Document.id.desc()).paginate(page=page, per_page=DOCS_PER_PAGE)
    return render_template('docs.html', docs=docs)


@app.route('/sign', methods=['GET', 'POST'])
def sign():
    form = SignForm()
    if request.method == 'GET' or not form.validate_on_submit():
        return render_template('sign.html', form=form)

    document = Document(
        author=current_user,
        title=request.form['title'],
        text=request.form['text'])
    db.session.add(document)
    db.session.commit()
    return redirect(url_for('doc', doc_id=document.id))


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    form = VerifyForm()
    error = None
    if request.method == 'POST' and form.validate_on_submit():
        if verify_signature(form.pubkey.data, form.title.data, form.text.data, form.signature.data):
            flash('The signature is valid')
        else:
            error = 'The signature is invalid'
    return render_template('verify.html', form=form, error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=17171)