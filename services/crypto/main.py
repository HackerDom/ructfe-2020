from flask import Flask, request, redirect, url_for, render_template, session
import user_model
import transaction_model
import database_controller

app = Flask(__name__)
app.secret_key = "useless_key"

@app.before_first_request
def before_request():
    database_controller.connect_to_db()

def check_auth():
    try:
        cookie = session["user"]
        print(f"cookie is {cookie}")
        with database_controller.DatabaseClient() as db:
            user = db.select_user_by_cookie(cookie)
            if not user:
                return False
            return True
    except KeyError:
        return False

@app.route('/send_money', methods=['GET', 'POST'])
def send_money():
    if not check_auth():
        return redirect(url_for('login'))
    if request.method == 'POST':
        cookie = session["user"]
        with database_controller.DatabaseClient() as db:
            login_from = db.select_user_by_cookie(cookie).login
        login_to = int(request.form['to'])
        amount = int(request.form['amount'])
        description = request.form['description']
        transaction = transaction_model.Transaction(login_from, login_to, amount, description)
        with database_controller.DatabaseClient() as db:
            db.add_transaction(transaction)
        return redirect(url_for('get_transactions'))
    return render_template("send_money.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("login_post1")
        login = request.form['login']
        password = request.form['password']
        print(f"log {login}, pass {password}", flush=True)
        with database_controller.DatabaseClient() as db:
            print(f"all users {db.get_all_users()}")
            print_all_users()
            user = db.select_user_by_login_and_pass(login, password)
            print(f"login {user}", flush=True)
            if not user:
                return "Incorrect username or password"
        session['user'] = user.cookie
        return "you have logined"
    print("login_get")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("reg_post")
        login = request.form['login']
        password = request.form['password']
        credit_card_credentials = request.form['credit_card_credentials']
        public_key_base64 = request.form['public_key_base64']
        print(f"reg {login}, pass {password}, credit_card {credit_card_credentials} pubkey {public_key_base64}")
        with database_controller.DatabaseClient() as db:
            if db.check_if_username_free(login):
                user = user_model.create_new(login, password, public_key_base64, credit_card_credentials)
                print(f"will add user {user}", flush=True)
                db.add_user(user)
                session['user'] = user.cookie
            else:
                return "this user already exists"
        return redirect(url_for('send_money'))

    return render_template('register.html')


@app.route('/transactions/')
def get_transactions():
    with database_controller.DatabaseClient() as db:
        return '\n'.join([str(x) for x in db.get_all_transactions()])

@app.route('/users/')
def get_users():
    print_all_users()
    with database_controller.DatabaseClient() as db:
        return '\n'.join([str(x) for x in db.get_all_users()])

def print_all_users():
    with database_controller.DatabaseClient() as db:
        print('\n'.join([str(x) for x in db.get_all_users_all_info()]), flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3113, debug=True)