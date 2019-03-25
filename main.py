#!/usr/bin/python3
import requests

class SConnector(object):
  url = "http://sion.stikom-bali.ac.id/load_login.php"
  ok_text = " "
  def __init__(self, nim, pin):
    self.payload = {'usern':nim, 'passw':pin}

  def connect(self):
    self.connection = requests.post(self.url, data=self.payload)

  def status(self):
    return self.connection.text == self.ok_text

  def content(self):
    return self.connection.text

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('-N', '--nim', help='NIM for testing', required=True)
  parser.add_argument('-P', '--pin', help='PIN for testing', required=True)

  args = parser.parse_args()

  test = SConnector(args.nim, args.pin)
  test.connect()
  print(test.content())
