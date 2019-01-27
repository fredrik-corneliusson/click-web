import locale
import os
import shutil
import sys
import tempfile
from html import escape
from pathlib import Path
from typing import List

from flask import request, Response, url_for
from werkzeug.utils import secure_filename

import click_web

import subprocess

from .input_fields import separator

log = None

HTML_HEAD = '''<!doctype html>
<html lang="en">
<head>
    <link rel="stylesheet" href="{pure_css_location}"/>
    <link rel="stylesheet" href="{click_web_css_location}"/>
</head>
<body>'''
HTML_TAIL = '''
</body>
'''


def exec(command_path):
    """
    Execute the command and stream the output from it as response
    :param command_path:
    """
    global log
    log = click_web.logger

    root_command, *commands = command_path.split('/')

    cmd = [sys.executable,  # run with same python executable we are running with.
           click_web.script_file]
    req_to_args = RequestToCommandArgs()
    # root command_index should not add a command
    cmd.extend(req_to_args.command_args(0))
    for i, command in enumerate(commands):
        cmd.append(command)
        cmd.extend(req_to_args.command_args(i + 1))

    index_location = url_for('.index')
    current_location = request.path
    pure_css_location = url_for('static', filename='pure.css')
    click_web_css_location = url_for('static', filename='click_web.css')

    def _generate_output():
        yield HTML_HEAD.format(pure_css_location=pure_css_location, click_web_css_location=click_web_css_location)
        yield (f'<div class="back-links">Back to <a href="{index_location}">[index]</a>&nbsp;&nbsp;'
               f'<a href="{current_location}">[{current_location}]</a></div>')
        yield '<div class="command-line">Executing: {}</div>'.format('/'.join(commands))
        yield '<pre class="script-output">'
        yield from _run_script_and_generate_stream(req_to_args, cmd)
        yield '</pre>'
        yield from _create_result_footer(req_to_args)
        yield HTML_TAIL

    return Response(_generate_output(), mimetype='text/html')


def _run_script_and_generate_stream(req_to_args: 'RequestToCommandArgs', cmd: List[str]):
    """
    Execute the command the via Popen and yield output
    """
    log.info('Executing: %s', cmd)
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               bufsize=1)
    log.info('script running Pid: %d', process.pid)

    encoding = locale.getpreferredencoding(False)

    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            yield escape(line.decode(encoding))
    process.wait()  # wait for the subprocess to exit
    log.info('script finished Pid: %d', process.pid)
    for fi in req_to_args.field_infos:
        fi.after_script_executed()


def _create_result_footer(req_to_args: 'RequestToCommandArgs'):
    to_download = [fi for fi in req_to_args.field_infos if fi.generate_download_link]
    if to_download:
        yield '<b>Result files:</b><br>'
        for fi in to_download:
            yield '<ul> '
            yield f'<li>{_build_relative_link(fi)}<br>'
            yield '</ul>'
    else:
        yield 'DONE'


def _build_relative_link(field_info):
    """Hack as url_for needed request context"""

    rel_file_path = Path(field_info.file_path).relative_to(click_web.OUTPUT_FOLDER)
    uri = f'/static/results/{rel_file_path.as_posix()}'
    return f'<a href="{uri}">{field_info.cmd_opt}</a>'


class RequestToCommandArgs:

    def __init__(self):
        field_infos = [FieldInfo.factory(key) for key in list(request.form.keys()) + list(request.files.keys())]
        # important to sort them so they will be in expected order on command line
        self.field_infos = list(sorted(field_infos))

    def command_args(self, command_index) -> List[str]:
        """
        Convert the post request into a list of command line arguments

        :param command_index: (int) the index for the command to get arguments for.
        :return: list of command line arguments for command at that cmd_index
        """
        args = []

        # only include relevant fields for this command index
        commands_field_infos = [fi for fi in self.field_infos if fi.cmd_index == command_index]
        commands_field_infos = sorted(commands_field_infos)

        for fi in commands_field_infos:
            log.info('filed info: %s', fi)
            if fi.cmd_opt.startswith('--'):
                # it's an option
                args.extend(self._process_option(fi))

            else:
                # argument(s)
                if isinstance(fi, FieldFileInfo):
                    # it's a file, append the written temp file path
                    # TODO: does file upload support multiple keys? In that case support it.
                    args.append(fi.file_path)
                else:
                    args.extend(request.form.getlist(fi.key))
        return args

    def _process_option(self, field_info):
        vals = request.form.getlist(field_info.key)
        if field_info.is_file:
            # it's a file, append the file path
            yield field_info.cmd_opt
            yield field_info.file_path
        elif vals:
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
        "0.1.argument.file[rb].an-argument"
    """

    @staticmethod
    def factory(key):
        parts = key.split(separator)
        type = parts[3]
        is_file = type.startswith('file')
        is_path = type.startswith('path')
        is_uploaded = key in request.files
        if is_file:
            if is_uploaded:
                field_info = FieldFileInfo(key)
            else:
                field_info = FieldOutFileInfo(key)
        elif is_path:
            if is_uploaded:
                field_info = FieldPathInfo(key)
            else:
                field_info = FieldPathOutInfo(key)
        else:
            field_info = FieldInfo(key)
        return field_info

    def __init__(self, key):
        self.key = key

        parts = key.split(separator)
        'the int index of the command it belongs to'
        self.cmd_index = int(parts[0])
        'the int index for the ordering of paramters/arguments'
        self.parameter_index = int(parts[1])
        'Type of option (argument, option, flag)'
        self.option_type = parts[2]
        'Type of option (file, text)'
        self.type = parts[3]
        self.is_file = self.type.startswith('file')

        'The actual command line option (--debug)'
        self.cmd_opt = parts[4]

        self.generate_download_link = False

    def after_script_executed(self):
        pass

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
        # Extract the file mode that is in the type e.g file[rw]
        self.type, mode = self.type.split('[')
        self.mode = mode[:-1]
        self.generate_download_link = True if 'w' in self.mode else False

        log.info(f'File mode for {self.key} is  {mode}')
        self.save()

    @classmethod
    def temp_dir(cls):
        if not cls._temp_dir:
            cls._temp_dir = tempfile.mkdtemp(dir=click_web.OUTPUT_FOLDER)
        log.info(f'Temp dir: {cls._temp_dir}')
        return cls._temp_dir

    def save(self):
        log.info('Saving...')

        log.info('field value is a file! %s', self.key)
        file = request.files[self.key]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            raise ValueError('No selected file')
        elif file and file.filename:
            filename = secure_filename(file.filename)
            name, suffix = os.path.splitext(filename)

            fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=name, suffix=suffix)
            self.file_path = filename
            log.info(f'Saving {self.key} to {filename}')
            file.save(filename)

    def __str__(self):

        res = [super().__str__()]
        res.append(f'file_path: {self.file_path}')
        return ', '.join(res)


class FieldOutFileInfo(FieldFileInfo):
    """
    Used when file option is just for output and form posted it as hidden field.
    Just create a empty temp file to give it's path to command.
    """

    def save(self):
        name = secure_filename(self.key)

        fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=name)
        log.info(f'Creating empty file for {self.key} as {filename}')
        self.file_path = filename


class FieldPathInfo(FieldFileInfo):
    """
    Use for processing input fields of path type.
    Extracts the posted data to a temp folder.
    When script finished zip that folder and provide download link to zip file.
    """

    def save(self):
        super().save()
        zip_extract_dir = tempfile.mkdtemp(dir=self.temp_dir())

        log.info(f'Extracting: {self.file_path} to {zip_extract_dir}')
        shutil.unpack_archive(self.file_path, zip_extract_dir, 'zip')
        self.file_path = zip_extract_dir

    def after_script_executed(self):
        super().after_script_executed()
        fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=self.key)
        folder_path = self.file_path
        self.file_path = filename

        log.info(f'Zipping {self.key} to {filename}')
        self.file_path = shutil.make_archive(self.file_path, 'zip', folder_path)
        log.info(f'Zip file created {self.file_path}')
        self.generate_download_link = True


class FieldPathOutInfo(FieldOutFileInfo):
    """
    Use for processing output fields of path type.
    Create a folder and use as path to script.
    When script finished zip that folder and provide download link to zip file.
    """

    def save(self):
        super().save()
        self.file_path = tempfile.mkdtemp(dir=self.temp_dir())

    def after_script_executed(self):
        super().after_script_executed()
        fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=self.key)
        folder_path = self.file_path
        self.file_path = filename
        log.info(f'Zipping {self.key} to {filename}')
        self.file_path = shutil.make_archive(self.file_path, 'zip', folder_path)
        log.info(f'Zip file created {self.file_path}')
        self.generate_download_link = True
