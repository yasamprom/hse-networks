import argparse
import logging
import os
import subprocess
import platform


def ping(mtu, host, count):
    print(mtu, host, count)
    # cmd = ["ping", host, "-c", str(count), "-D", "-t", "255", "-s", str(mtu)]
    cmd = ["ping", host, "-c", "1", "-s", str(mtu), "-M", "do"]
    if platform.system().lower() == 'darwin':
        cmd = ["ping", "-D", "-s", str(mtu), host, "-c", "1", "-W", "3000"]
    print(cmd)
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    code = 1
    if res.returncode == 2:
        exit(2)
    if res.returncode == 0:
        code = 0
    return code, "", res.stderr


def worker(
        ping_count: int,
        verb_mode: str,
        host: str
) -> None:
    res = process(ping_count, verb_mode, host)
    print("ANSWER =", res)


def process(ping_count: int,
            verb_mode: str,
            host: str
            ):
    cnt = int(ping_count)
    if verb_mode == '1':
        logging.info("verbose on")

    reachable = True if os.system("ping -c 1 " + host) is 0 else False
    if not reachable:
        exit(2)

    disabled = subprocess.run(
        ["cat", "/proc/sys/net/ipv4/icmp_echo_ignore_all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if disabled.stdout == 1:
        print('ICMP is disabled. Enable it')
        exit(1)
    l, r = 0, 1491
    while l < r - 1:
        m = (l + r) // 2
        res = ping(m, host, cnt)
        code, out, err = res
        if code == 1:
            r = m
            continue
        if code == 0:
            l = m
            continue
        logging.error(err)
    return l + 28


parser = argparse.ArgumentParser(description='PMTUD')
parser.add_argument('-count_ping', default=1, help='count of pings')
parser.add_argument('-verb_mode', default=0, help='verbose mod')
parser.add_argument('host', help='host')

args = parser.parse_args()

host = args.host
count = args.count_ping
verbose = args.verb_mode

if __name__ == "__main__":
    worker(ping_count=count, verb_mode=verbose, host=host)
