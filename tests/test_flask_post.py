import json

import pytest
from werkzeug.datastructures import MultiDict

from click_web.resources.cmd_exec import Executor


def test_exec_command(app, client):
    resp = client.post('/cli/simple-no-params-command')
    assert resp.status_code == 200
    assert b'Simpel noparams command called' in resp.data


def test_exec_sub_command(app, client):
    resp = client.post('/cli/sub-group/a-sub-group-command')
    assert resp.status_code == 200
    assert b'Sub group command called' in resp.data


def test_exec_default_arg_and_opt(app, client):
    resp = client.post('/cli/command-with-option-and-argument')
    assert resp.status_code == 200
    assert b'Ran command with option: option_value argument 10' in resp.data


@pytest.mark.parametrize(
    'form_data, expected_msg',
    [
        ({},
         b'Ran command with option: option_value argument 10'),

        ({
             '1.1.argument.int.1.number.an-argument': 321
         },
         b'Ran command with option: option_value argument 321'),

        ({'0.0.flag.bool_flag.1.checkbox.--debug': '--debug',
          '1.0.option.text.1.text.--an-option': 'ABC',
          '1.1.argument.int.1.number.an-argument': 321
          },
         b'Ran command with option: ABC argument 321')
    ])
def test_exec_with_arg_and_default_opt(form_data, expected_msg, app, client):
    resp = client.post('/cli/command-with-option-and-argument',
                       data=form_data)
    assert resp.status_code == 200
    print(resp.data)
    assert expected_msg in resp.data


@pytest.mark.parametrize(
    'form_data, expected_msg',
    [
        ({'1.0.flag.bool_flag.1.checkbox.--flag': '--flag'},
         b'Ran command with flag True'),

        # if it was not set we also send it down as a hidden field with turn off flag as value
        ({'1.0.flag.bool_flag.1.checkbox.--flag': '--no-flag'},
         b'Ran command with flag False'),

    ])
def test_exec_with_default_on_flag_option(form_data, expected_msg, app, client):
    resp = client.post('/cli/command-with-default-on-flag-option',
                       data=form_data)
    assert resp.status_code == 200
    print(resp.data)
    assert expected_msg in resp.data


@pytest.mark.parametrize(
    'form_data, expected_msg',
    [
        ({},
         b'Ran command with option: None'),

        (MultiDict([('1.0.option.text.2.text.--an-option', 'a'),
                    ('1.0.option.text.2.text.--an-option', 'b')]),
         b"Ran command with option: (\'a\', \'b\')"),

        (MultiDict([('1.0.option.text.2.text.--an-option', 'a')]),
         b"Error: Option \'--an-option\' requires 2 arguments."),

        (MultiDict([('1.0.option.text.2.text.--an-option', 'a'),
                    ('1.0.option.text.2.text.--an-option', 'b'),
                    ('1.0.option.text.2.text.--an-option', 'c')]),
         b"Got unexpected extra argument (c)"),

    ])
def test_exec_with_nargs_opts(form_data, expected_msg, app, client):
    resp = client.post('/cli/command-with-nargs-option',
                       data=form_data)
    assert resp.status_code == 200
    print(resp.data)
    assert expected_msg in resp.data


@pytest.mark.parametrize(
    'form_data, expected_msg',
    [
        ({},
         b'Executing: command-with-variadic-args'),

        ({
             '1.1.argument.int.-1.number.an-argument': 'line 1'
         },
         b'Hi line 1, you are number 1'),

        ({
             '1.1.argument.int.-1.number.an-argument': 'line 1\nline 2'
         },
         b'line 2, you are number 2'),

    ])
def test_exec_with_variadic_args(form_data, expected_msg, app, client):
    resp = client.post('/cli/command-with-variadic-args',
                       data=form_data)
    assert resp.status_code == 200
    print(resp.data)
    assert expected_msg in resp.data


@pytest.mark.parametrize(
    'data, expected_msg',
    [
        ('command-with-option-and-argument',
         b'Ran command with option: option_value argument 10'),

        ("command-with-option-and-argument 11",
         b'Ran command with option: option_value argument 11'),

        ("--debug command-with-option-and-argument --an-option ABC 12",
         b'Ran command with option: ABC argument 12')
    ])
def test_rawcmd_exec_with_arg_and_default_opt(data, expected_msg, app, client):
    """
    Test of the giving raw command line.
    """
    resp = client.post('/' + Executor.RAW_CMD_PATH, data=data)
    assert resp.status_code == 200
    assert resp.content_type == 'text/plain; charset=utf-8'
    assert expected_msg in resp.data
    last_line = resp.data.splitlines()[-1]
    assert json.loads(last_line) == {"result": "OK", "returncode": 0, "message": "Done"}
