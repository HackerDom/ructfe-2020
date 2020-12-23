import string
from gornilo import CheckRequest, PutRequest, GetRequest

import checker
import random


def get_random_string(k=10):
    return ''.join(random.choices(string.ascii_lowercase, k=k))


code = {
    101: "OK  # operation has been finished sucessfully",
    102: "CORRUPT  # service is working, but there is no correct flag",
    103: "MUMBLE  # service is working incorrect (iex: not responding to the protocol)",
    104: "DOWN  # service not working (iex: no tcp connection can be initialized)",
    110: "CHECKER_ERROR  # something gone wrong with args or with remote part of checker"
}

if __name__ == "__main__":
    verdict = checker.check_service(CheckRequest("localhost"))
    print(code[verdict._code])

    verdict = checker.put_flag(PutRequest("", "flagflag__flagflag__flagflagflag", 1, "localhost"))
    flag_id = verdict._public_message
    print(code[verdict._code], flag_id)

    verdict = checker.get_flag(GetRequest(flag_id, "flagflag__flagflag__flagflagflag", 1, "localhost"))
    print(code[verdict._code])
