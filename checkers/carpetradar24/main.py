import string
from gornilo import CheckRequest, PutRequest, GetRequest

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

if __name__ == "__main__":
    host = "10.60.4.2"
    verdict = checker.check_service(CheckRequest(host))
    print(code[verdict._code])

    verdict = checker.put_flag(PutRequest("", "flagflag__flagflag__flagflagflag", 1, host))
    flag_id = verdict._public_message
    print(code[verdict._code], flag_id)

    verdict = checker.get_flag(GetRequest(flag_id, "flagflag__flagflag__flagflagflag", 1, host))
    print(code[verdict._code])
