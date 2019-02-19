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

        ('/cli/command-with-flag-without-off-option', 200, b'>Command-With-Flag-Without-Off-Option</',
         [
             '0.0.flag.bool_flag.checkbox.--debug',
             '1.0.flag.bool_flag.checkbox.--flag']),
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
