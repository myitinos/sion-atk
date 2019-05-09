#!/usr/bin/env python3

import argparse

from requests import Session
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class ELogin(object):
    url = "http://elearning.stikom-bali.ac.id"
    # target = "MAHASISWA || E-LEARNING STIKOM BALI"

    def __init__(self, nim, pin, session=None):
        self.data = {
            '__VIEWSTATE': '',
            'ctl00$txtUser': nim,
            'ctl00$txtPass': pin,
            'ctl00$btnLogin': 'Login',
        }
        self.session = session
        self.user_agent = UserAgent().random

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
            # index = self.session.get(self.url)
            # soup = BeautifulSoup(index.text, 'html.parser')
            # self.data.update({'__VIEWSTATE': soup.find(
            #     "input", id="__VIEWSTATE")['value']})
            # self.data.update({'__VIEWSTATEGENERATOR': soup.find(
            #     "input", id="__VIEWSTATEGENERATOR")['value']})

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
