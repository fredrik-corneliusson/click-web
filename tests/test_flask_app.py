import pytest
from bs4 import BeautifulSoup


def test_get_index(app, client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'the root command' in resp.data


@pytest.mark.parametrize(
    'command_path, response_code, expected_msg, expected_form_ids',
    [
        ('/cli/simple-no-params-command', 200, b'<title>Simple-No-Params-Command</title>',
         ['0.0.flag.bool_flag.--debug']),
        ('/cli/command-with-option-and-argument', 200, b'<title>Command-With-Option-And-Argument</title>',
         ['0.0.flag.bool_flag.--debug', '1.0.option.text.--an-option', '1.1.argument.int.an-argument']),
        ('/cli/sub-group/a-sub-group-command', 200, b'<title>A-Sub-Group-Command</title>',
         ['0.0.flag.bool_flag.--debug']),
    ])
def test_get_command(command_path, response_code, expected_msg, expected_form_ids, app, client):
    resp = client.get(command_path)
    print(_get_form_ids(resp.data))
    assert resp.status_code == response_code
    assert expected_msg in resp.data
    assert expected_form_ids == _get_form_ids(resp.data)


def _get_form_ids(html):
    soup = BeautifulSoup(html, 'html.parser')
    form_ids = [elem['id'] for elem in soup.find_all('input')]
    return form_ids


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
        ({'0.0.flag.bool_flag.--debug': None,
          '1.0.option.text.--an-option': None,
          '1.1.argument.int.an-argument': None
          },
         b'Ran command with option: option_value argument 10'),
        ({'0.0.flag.bool_flag.--debug': None,
          '1.0.option.text.--an-option': None,
          '1.1.argument.int.an-argument': 123
          },
         b'Ran command with option: option_value argument 123'),
        ({'0.0.flag.bool_flag.--debug': None,
          '1.0.option.text.--an-option': 'ABC',
          '1.1.argument.int.an-argument': 123
          },
         b'Ran command with option: ABC argument 123'),

    ])
def test_exec_with_arg_and_default_opt(form_data, expected_msg, app, client):
    resp = client.post('/cli/command-with-option-and-argument',
                       data=form_data)
    assert resp.status_code == 200
    assert expected_msg in resp.data
