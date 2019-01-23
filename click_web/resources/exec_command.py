import locale
import sys
import tempfile
from html import escape
from typing import List

from flask import request, Response
from werkzeug.utils import secure_filename

import click_web

import subprocess

from click_web.resources.command import separator

log = None


def exec(command_path):
    '''
    Execute the command, will execute the script via Popen and stream the output from it as response
    :param command_path:
    :return:
    '''
    global log
    log = click_web.flask_app.logger

    root_command, *commands = command_path.split('/')

    cmd = [sys.executable,  # run with same python executable we are running with.
           click_web.script_file]
    r = RequestToCommandArgs()
    # root command_index should not add a command
    cmd.extend(r.command_args(0))
    for i, command in enumerate(commands):
        cmd.append(command)
        cmd.extend(r.command_args(i + 1))

    log.info('Executing: %s', cmd)
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               bufsize=1)
    log.info('script running Pid: %d', process.pid)

    def commands_output_stream_generator():
        encoding = locale.getpreferredencoding(False)
        yield '<pre>'
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                yield escape(line.decode(encoding))
        process.wait()  # wait for the subprocess to exit
        yield '</pre>'
        yield '<b>Done</b>'
        click_web.flask_app.logger.info('script finished Pid: %d', process.pid)

    return Response(commands_output_stream_generator(), mimetype='text/html')


class RequestToCommandArgs:

    def command_args(self, command_index) -> List[str]:
        """
        Convert the post request into a list of command line arguments

        :param command_index: (int) the index for the command to get arguments for.
        :return: list of command line arguments for command at that cmd_index
        """
        click_web.flask_app.logger.info("files: %r", request.files)
        args = []
        field_file_infos = [FieldFileInfo(key) for key in list(request.files.keys())]
        field_infos = [FieldInfo(key) for key in list(request.form.keys())]
        field_infos += field_file_infos

        # only include relevant fields for this command index
        field_infos = [fi for fi in field_infos if fi.cmd_index == command_index]
        field_infos = sorted(field_infos)

        for fi in field_infos:
            click_web.flask_app.logger.info('filed info: %s', fi)
            if fi.key in request.files:
                # it's a file, save it to temp location and insert it's path into request.form
                fi.save()

            if fi.cmd_opt.startswith('--'):
                # it's an option
                args.extend(self._process_option(fi))

            else:
                # argument(s)
                if fi in field_file_infos:
                    # it's a file, append the written temp file path
                    # TODO: does file upload support multiple keys? In that case support it.
                    args.append(fi.file_path)
                else:
                    args.extend(request.form.getlist(fi.key))
        return args

    def _process_option(self, field_info):
        # TODO: handle options that takes File
        vals = request.form.getlist(field_info.key)
        if vals:
            # opt with value, if option was given multiple times get the values for each.
            if field_info.option_type == 'flag' or ''.join(vals):
                # flag options should always be set if we get them
                # for normal options they must have a non empty value
                yield field_info.cmd_opt
                for val in vals:
                    if val:
                        yield val
        else:
            # boolean opt
            yield field_info.cmd_opt


class FieldInfo:
    """
    Extract information from the encoded form input field name
    e.g.
        "0.0.option.text.--an-option"
        "0.1.argument.file.an-argument"
    """

    def __init__(self, key):
        self.key = key

        parts = key.split(separator)
        'the int index of the command it belongs to'
        self.cmd_index = int(parts[0])
        'the int index for the ordering of paramters/arguments'
        self.parameter_index = int(parts[1])
        'Type of option (argument, option, flag)'
        self.option_type = parts[2]
        'Type of option (argument, option, flag)'
        self.type = parts[3]
        'The actual command line option (--debug)'
        self.cmd_opt = parts[4]

    def __str__(self):
        res = []
        res.append(f'key: {self.key}')
        res.append(f'key_cmd_index: {self.cmd_index}')
        res.append(f'parameter_index: {self.parameter_index}')
        res.append(f'option_type: {self.option_type}')
        res.append(f'type: {self.type}')
        res.append(f'cmd_opt: {self.cmd_opt}')
        return ', '.join(res)

    def __lt__(self, other):
        "Make class sortable"
        return (self.cmd_index, self.parameter_index) < (other.cmd_index, other.parameter_index)

    def __eq__(self, other):
        return self.key == other.key


class FieldFileInfo(FieldInfo):
    """
    Use for processing input fileds of file type.
    Saves the posted data to a temp file.
    """
    'temp dir is on class in order to be uniqe for each request'
    _temp_dir = None

    def __init__(self, key):
        super().__init__(key)
        self.file_path = None
        # Extract the file mode that is in the type e.g file[rw]
        self.type, mode = self.type.split('[')
        self.mode = mode[:-1]
        self.generate_download_link = True if 'w' in self.mode else False

        log.info(f'File mode for {self.key} is  {mode}')

    @classmethod
    def temp_dir(cls):
        if not cls._temp_dir:
            cls._temp_dir = tempfile.mkdtemp(prefix='click-web-')
        log.info(f'Temp dir: {cls._temp_dir}')
        return cls._temp_dir

    def save(self):
        # TODO: handle Paths (upload zip file)
        log.info('Saving...')

        click_web.flask_app.logger.info('field value is a file! %s', self.key)
        file = request.files[self.key]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            raise ValueError('No selected file')
        elif file and file.filename:
            filename = secure_filename(file.filename)

            fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=filename)
            self.file_path = filename
            log.info(f'Saving {self.key} to {filename}')
            file.save(filename)
            # zip_ref = zipfile.ZipFile(os.path.join(UPLOAD_FOLDER, filename), 'r')
            # zip_ref.extractall(UPLOAD_FOLDER)
            # zip_ref.close()
