import json

class Transaction:
    def __init__(self, login_from, login_to, money_amount, description):
        self.login_from = login_from
        self.login_to = login_to
        self.money_amount = money_amount
        self.description = description
    
    def dumps(self):
        return json.dumps({"login_from": self.login_from, "login_to": self.login_to, "money_amount":self.money_amount, "description":self.description})
    
def load(json_bytes):
    data = json.loads(json_bytes)
    return Transaction(data["login_from"], data["login_to"], data["money_amount"], data["description"])