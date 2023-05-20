import logging
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import List, Union

from flask import Response, request
from werkzeug.utils import secure_filename

import click_web

from .input_fields import FieldId

logger: Union[logging.Logger, None] = None

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


class Executor:
    def __init__(self):
        self.returncode = None
        self._command_line = None

    def exec(self, command_path):
        """
        Execute the command and stream the output from it as response
        :param command_path:
        """
        global logger
        logger = click_web.logger

        root_command, *commands = command_path.split('/')
        self._command_line = CommandLine(click_web.script_file, commands)

        def _generate_output():
            yield self._create_cmd_header(commands)
            try:
                yield from self._run_script_and_generate_stream()
            except Exception as e:
                # exited prematurely, show the error to user
                yield f"\nERROR: Got exception when reading output from script: {type(e)}\n"
                yield traceback.format_exc()
                raise

            yield from self._create_result_footer()

        return Response(_generate_output(), mimetype='text/plain')

    def _run_script_and_generate_stream(self):
        """
        Execute the command the via Popen and yield output
        """
        logger.info('Executing: %s', self._command_line.get_commandline(obfuscate=True))
        if not os.environ.get('PYTHONIOENCODING'):
            # Fix unicode on windows
            os.environ['PYTHONIOENCODING'] = 'UTF-8'

        process = subprocess.Popen(self._command_line.get_commandline(),
                                   shell=False,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        logger.info('script running Pid: %d', process.pid)

        encoding = sys.getdefaultencoding()
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                yield line.decode(encoding)

        process.wait()  # wait for the subprocess to exit
        self.returncode = process.returncode
        logger.info(f'script finished Pid: {process.pid} Return code: {process.returncode}')

        self._command_line.after_script_executed()

    def _create_cmd_header(self, commands: List['CmdPart']):
        """
        Generate a command header.
        Note:
            here we always allow to generate HTML as long as we have it between CLICK-WEB comments.
            This way the JS frontend can insert it in the correct place in the DOM.
        """

        def generate():
            yield '<!-- CLICK_WEB START HEADER -->'
            yield '<div class="command-line">Executing: {}</div>'.format('/'.join(str(c) for c in commands))
            yield '<!-- CLICK_WEB END HEADER -->'

        # important yield this block as one string so it pushed to client in one go.
        # so the whole block can be treated as html.
        html_str = '\n'.join(generate())
        return html_str

    def _create_result_footer(self):
        """
        Generate a footer.
        Note:
            here we always allow to generate HTML as long as we have it between CLICK-WEB comments.
            This way the JS frontend can insert it in the correct place in the DOM.
        """
        # important yield this block as one string so it pushed to client in one go.
        # This is so the whole block can be treated as html if JS frontend.
        to_download = self._command_line.get_download_field_infos()
        lines = ['<!-- CLICK_WEB START FOOTER -->']
        if to_download:
            lines.append('<b>Result files:</b><br>')
            for fi in to_download:
                lines.append('<ul> ')
                lines.append(f'<li>{_get_download_link(fi)}<br>')
                lines.append('</ul>')

        if self.returncode == 0:
            lines.append('<div class="script-exit script-exit-ok">Done</div>')
        else:
            lines.append(f'<div class="script-exit script-exit-error">'
                         f'Script exited with error code: {self.returncode}</div>')

        lines.append('<!-- CLICK_WEB END FOOTER -->')
        html_str = '\n'.join(lines)
        yield html_str


def _get_download_link(field_info):
    """Hack as url_for need request context"""

    rel_file_path = Path(field_info.file_path).relative_to(click_web.OUTPUT_FOLDER)
    uri = f'/static/results/{rel_file_path.as_posix()}'
    return f'<a href="{uri}">{field_info.link_name}</a>'


class CommandLine:
    def __init__(self, script_file_path: str, commands: List[str]):
        self._parts: List[CmdPart] = list()
        self.append(_get_python_interpreter())
        self.append(script_file_path)

        self.command_line_bulder = FormToCommandLineBuilder(self)

        # root command_index should not add a command
        self.command_line_bulder.add_command_args(0)
        for i, command in enumerate(commands):
            self.append(command)
            self.command_line_bulder.add_command_args(i + 1)

    def append(self, part: str, secret: bool = False):
        self._parts.append(CmdPart(part, secret))

    def get_commandline(self, obfuscate: bool = False) -> List[str]:
        """
        Return command line as a list of strings.
        obfuscate - if True secret parts like passwords are replaced with *****. Use for logging etc.
        """
        return ['******' if cmd_part.secret and obfuscate else str(cmd_part)
                for cmd_part in self._parts]

    def get_download_field_infos(self):
        return [fi for fi in self.command_line_bulder.field_infos
                if fi.generate_download_link and fi.link_name]

    def after_script_executed(self):
        """Call this after the command has executed"""
        for fi in self.command_line_bulder.field_infos:
            fi.after_script_executed()


def _get_python_interpreter():
    if sys.executable.endswith("uwsgi"):
        import uwsgi
        python_interpreter = str((Path(uwsgi.opt.get("virtualenv").decode()) / "bin" / "python").absolute())
    else:
        # run with same python executable we are running with.
        python_interpreter = sys.executable
    return python_interpreter


class CmdPart:
    def __init__(self, part: str, secret=False):
        self.part = part
        self.secret = secret

    def __str__(self):
        return self.part


class FormToCommandLineBuilder:

    def __init__(self, command_line: CommandLine):
        self.command_line = command_line
        field_infos = [FieldInfo.factory(key) for key in list(request.form.keys()) + list(request.files.keys())]
        # important to sort them so they will be in expected order on command line
        self.field_infos = list(sorted(field_infos))

    def add_command_args(self, command_index: int):
        """
        Convert the post request into a list of command line arguments

        :param command_index: (int) the index for the command to get arguments for.
        """

        # only include relevant fields for this command index
        commands_field_infos = [fi for fi in self.field_infos if fi.param.command_index == command_index]
        commands_field_infos = sorted(commands_field_infos)

        for fi in commands_field_infos:

            # must be called mostly for saving and preparing file output.
            fi.before_script_execute()

            if self._is_option(fi.cmd_opt):
                self._process_option(fi)
            else:
                # argument(s)
                if isinstance(fi, FieldFileInfo):
                    # it's a file, append the written temp file path
                    # TODO: does file upload support multiple keys? In that case support it.
                    self.command_line.append(fi.file_path)
                else:
                    arg_values = request.form.getlist(fi.key)
                    has_values = bool(''.join(arg_values))
                    # If arg value is empty the field was not filled, and thus optional argument
                    if has_values:
                        if fi.param.nargs == -1:
                            # Variadic argument, in html form each argument is a separate line in a textarea.
                            # treat each line we get from text area as a separate argument.
                            for value in arg_values:
                                values = value.splitlines()
                                for val in values:
                                    self.command_line.append(val, secret=fi.param.form_type == 'password')
                        else:
                            for val in arg_values:
                                self.command_line.append(val, secret=fi.param.form_type == 'password')

    @staticmethod
    def _is_option(cmd_option):
        return isinstance(cmd_option, str) and \
            (cmd_option.startswith('--') or cmd_option.startswith('-'))

    def _process_option(self, field_info):
        vals = request.form.getlist(field_info.key)
        if field_info.is_file:
            if field_info.link_name:
                # it's a file, append the file path
                self.command_line.append(field_info.cmd_opt)
                self.command_line.append(field_info.file_path)
        elif field_info.param.param_type == 'flag':
            # To work with flag that is default True a hidden field with same name is also sent by form.
            # This is to detect if checkbox was not checked as then we will get the field anyway with the "off flag"
            # as value.
            if len(vals) == 1:
                off_flag = vals[0]
                flag_on_cmd_line = off_flag
            else:
                # we got both off and on flags, checkbox is checked.
                on_flag = vals[1]
                flag_on_cmd_line = on_flag

            self.command_line.append(flag_on_cmd_line)
        elif ''.join(vals):
            # opt with value, if option was given multiple times get the values for each.
            # flag options should always be set if we get them
            # for normal options they must have a non empty value
            self.command_line.append(field_info.cmd_opt)
            for val in vals:
                if val:
                    self.command_line.append(val, secret=field_info.param.form_type == 'password')
        else:
            # option with empty values, should not be added to command line.
            pass


class FieldInfo:
    """
    Extract information from the encoded form input field name
    the parts:
        [command_index].[opt_or_arg_index].[click_type].[html_input_type].[opt_or_arg_name]
    e.g.
        "0.0.option.text.text.--an-option"
        "0.1.argument.file[rb].text.an-argument"
    """

    @staticmethod
    def factory(key):
        field_id = FieldId.from_string(key)
        is_file = field_id.click_type.startswith('file')
        is_path = field_id.click_type.startswith('path')
        is_uploaded = key in request.files
        if is_file:
            if is_uploaded:
                field_info = FieldFileInfo(field_id)
            else:
                field_info = FieldOutFileInfo(field_id)
        elif is_path:
            if is_uploaded:
                field_info = FieldPathInfo(field_id)
            else:
                field_info = FieldPathOutInfo(field_id)
        else:
            field_info = FieldInfo(field_id)
        return field_info

    def __init__(self, param: FieldId):
        self.param = param
        self.key = param.key

        'Type of option (file, text)'
        self.is_file = self.param.click_type.startswith('file')

        'The actual command line option (--debug)'
        self.cmd_opt = param.name

        self.generate_download_link = False

    def before_script_execute(self):
        pass

    def after_script_executed(self):
        pass

    def __str__(self):
        return str(self.param)

    def __lt__(self, other):
        # Make class sortable
        return (self.param.command_index, self.param.param_index) < \
            (other.param.command_index, other.param.param_index)

    def __eq__(self, other):
        return self.key == other.key


class FieldFileInfo(FieldInfo):
    """
    Use for processing input fields of file type.
    Saves the posted data to a temp file.
    """
    'temp dir is on class in order to be uniqe for each request'
    _temp_dir = None

    def __init__(self, fimeta):
        super().__init__(fimeta)
        # Extract the file mode that is in the type e.g file[rw]
        self.mode = self.param.click_type.split('[')[1][:-1]
        self.generate_download_link = True if 'w' in self.mode else False
        self.link_name = f'{self.cmd_opt}.out'
        self.file_path = None

        logger.info(f'File mode for {self.key} is {self.mode}')

    def before_script_execute(self):
        self.save()

    @classmethod
    def temp_dir(cls):
        if not cls._temp_dir:
            cls._temp_dir = tempfile.mkdtemp(dir=click_web.OUTPUT_FOLDER)
        logger.info(f'Temp dir: {cls._temp_dir}')
        return cls._temp_dir

    def save(self):
        logger.info('Saving...')

        logger.info('field value is a file! %s', self.key)
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
            logger.info(f'Saving {self.key} to {filename}')
            file.save(filename)

    def __str__(self):
        res = [super().__str__(), f'file_path: {self.file_path}']
        return ', '.join(res)


class FieldOutFileInfo(FieldFileInfo):
    """
    Used when file option is just for output and form posted it as hidden or text field.
    Just create a empty temp file to give it's path to command.
    """

    def __init__(self, fimeta):
        super().__init__(fimeta)
        if self.param.form_type == 'text':
            self.link_name = request.form[self.key]
            # set the postfix to name provided from form
            # this way it will at least have the same extension when downloaded
            self.file_suffix = request.form[self.key]
        else:
            # hidden no preferred file name can be provided by user
            self.file_suffix = '.out'

    def save(self):
        name = secure_filename(self.key)

        fd, filename = tempfile.mkstemp(dir=self.temp_dir(), prefix=name, suffix=self.file_suffix)
        logger.info(f'Creating empty file for {self.key} as {filename}')
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

        logger.info(f'Extracting: {self.file_path} to {zip_extract_dir}')
        shutil.unpack_archive(self.file_path, zip_extract_dir, 'zip')
        self.file_path = zip_extract_dir

    def after_script_executed(self):
        super().after_script_executed()
        self.file_path = zip_folder(self.file_path, self.temp_dir(), out_prefix=self.key)
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
        self.file_path = zip_folder(self.file_path, self.temp_dir(), out_prefix=self.key)
        self.generate_download_link = True


def zip_folder(folder_path, out_folder, out_prefix):
    fd, out_base_name = tempfile.mkstemp(dir=out_folder, prefix=out_prefix)
    logger.info(f'Zipping {folder_path}')
    zip_file_path = shutil.make_archive(out_base_name, 'zip', folder_path)
    logger.info(f'Zip file created {zip_file_path}')
    return zip_file_path
