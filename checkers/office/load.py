import signal
import threading
import subprocess
import time
import sys


PARALLEL = 30
WAIT_TIME = 1  # sleep time after execution in seconds
LIMIT = 1000
START_JITTER = 0.3 # in seconds

if len(sys.argv) != 3:
    print("invalid format")
    print("load.py <checker_path> <IP>")
    sys.exit(1)

path = sys.argv[1]
IP = sys.argv[2]

stop_requested = False
processes = {}


def sig_handler(signum, frame):
    print("handling signal: %s\n" % signum)
    global stop_requested
    # term running processes
    for num in processes:
        print(f"sending SIGKIL to worker({num})...")
        p = processes[num]
        p.kill()
    stop_requested = True


def sleep(t: int):
    for _ in range(int(t / 0.1)):
        if stop_requested:
            break
        time.sleep(0.1)


def worker(num: int, limit: int, wait_time: int):
    print(f"[worker({num})]\t starts")
    for r in range(limit):
        if stop_requested:
            print(f"[worker({num})]\t stopped")
            return
        start = time.time()
        p = subprocess.Popen(
            [
                "python3",
                path, "TEST",
                IP
            ],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
        processes[num] = p
        p.wait()
        del processes[num]
        finish = time.time()
        if not stop_requested:
            print(f"[worker({num})]\t{r + 1} run finished in: '{finish - start}s'")
        sleep(wait_time)
    print(f"[worker({num})]\t finished work")


signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

if __name__ == '__main__':
    print(
        f"Starting load testing:\n"
        f"\tPARALLEL: '{PARALLEL}'\n"
        f"\tLIMIT: '{LIMIT}'\n"
        f"\tWAIT_TIME: '{WAIT_TIME}s'\n"
        f"\tSTART_JITTER: '{START_JITTER}s'\n"
    )
    worker_limit = LIMIT / PARALLEL
    for i in range(PARALLEL):
        threading.Thread(target=worker, args=(i, int(worker_limit), WAIT_TIME)).start()
        if stop_requested:
            break
        sleep(START_JITTER)
