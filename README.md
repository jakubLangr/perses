# Perses

## Infrastructure code for Yepic

Features:
* `tracking.py` 
* `README.md`

###`tracking.py` is a wrapper around CLI that
* enables the user to get a sentry notification everytime a script finishes running
* shutdown the machine between 0 and 9 am 
* logs CLI output to `cli_output/` with a timestamp of the run
	- This file is created automatically 
* accepts two parameters: 
	- `--testing`
	- `--flags`, which are passed to the downstream script.  

