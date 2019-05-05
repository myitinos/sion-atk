#!/usr/bin/env python3.6
import argparse
import re
from requests import Session


class SLogin(object):
    # url = "http://sion.stikom-bali.ac.id/load_login.php"
    url = "http://180.250.7.188/"
    urlLogin = "load_login.php"
    target = """<script language="JavaScript1.2">document.getElementById('usern').style.backgroundColor='#F3F3F3';document.getElementById('passw').style.backgroundColor='#F3F3F3'</script><script language="javascript">window.location ='/reg/'</script>"""

    user_agent = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"""

    regex = re.compile("[a-f0-9]{32}")

    def __init__(self, nim, pin, session=None):
        self.data = {
            'uname': nim,
            'passwd': pin
        }
        self.session = session

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
            index = self.session.get(self.url)
            flag = self.regex.findall(index.text)[0]
            self.data.update({'flag': flag})

            headers = {
                'User-Agent': self.user_agent,
                'Referer': self.url
            }
            response = self.session.post(self.url + self.urlLogin,
                                         data=self.data,
                                         headers=headers)
            self.text = response.text
            self.success = self.target in self.text
            return self.success


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    parser.add_argument("pin", help="PIN to try login")
    args = parser.parse_args()

    with SLogin(args.nim, args.pin) as conn:
        if conn.login():
            print('Login success')
        else:
            print('Login failed')
        print(conn.text)
