#!/usr/bin/python3
import re

from requests import Session
from SLogin import SLogin


class STract(SLogin):
    urlTract = "reg/mhsscrdet.php?tipe=nim&txt={}"
    extracted = []

    def extract(self):
        # check if logged in
        if self.success:
            # just a little future proofing
            for i in range(0, 10):
                raw = self.session.get(self.url + self.urlTract.format(i)).text

                if 'HASIL PENCARIAN DATA MAHASISWA' in raw:
                    # use regex to find all nim
                    raw = re.findall("([0-9]{9})", raw)
                    # remove duplicate values using set
                    raw = list(set(raw))
                    # sort all the values
                    raw = sorted(raw)

                    # append to all extracted data
                    self.extracted += raw

            return self.extracted
        else:
            raise Exception("Please login first")


if __name__ == "__main__":
    import argparse
    from time import time as now

    start_time = now()
    parser = argparse.ArgumentParser()
    parser.add_argument("nim",
                        help="NIM to try login")
    parser.add_argument("pin",
                        help="PIN to try login")
    parser.add_argument("--outfile",
                        metavar="FILE",
                        default="temp.txt",
                        help="outfile target")
    args = parser.parse_args()

    with STract(args.nim, args.pin) as extraction:
        print('Trying to login with {} {}'.format(args.nim, args.pin))
        if extraction.login():
            print('Login success, extracing data...')
            data = extraction.extract()
            print('Extraced {} data'.format(len(data)))

            with open(args.outfile, 'w') as output:
                print('Writing data to output file...')
                output.write("\n".join(data))

            print('Done in {:0.2f}s'.format(now() - start_time))
        else:
            print('Login failed')
