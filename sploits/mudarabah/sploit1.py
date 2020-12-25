import sys
import numpy as np
from base64 import b85decode

from cipher.utils import gauss_jordan, bytes_to_codeword, load, codeword_to_bytes
from api import Api

K = 5

def information_set_decoding(encrypted, public_key, epochs, wrong_indexes):
    t = 10
    k, n = public_key.shape
    arr = np.array([x for x in np.arange(n) if x not in wrong_indexes])
    wt = -1
    step = 0

    E = np.eye(k, dtype=int)
    while wt < t and step <= epochs:
        np.random.shuffle(arr)
        J = arr[:k]
        G = public_key[:, J]
        I, G_inv = gauss_jordan(G, True)
        if not (I == E).all():
            continue
        wt = np.sum((encrypted + encrypted[J] @ G_inv @ public_key) % 2)
        step += 1
        
    return (encrypted[J] @ G_inv) % 2
    
def load_public(data):
    return load(data[2:])

def crack(transactions, pub_key):
    pub_key = load_public(b85decode(pub_key.encode()))
    word_size = pub_key.shape[1]
    main_transaction = {
        (x['amount'], x['login_from'], x['login_to']): bytes_to_codeword(bytes.fromhex(x['description']), word_size) 
        for x in transactions[0]
    }
    indexes = {k:list(v) for k,v in main_transaction.items()}

    for tr in transactions[1:]:
        for x in tr:
            key = x['amount'], x['login_from'], x['login_to']
            descr = bytes_to_codeword(bytes.fromhex(x['description']), word_size)
            for i,x in enumerate(descr):
                indexes[key][i] += x

    for k, ind in indexes.items():
        res = [1 if x/K > 0.5 else 0 for x in ind]
        tr = main_transaction[k]
        wrong_indexes = {i for i, (x,y) in enumerate(zip(res, tr)) if x!=y}
        res = information_set_decoding(tr, pub_key, 10, wrong_indexes)
        if res is not None:
            print(codeword_to_bytes(res))

def list_users(api):
    res = api.list_users()
    if res is None: return []
    if 'addition' not in res or 'users' not in res['addition']: return []
    return res['addition']['users']

def get_user_pub_key(api, login):
    result = api.get_user(login)
    if result is None: return None
    if "addition" not in result or "pub_key" not in result["addition"]: return None
    return result["addition"]["pub_key"]

def get_transactions(api, login):
    result = api.get_transacions(login)
    if result is None: return None
    if "addition" not in result or "transactions" not in result["addition"]: return None
    return result["addition"]["transactions"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need host")
        exit()
    api = Api(sys.argv[1])
    users = list_users(api)

    for user in users:
        transaction = get_transactions(api, user)
        if transaction:
            transactions = [transaction]
            for _ in range(K):
                transactions.append(get_transactions(api, user))
            pub_key = get_user_pub_key(api, user)
            print(f'Trying to hack {user}')
            crack(transactions, pub_key)