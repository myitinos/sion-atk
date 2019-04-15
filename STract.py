#!/usr/bin/python3

from requests import Session
from SLogin import SLogin


class STractNotLoggedIn(Exception):
    pass


class STract(object):
    url = "http://180.250.7.188/reg/mhsscrdet.php"

    def __init__(self, nim, pin):
        self.connection = SLogin(nim, pin)
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def connect(self):
        self.connection.login(session=self.session)

        return self.connection.success

    def extract(self):
        txt0 = "<center><strong>[HASIL PENCARIAN DATA MAHASISWA]</strong></center><table><tr><th align='center'>NIM</th><th align='center'>NAMA</th><th align='center'>DETAIL</th></tr>"
        txt1 = "<tr class='labelhitam' bgcolor=#CCCCCC><td width='120' align='center'>"
        txt2 = "<tr class='labelhitam' bgcolor=#FFFFFF><td width='120' align='center'>"
        txt3 = "</td><td width='450'>"
        txt4 = "</td><td><a href='mhsdet.php?nim="
        txt5 = "' class='linkhitam'>Detail</a></td></tr>"
        txt6 = "</table>"

        if self.connection.success:
            data = self.session.post(self.url).text

            data = data.replace(txt0, "")
            data = data.replace(txt1, "")
            data = data.replace(txt2, "")
            data = data.replace(txt3, "\n")
            data = data.replace(txt4, "\n")
            data = data.replace(txt5, "\n")
            data = data.replace(txt6, "")

            data = data.split("\n")[:-1]
            data = [int(t) if n % 3 == 0 else 0 for (n, t)
                    in enumerate(data)]
            data = sorted(list(set(data)))
            data.remove(0)

            data = list(map(str, data))

            return data
        else:
            raise STractNotLoggedIn("Please login first")


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
        print('Trying to connect with {} {}'.format(args.nim, args.pin))
        if extraction.connect():
            print('Login success, extracing data...')
            data = extraction.extract()
            print('Extraced {} data'.format(len(data)))

            with open(args.outfile, 'w') as output:
                print('Writing data to output file...')
                output.write("\n".join(data))

            print('Done in {:0.2f}s'.format(now() - start_time))
        else:
            print('Login failed')
