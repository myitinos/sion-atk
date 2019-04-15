#!/usr/bin/env python3.6
import argparse
from requests import Session


class SLoginInvalidSession(Exception):
    pass


class SLogin(object):
    # url = "http://sion.stikom-bali.ac.id/load_login.php"
    url = "http://180.250.7.188/load_login.php"
    target = """<script language="javascript">window.location ='/reg/'</script>"""

    def __init__(self, nim, pin):
        self.data = {
            'uname': nim,
            'passwd': pin
        }

    def login(self, session=None):
        if session is None:
            with Session() as self.session:
                self.__connect()
        elif type(session) is Session:
            self.session = session
            self.__connect()
        else:
            raise SLoginInvalidSession("Invalid session provided")

    def __connect(self):
        response = self.session.post(self.url, self.data)
        self.text = response.text
        self.success = self.target in self.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    parser.add_argument("pin", help="PIN to try login")
    args = parser.parse_args()

    response = SLogin(args.nim, args.pin)
    print(response)
