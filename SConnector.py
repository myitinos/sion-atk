#!/usr/bin/python3
import requests

class SConnector(object):
  url = "http://sion.stikom-bali.ac.id/load_login.php"
  ok_text = """<script language="JavaScript1.2">document.getElementById('usern').style.backgroundColor='#F3F3F3';document.getElementById('passw').style.backgroundColor='#F3F3F3'</script><div id="divTarget">Success </div><script language="javascript">window.location ='/reg/'</script>"""
  ok_len = len(ok_text)

  def __init__(self, nim, pin):
    self.payload = {'usern':nim, 'passw':pin}

  def connect(self):
    connection = requests.post(self.url, data=self.payload)
    # self.text = connection.text
    self.status = len(connection.text) == self.ok_len and connection.text == self.ok_text

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('-N', '--nim', help='NIM for testing', required=True)
  parser.add_argument('-P', '--pin', help='PIN for testing', required=True)

  args = parser.parse_args()

  test = SConnector(args.nim, args.pin)
  test.connect()
  print(test.status)
