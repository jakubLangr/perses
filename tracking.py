'''
Stopped training alerting script.
'''
__author__ = 'Jakub Langr'
import subprocess
import sentry_sdk
import datetime
import os
from sentry_sdk import capture_exception, capture_message
from argparse import ArgumentParser

os.environ['BETTER_EXCEPTIONS'] = "1"

now_str = str(datetime.datetime.now())[:-7].replace(' ','_')
base_py = '/home/ubuntu/anaconda3/envs/pytorch_p36/bin/python3'
log_file = f'cli_output/train.py_{now_str}.txt'

# This should be eventually grabbed from ENV or something.
sentry_sdk.init("https://53a270efda1044afaea7a773d065be60@sentry.io/1528098")

if __name__ == "__main__":
    usage = 'Tracks experiments by making a Sentry alert when a script finishes.'
    parser = ArgumentParser(description=usage)
    parser.add_argument(
        '--flags', type=str, default='--parallel --batch_size 256',
        help='Which flags you want to pass to the underlying script.'
        'e.g. --parallel --batch_size 256'
    )
    parser.add_argument(
        '--testing', type=bool, default=False,
        help='If we are testing / doing a dry run. Default: False'
    )
    FLAGS = vars(parser.parse_args())['flags']
    TESTING = vars(parser.parse_args())['testing']

    # makes sure the file above exists
    open(log_file, 'a').close()

    if TESTING:
        command = f'{base_py} buggy.py {FLAGS} 2>&1 | tee test.txt'
    else:
        command = f'{base_py} train.py {FLAGS} 2>> {log_file}'


    try:
        print(f'Starting tracking, running command: \n {command}')
        output = subprocess.check_output(
            command, stderr=subprocess.PIPE, shell=True, timeout=3,
            universal_newlines=True)
            # os.system()
            # subprocess.run(f'{base_py} buggy.py 2>&1 | tee test.txt',
            #                 shell=True, check=True)
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        capture_exception(exc)
    else:
        capture_message('Program exited, Output: \n{}\n'.format(output))
        if datetime.datetime.now().hour in range(0,9):
            capture_message('It is also late. Shutting down the instance.')
            os.system('sudo shutdown now')
        
