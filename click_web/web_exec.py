import sys
from typing import List

from flask import request, Response

import click_web

import subprocess


def exec(command_path):
    '''
    Execute the command, will execute the script via Popen
    :param command_path:
    :return:
    '''
    commands = command_path.split('/')
    command_args = _request_to_command_args()

    cmd = [sys.executable,  # run with same python executable we are running with.
           click_web.script_file]
    cmd += commands
    cmd += command_args

    click_web.flask_app.logger.info('Executing: %s', cmd)
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               bufsize=1)
    click_web.flask_app.logger.info('script running Pid: %d', process.pid)

    def commands_output_stream_generator():
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                yield line
        process.wait()  # wait for the subprocess to exit
        click_web.flask_app.logger.info('script finished Pid: %d', process.pid)

    return Response(commands_output_stream_generator(), mimetype='text/plain')


def _request_to_command_args() -> List[str]:
    '''
    Convert the post request into a list of command line arguments to be passed to click.invoke
    :return: list of command line arguments
    '''
    args = []
    for key in request.form.keys():
        if key.startswith('--'):
            # it's an option
            vals = request.form.getlist(key)
            if vals:
                # opt with value, if option was given multiple times get the values for each.
                for val in vals:
                    args.append(key)
                    if val:
                        args.append(val)
            else:
                # boolean opt
                args.append(key)

        else:
            # argument(s)
            args.extend(request.form.getlist(key))
    return args
