'''
Stopped training alerting script.
'''
__author__ = 'Jakub Langr'
import subprocess
import sentry_sdk
import datetime
import os
import perses_config as config
from sentry_sdk import capture_exception, capture_message
from argparse import ArgumentParser
import sys

import subprocess as sp


CWD = os.getcwd()

if not os.path.exists(f'{CWD}/perses_config.py'):
    print('Config does not exist. Please enter the commands.')
    command = input('Enter the command to run:')
    defaults = input("Please set defaults[Y/N]")
    sentry_sdn = input("Enter the Sentry SDN")
    with open('config_perses.py',"w+") as f:
        f.write(f"command = {command}")
        f.write("defaults = {defaults}")
        f.write("sentry_sdn = {sentry_sdn}")


# variables to set
shutdown_hours = [22, 23] + list(range(0,9))
now_str = str(datetime.datetime.now())[:-7].replace(' ','_')
log_file = f'cli_output/{config.exec_file}_{now_str}.txt'

# uses the current python env
os.environ['BETTER_EXCEPTIONS'] = "1"
py_path = sp.run(['which','python'], stdout=sp.PIPE)
base_py = py_path.stdout.decode()[:-1]

# makes sure the file above exists
open(log_file, 'a').close()

# This should be eventually grabbed from ENV or something.
sentry_sdk.init(config.sentry_sdn)


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
        command = f'{base_py} buggy.py {FLAGS}'
        # e.g. command = f'{base_py} train.py {FLAGS} 2>> {log_file}'
        # alt command = f'{base_py} train.py {FLAGS} 2>&1 | tee {log_file}'
    else:
        # example
        command = f'{base_py} {config.exec_file} {FLAGS} 2>> {log_file}'

    try:
        print(f'Starting tracking, running command: \n {command}')
        from IPython.utils.capture import capture_output

        with capture_output() as c:
            os.system(command)

        c()
        
        print(c.outputs, c.stdout, c.stderr)
    except Exception as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        capture_exception(exc)
    else:
        capture_message('Program exited, Output: \n{}\n'.format(output))
        if not NO_SHUTDOWN and datetime.datetime.now().hour in shutdown_hours:
            capture_message('It is also late. Shutting down the instance.')
            os.system('sudo shutdown now')
        