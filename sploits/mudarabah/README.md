## VULN 1
[Crypter](../../services/mudarabah/service/cipher/crypter.py) class is McEliece cryptosystem on LDPC.

All flags in transactions on each request are encrypted with same public key. That means that same ct-vector is xored with different error-vector. So U can use this Multiple Encryption attack to found some places of errors to reduce index-space for [ISD attack](https://crypto.stackexchange.com/a/22779). 

[sploit](./sploit1.py)

To fix this U can store encrypted flags or just freeze error-vector in encryption function.

## VULN 2
`/check_card` method uses `LIKE` in query. So U can send `{"login": login, "credit_card_credentials":"%"}` or `{"login": login, "credit_card_credentials":"<32 underscores>"}` and steal user's flag.

[sploit](./sploit2.py)

Checksystem tries to check flag using `[A-Z0-9]{5}_{22}[A-Z0-9]{4}=` in `get` and `[a-zA-Z0-9]{32}` in `check`. To fix vuln U can validate queries before execute.
