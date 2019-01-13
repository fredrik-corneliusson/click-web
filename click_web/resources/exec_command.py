import sys
from typing import List

from flask import request, Response

import click_web

import subprocess

from click_web.resources.command import form_command_index_separator


def exec(command_path):
    '''
    Execute the command, will execute the script via Popen and stream the output from it as response
    :param command_path:
    :return:
    '''
    root_command, *commands = command_path.split('/')

    cmd = [sys.executable,  # run with same python executable we are running with.
           click_web.script_file]
    # root command_index should not add a command
    cmd.extend(_request_to_command_args(0))
    for i, command in enumerate(commands):
        cmd.append(command)
        cmd.extend(_request_to_command_args(i + 1))

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


def _request_to_command_args(command_index) -> List[str]:
    """
    Convert the post request into a list of command line arguments
    
    :param command_index: (int) the index for the command to get arguments for.
    :return: list of command line arguments for command at that cmd_index
    """
    args = []
    for key in request.form.keys():
        key_cmd_index, cmd_opt = key.split(form_command_index_separator)
        if int(key_cmd_index) != command_index:
            # not a key for this command, skip
            continue
        elif cmd_opt.startswith('--'):
            # it's an option
            vals = request.form.getlist(key)
            if vals:
                # opt with value, if option was given multiple times get the values for each.
                args.append(cmd_opt)
                for val in vals:
                    if val:
                        args.append(val)
            else:
                # boolean opt
                args.append(cmd_opt)

        else:
            # argument(s)
            args.extend(request.form.getlist(key))
    return args
