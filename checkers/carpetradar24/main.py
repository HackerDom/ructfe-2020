import string
from gornilo import CheckRequest, PutRequest, GetRequest
import client as c
import checker
import random


def get_random_string(k=10):
    return ''.join(random.choices(string.ascii_lowercase, k=k))


code = {
    101: "OK",
    102: "CORRUPT",
    103: "MUMBLE",
    104: "DOWN",
    110: "CHECKER_ERROR"
}

# python checker.py test localhost
# python checker.py check localhost
# python checker.py put localhost aaaa:aaaa aaaaaaaabbbbbbbbaaaabbbbaaaabbb= 1
# python checker.py get localhost vglmxskblp:zwzkvrfiac aaaaaaaabbbbbbbbaaaabbbbaaaabbb= 1

if __name__ == "__main__":
    host = "10.60.5.2"
    # host = "localhost"

    # client = c.Client(host, 12345, 7000)
    # print(client.send_flight_state(32 * 'a', 100, 100, 16 * b'1', 15 * 'a', 32 * 'b', False))

    verdict = checker.check_service(CheckRequest(host))
    print(code[verdict._code])

    verdict = checker.put_flag(PutRequest("", "flagflag__flagflag__flagflagflag", 1, host))
    flag_id = verdict._public_message
    print(code[verdict._code], flag_id)

    verdict = checker.get_flag(GetRequest(flag_id, "flagflag__flagflag__flagflagflag", 1, host))
    print(code[verdict._code])
