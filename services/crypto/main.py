import json
from flask import Flask, request, redirect, url_for, render_template, session, jsonify
import helpers.user_model as user_model
import helpers.transaction_model as transaction_model
import helpers.database_controller as database_controller
import helpers.exceptions as e
import helpers.decorators as d

app = Flask(__name__)
app.secret_key = "useless_key"

@app.before_first_request
def before_request():
    database_controller.connect_to_db()


@app.route('/send_money', methods=['GET', 'POST'])
@d.need_args("token", "to", "amount", "description")
def send_money(token=None, to=None, login_from=None, description=None, amount=None):
    if request.method == 'POST':
        with database_controller.DatabaseClient() as db:
            login_from = db.select_user_by_cookie(token).login
        transaction = transaction_model.Transaction(login_from, to, amount, description)
        with database_controller.DatabaseClient() as db:
            db.send_money(transaction)
        return redirect(url_for('get_transactions'))
    return render_template("send_money.html")


@app.route('/get_token', methods=['POST'])
@d.need_args("login", "password")
def login(login=None, password=None):
    print("login_post")
    print(f"log {login}, pass {password}", flush=True)
    with database_controller.DatabaseClient() as db:
        print(f"all users {db.get_all_users()}")
        user = db.select_user_by_login_and_pass(login, password)
        print(f"login {user}", flush=True)
        if not user:
            return "Incorrect username or password"
    return jsonify({"status": 200, "result": True, "addition": {"token":str(user.cookie)}})

@app.route('/get_user', methods=['POST'])
@d.need_args("token")
def get_user(token=None):
    print("get user by token")
    with database_controller.DatabaseClient() as db:
        print(f"all users {db.get_all_users()}")
        user = db.select_user_by_cookie(token)
        print(f"get {user}", flush=True)
        if not user:
            return "Incorrect username or password"
    return jsonify({"status": 200, 
                    "result": True, "addition": {
                        "login":user.login, "password_hash":user.password_hash, 
                        "credit_card_credentials":user.credit_card_credentials, 
                        "public_key_base64": user.public_key_base64}
                        }
                    )

@app.route('/register', methods=['POST'])
@d.need_args("login", "password", "credit_card_credentials", "public_key_base64")
def register(login=None, password=None, credit_card_credentials=None, public_key_base64=None):
    print("reg_post")
    print(f"reg {login}, pass {password}, credit_card {credit_card_credentials} pubkey {public_key_base64}")
    with database_controller.DatabaseClient() as db:
        if db.check_if_username_free(login):
            user = user_model.create_new(login, password, public_key_base64, credit_card_credentials)
            print(f"will add user {user}", flush=True)
            db.add_user(user)
        else:
            return "this user already exists"
    return jsonify({"status": 200, "result": True, "addition": {"token":str(user.cookie)}})


@app.route('/transactions')
def get_transactions():
    with database_controller.DatabaseClient() as db:
        return jsonify({"status": 200, "result": True, "addition": db.get_all_transactions()})

@app.route('/users_pubkeys')
def get_users():
    with database_controller.DatabaseClient() as db:
        return jsonify({"status": 200, "result": True, "addition": 
        [
            {x[1]:x[3]} for x in db.get_all_users_all_info() #depends on fields order in select *
        ]})

@app.route('/users_all_info') #debug only
def _get_users():
    with database_controller.DatabaseClient() as db:
        return jsonify({"status": 200, "result": True, "addition": db.get_all_users_all_info()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3113, debug=True)