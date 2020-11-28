class Transaction:
    def __init__(self, login_from, login_to, money_amount, description=""):
        self.login_from = login_from
        self.login_to = login_to
        self.money_amount = money_amount
        self.description = description