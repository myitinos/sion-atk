#!/usr/bin/env python3

import argparse

from requests import Session
from SAgent import SAgent


class ELogin(object):
    url = "http://elearning.stikom-bali.ac.id"

    def __init__(self, nim, pin, session=None):
        self.data = {
            '__VIEWSTATE': '',
            'ctl00$txtUser': nim,
            'ctl00$txtPass': pin,
            'ctl00$btnLogin': 'Login',
        }
        self.session = session
        self.user_agent = next(SAgent)

    def __enter__(self):
        if type(self.session) is not Session:
            self.session = Session()
        return self

    def __exit__(self, *kwargs):
        self.session.close()

    def login(self):
        if type(self.session) is not Session:
            raise Exception("Invalid session")
        else:
            response = self.session.post(self.url,
                                         data=self.data,
                                         allow_redirects=False)
            self.text = response.text
            # self.success = self.target in self.text
            self.success = response.status_code == 302
            return self.success


if __name__ == "__main__":
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    parser.add_argument("pin", help="PIN to try login")
    parser.add_argument("count", type=int, help="repetition")
    args = parser.parse_args()

    tStart = time.time()
    for _ in range(args.count):
        with ELogin(args.nim, args.pin) as conn:
            print(conn.login())
            # if conn.login():
            #     print('Login success')
            # else:
            #     print('Login failed')
            # print(conn.text)
    tEnd = time.time()

    print("Completed in: {:02f}".format(tEnd - tStart))
