'''
Stopped training alerting script.
'''
__author__ = 'Jakub Langr'
import subprocess
import sentry_sdk
import datetime
import os
import config
from sentry_sdk import capture_exception, capture_message
from argparse import ArgumentParser
import sys

import subprocess as sp
from concurrent.futures import ThreadPoolExecutor


os.environ['BETTER_EXCEPTIONS'] = "1"

shutdown_hours = [22, 23] + list(range(0,9))
now_str = str(datetime.datetime.now())[:-7].replace(' ','_')
base_py = config.py_path
log_file = f'cli_output/{config.exec_file}_{now_str}.txt'

# makes sure the file above exists
open(log_file, 'a').close()

# This should be eventually grabbed from ENV or something.
# sentry_sdk.init(config.sentry_str)

def log_popen_pipe(p, pipe_name):

    while p.poll() is None:
        line = getattr(p, pipe_name).readline()
        log_file.write(line)


if __name__ == "__main__":
    usage = 'Tracks experiments by making a Sentry alert when a script finishes.'
    parser = ArgumentParser(description=usage)
    parser.add_argument(
        '--flags', '-f', type=str, default='',
        help='Which flags you want to pass to the underlying script.'
        'e.g. --parallel --batch_size 256'
    )
    parser.add_argument(
        '--testing', '-t', type=bool, default=False,
        help='If we are testing / doing a dry run. Default: False'
    )
    parser.add_argument(
        '--no_shutdown', '-ns', type=bool, default=False,
        help='Shuts down the computer between in the shutdown_hours.'
        'Set to 22-08. Default: True')
    FLAGS = config.defaults + vars(parser.parse_args())['flags']
    TESTING = vars(parser.parse_args())['testing']
    NO_SHUTDOWN = vars(parser.parse_args())['no_shutdown']

    if TESTING:
        command = f'{base_py} {config.exec_file} {FLAGS}'
        # e.g. command = f'{base_py} train.py {FLAGS} 2>> {log_file}'
        # alt command = f'{base_py} train.py {FLAGS} 2>&1 | tee {log_file}'
    else:
        # example
        command = f'{base_py} {config.exec_file} {FLAGS} 2>> {log_file}'
        command = 'pwd'

    try:
        # import ipdb; ipdb.set_trace()
        with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, text=True) as p:

            with ThreadPoolExecutor(2) as pool:
                r1 = pool.submit(log_popen_pipe, p, 'stdout')
                r2 = pool.submit(log_popen_pipe, p, 'stderr')
                r1.result()

    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        capture_exception(exc)
    else:
        capture_message('Program exited, Output: \n{}\n'.format(process))
        if not NO_SHUTDOWN and datetime.datetime.now().hour in shutdown_hours:
            capture_message('It is also late. Shutting down the instance.')
            os.system('sudo shutdown now')
        
