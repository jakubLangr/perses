# Perses

## Infrastructure code for Yepic

Features:
* `tracking.py` 
* `README.md`
* `.gitignore`

Needs: `config.py` with the following defined as string variables.
* `py_path`: python env you want to use
* `sentry_str`: sentry DNS string
* `exec_file`: what file you want to run
* `defaults`: what flags will be appended by default


## `tracking.py` is a wrapper around CLI that
* enables the user to get a sentry notification everytime a script finishes running
* shutdown the machine between 22 pm and 8 am 
* logs CLI output to `cli_output/` with a timestamp of the run
	- This file is created automatically 
* accepts parameters: 
	- `--testing`
	- `--flags`, which are passed to the downstream script.  
	- `no_shutdown`