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
    text_only = 'text/plain' in request.accept_mimetypes.values()

    def _generate_output(use_html: bool):
        if use_html:
            yield HTML_HEAD.format(pure_css_location=pure_css_location, click_web_css_location=click_web_css_location)
            yield (f'<div class="back-links">Back to <a href="{index_location}">[index]</a>&nbsp;&nbsp;'
                   f'<a href="{current_location}">[{current_location}]</a></div>')
        yield _create_cmd_header(commands)
        if use_html:
            yield '<pre class="script-output">'
        if use_html:
            yield from (escape(l) for l in _run_script_and_generate_stream(req_to_args, cmd))
        else:
            yield from _run_script_and_generate_stream(req_to_args, cmd)
        if use_html:
            yield '</pre>'
        yield from _create_result_footer(req_to_args)
        if use_html:
            yield HTML_TAIL

    return Response(_generate_output(use_html=not text_only),
                    mimetype='text/plain' if text_only else 'text/html')


def _run_script_and_generate_stream(req_to_args: 'RequestToCommandArgs', cmd: List[str]):
    """
    Execute the command the via Popen and yield output
    """
    log.info('Executing: %s', cmd)
    process = subprocess.Popen(cmd, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    log.info('script running Pid: %d', process.pid)

    encoding = locale.getpreferredencoding(False)

    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            yield line.decode(encoding)
    process.wait()  # wait for the subprocess to exit
    log.info('script finished Pid: %d', process.pid)
    for fi in req_to_args.field_infos:
        fi.after_script_executed()


def _create_cmd_header(commands: List[str]):
    """
    Generate a command header.
    Note:
        here we always allow to generate HTML as long as we have it between CLICK-WEB comments.
        This way the JS text readed knows this chunk will be special when inserting into DOM.
    """

    def generate():
        yield '<!-- CLICK_WEB START HEADER -->'
        yield '<div class="command-line">Executing: {}</div>'.format('/'.join(commands))
        yield '<!-- CLICK_WEB END HEADER -->'

    # important yield this block as one string so it pushed to client in one go.
    # so the whole block can be treated as html.
    html_str = '\n'.join(generate())
    return html_str


def _create_result_footer(req_to_args: 'RequestToCommandArgs'):
    """
    Generate a footer.
    Note:
        here we always allow to generate HTML as long as we have it between CLICK-WEB comments.
        This way the JS text readed knows this chunk will be special when inserting into DOM.
    """
    to_download = [fi for fi in req_to_args.field_infos if fi.generate_download_link]
    # important yield this block as one string so it pushed to client in one go.
    # so the whole block can be treated as html.
    lines = []
    lines.append('<!-- CLICK_WEB START FOOTER -->')
    if to_download:
        lines.append('<b>Result files:</b><br>')
        for fi in to_download:
            lines.append('<ul> ')
            lines.append(f'<li>{_build_relative_link(fi)}<br>')
            lines.append('</ul>')

    else:
        lines.append('<b>DONE</b>')
    lines.append('<!-- CLICK_WEB END FOOTER -->')
    html_str = '\n'.join(lines)
    yield html_str


def _build_relative_link(field_info):
    """Hack as url_for needed request context"""

    rel_file_path = Path(field_info.file_path).relative_to(click_web.OUTPUT_FOLDER)
    uri = f'/static/results/{rel_file_path.as_posix()}'
    return f'<a href="{uri}">{field_info.link_name}</a>'


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

            # must be called mostly for saving and preparing file output.
            fi.before_script_execute()

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

        self.form_type = parts[4]

        'The actual command line option (--debug)'
        self.cmd_opt = parts[5]

        self.generate_download_link = False

    def before_script_execute(self):
        pass

    def after_script_executed(self):
        pass

    def __str__(self):
        res = []
        res.append(f'key: {self.key}')
        res.append(f'key_cmd_index: {self.cmd_index}')
        res.append(f'parameter_index: {self.parameter_index}')
        res.append(f'option_type: {self.option_type}')
        res.append(f'type: {self.type}')
        res.append(f'form_type: {self.form_type}')
        res.append(f'cmd_opt: {self.cmd_opt}')
        return ', '.join(res)

    def __lt__(self, other):
        "Make class sortable"
        return (self.cmd_index, self.parameter_index) < (other.cmd_index, other.parameter_index)

    def __eq__(self, other):
        return self.key == other.key


class FieldFileInfo(FieldInfo):
    """
    Use for processing input fields of file type.
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
        self.link_name = f'{self.cmd_opt}.out'

        log.info(f'File mode for {self.key} is  {mode}')

    def before_script_execute(self):
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
    Used when file option is just for output and form posted it as hidden or text field.
    Just create a empty temp file to give it's path to command.
    """

    def __init__(self, key):
        super().__init__(key)
        if self.form_type == 'text':
            self.link_name = request.form[self.key]
            # set the postfix to name name provided from form
            # this way it will at least have the same extension when downloaded
            self.file_suffix = request.form[self.key]
        else:
            # hidden no preferred file name can be provided by user
            self.file_suffix = '.out'

    def save(self):
        name = secure_filename(self.key)

        fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=name, suffix=self.file_suffix)
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
