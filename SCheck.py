#!/usr/bin/env python3.6

import argparse     # argparse
import requests     # requests.Session
import time         # time.time

URL = "http://sion.stikom-bali.ac.id/load_login.php"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    parser.add_argument("pin", help="PIN to try login")
    args = parser.parse_args()

    print('Sending requests...')
    start_time = time.time()
    with requests.Session() as session:
        resp1 = session.post(URL, data={'uname': args.nim, 'passwd': args.pin})
        resp1 = resp1.text
        resp2 = session.post(URL, data={'uname': args.nim, 'passwd': args.pin[::-1]})
        resp2 = resp2.text
    print('Requests completed in %0.2f' % (time.time() - start_time))

    if resp1 == resp2:
        print('Got only one response, please check your NIM and PIN:')
        print(resp1)
    else:
        print('First Response:')
        print(resp1)
        print('Second Response:')
        print(resp2)


if __name__ == "__main__":
    main()
