#!/usr/bin/python3

import argparse
import requests
import time


def main():
    start_time = time.time()

    URL1 = "http://sion.stikom-bali.ac.id/load_login.php"
    URL2 = "http://sion.stikom-bali.ac.id/reg/mhsscrdet.php"
    OK_TXT = """<script language="JavaScript1.2">document.getElementById('usern').style.backgroundColor='#F3F3F3';document.getElementById('passw').style.backgroundColor='#F3F3F3'</script><div id="divTarget">Success </div><script language="javascript">window.location ='/reg/'</script>"""

    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    parser.add_argument("pin", help="PIN to try login")
    args = parser.parse_args()

    print("Trying to login...")
    s = requests.Session()
    r = s.post(URL1, data={"usern": args.nim, "passw": args.pin})
    if not r.text == OK_TXT:
        print("Wrong NIM / PIN please try again")
        exit(1)
    else:
        print("Login succes, trying to extract data...")

    TXT0 = "<center><strong>[HASIL PENCARIAN DATA MAHASISWA]</strong></center><table><tr><th align='center'>NIM</th><th align='center'>NAMA</th><th align='center'>DETAIL</th></tr>"
    TXT1 = "<tr class='labelhitam' bgcolor=#CCCCCC><td width='120' align='center'>"
    TXT2 = "<tr class='labelhitam' bgcolor=#FFFFFF><td width='120' align='center'>"
    TXT3 = "</td><td width='450'>"
    TXT4 = "</td><td><a href='mhsdet.php?nim="
    TXT5 = "' class='linkhitam'>Detail</a></td></tr>"
    TXT6 = "</table>"

    data = str(s.get(URL2).text)
    data = data.replace(TXT0, "")
    data = data.replace(TXT1, "")
    data = data.replace(TXT2, "")
    data = data.replace(TXT3, "\n")
    data = data.replace(TXT4, "\n")
    data = data.replace(TXT5, "\n")
    data = data.replace(TXT6, "")
    data = data.split("\n")[:-1]

    data = [int(t) if n % 3 == 0 else 0 for (n, t) in enumerate(data)]
    data = sorted(list(set(data)))
    data.remove(0)
    with open('list.txt', 'w') as outfile:
        data = list(map(str, data))
        outfile.write(' '.join(data))

    total_time = time.time() - start_time

    print("Extracted {} data in {}s".format(len(data), total_time))


if __name__ == "__main__":
    main()
