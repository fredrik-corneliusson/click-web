import pytest
from werkzeug.datastructures import MultiDict


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
         b'Ran command with option: ()'),

        (MultiDict([('1.0.option.text.2.text.--an-option', 'a'),
                    ('1.0.option.text.2.text.--an-option', 'b')]),
         b"Ran command with option: (&#x27;a&#x27;, &#x27;b&#x27;)"),

        (MultiDict([('1.0.option.text.2.text.--an-option', 'a')]),
         b"Error: --an-option option requires 2 arguments"),

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
         b'<pre class="script-output">'),

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
