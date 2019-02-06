import pytest
from bs4 import BeautifulSoup


def test_get_index(app, client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'the root command' in resp.data


@pytest.mark.parametrize(
    'command_path, response_code, expected_msg, expected_form_ids',
    [
        ('/cli/simple-no-params-command', 200, b'>Simple-No-Params-Command</',
         [
             '0.0.flag.bool_flag.checkbox.--debug'
         ]),
        ('/cli/unicode-test', 200, 'Åäö'.encode('utf-8'),
         [
             '0.0.flag.bool_flag.checkbox.--debug',
             '1.0.option.choice.option.--unicode-msg'
         ]
         ),
        ('/cli/command-with-option-and-argument', 200, b'>Command-With-Option-And-Argument</',
         [
             '0.0.flag.bool_flag.checkbox.--debug',
             '1.0.option.text.text.--an-option',
             '1.1.argument.int.number.an-argument'
         ]),
        ('/cli/sub-group/a-sub-group-command', 200, b'>A-Sub-Group-Command</',
         [
             '0.0.flag.bool_flag.checkbox.--debug'
         ]),
        ('/cli/command-with-input-folder', 200, b'>Command-With-Input-Folder</',
         [
             '0.0.flag.bool_flag.checkbox.--debug',
             '1.0.argument.path[r].file.folder'
         ]),
        ('/cli/command-with-output-folder', 200, b'>Command-With-Output-Folder</',
         [
             '0.0.flag.bool_flag.checkbox.--debug',
             '1.0.argument.path[w].hidden.folder']),
    ]
)
def test_get_command(command_path, response_code, expected_msg, expected_form_ids, app, client):
    resp = client.get(command_path)
    form_ids = _get_form_ids(resp.data)
    print(form_ids)
    print(resp.data)
    assert resp.status_code == response_code
    assert expected_msg in resp.data
    assert expected_form_ids == form_ids


def _get_form_ids(html):
    soup = BeautifulSoup(html, 'html.parser')
    form_ids = [elem['name'] for elem in soup.find_all(['input', 'select'])]
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
        ({'0.0.flag.bool_flag.checkbox.--debug': None,
          '1.0.option.text.text.--an-option': None,
          '1.1.argument.int.number.an-argument': 321
          },
         b'Ran command with option: option_value argument 321'),
        ({'0.0.flag.bool_flag.checkbox.--debug': None,
          '1.0.option.text.text.--an-option': 'ABC',
          '1.1.argument.int.number.an-argument': 321
          },
         b'Ran command with option: ABC argument 321'),

    ])
def test_exec_with_arg_and_default_opt(form_data, expected_msg, app, client):
    resp = client.post('/cli/command-with-option-and-argument',
                       data=form_data)
    assert resp.status_code == 200
    print(resp.data)
    assert expected_msg in resp.data
