#!/usr/bin/env python3

import logging

from multiprocessing import Pool, Manager, Queue, Lock, cpu_count
from SBrute import SBrute


def init_logging(args):
    logFormatter = logging.Formatter(
        fmt="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')

    rootLogger = logging.getLogger()

    if args.logfile is not None:
        fileHandler = logging.FileHandler(args.logfile, mode='a')
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

    if not args.disable_console_logging:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.DEBUG if args.debug else logging.INFO)


def parse_argument():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--disable-console-logging",
                        action="store_true",
                        default=False,
                        help="disable progress bar")
    parser.add_argument("--disable-progressbar",
                        action="store_true",
                        default=False,
                        help="disable progress bar")
    parser.add_argument("--debug",
                        action="store_true",
                        default=False,
                        help="activate debug logging")
    parser.add_argument("--retry",
                        metavar="N",
                        default=4,
                        type=int,
                        help="number of max retry if exception occured, default is 4")
    parser.add_argument("-i", "--infile",
                        metavar="PATH",
                        help="txt file containing targets to bruteforce")
    parser.add_argument("-o", "--outfile",
                        metavar="PATH",
                        default="temp.txt",
                        help="txt file to write if not all target is tried, default is temp.txt")
    parser.add_argument("--logfile",
                        metavar="PATH",
                        default="log.txt",
                        help="log file destination")
    parser.add_argument("--target",
                        metavar="TARGET",
                        type=str,
                        help="target NIM to bruteforce",
                        nargs="+")
    parser.add_argument("--range",
                        metavar=("START", "END"),
                        type=int,
                        nargs=2,
                        help="range of target NIM to bruteforce, END is included in the range")
    parser.add_argument("-P", "--process",
                        metavar="N",
                        type=int,
                        default=cpu_count(),
                        help="Specify number of process to use, default value is CPU Count.")
    parser.add_argument("-T", "--thread",
                        metavar="N",
                        type=int,
                        default=16,
                        help="Specify number of thread to use, default value is 16.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argument()
    init_logging(args)

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
        bar = None
        for t in target:
            s = SBrute(nim=t,
                       thread=args.thread,
                       disableProgressBar=args.disable_progressbar,
                       start=False)
            done.append(s.start())

        # with Pool(args.process) as pool:
        #     pool.starmap(SBrute, [(t, args.thread, True, positionQueue)
        #                           for t in target])
    except KeyboardInterrupt:
        logging.info('Interrupted by user input')
    except Exception as ex:
        logging.exception('Exception occured: {}'.format(str(ex)))
    finally:
        if len(done) == len(target):
            logging.info(
                'Program completed successfully, found {} pins'.format(
                    len(done)
                )
            )
        else:
            logging.info(
                'Program terminated prematurely. Writing remaining target to temp.txt')
            with open(args.outfile, 'w') as outfile:
                outfile.write('\n'.join([str(t)
                                         for t in target if t not in done]))
