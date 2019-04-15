#!/usr/bin/env python3.6

from SLogin import SLogin
from time import time as now


class SCheck(object):
    def __init__(self, nim, pin):
        self.conn0 = SLogin(nim, pin)
        self.conn1 = SLogin(nim, pin[::-1])

    def connect(self):
        self.conn0.login()
        self.conn1.login()
        return self

    def is_both_equal(self):
        return self.conn0.text == self.conn1.text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    parser.add_argument("pin", help="PIN to try login")
    args = parser.parse_args()

    start_time = now()
    checker = SCheck(args.nim, args.pin)
    checker.connect()
    if checker.is_both_equal():
        print('Got same response, please check your NIM/PIN')
    else:
        print('Got two different result. Writing to conn0.txt and conn1.txt')
        with open('conn0.txt', 'w') as outfile:
            outfile.write(checker.conn0.text)
        with open('conn1.txt', 'w') as outfile:
            outfile.write(checker.conn1.text)
