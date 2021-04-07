from collections import OrderedDict

import flask
import pytest

from click_web.resources.cmd_exec import RequestToCommandArgs

app = flask.Flask(__name__)


@pytest.mark.parametrize(
    'data, expected',
    [
        ({
             '0.0.option.text.1.text.--an-option': 'option-value',
             '0.1.option.text.1.text.--another-option': 'another-option-value',
             '1.0.option.text.1.text.--option-for-other-command': 'some value'
         }, (['--an-option', 'option-value', '--another-option', 'another-option-value'],
             ['--option-for-other-command', 'some value']),
        ), # noqa
        (OrderedDict((
                ('0.1.option.text.1.text.--another-option', 'another-option-value'),
                ('0.0.option.text.1.text.--an-option', 'option-value'),
                ('1.0.option.text.1.text.--option-for-other-command', 'some value')
        )), (['--an-option', 'option-value', '--another-option', 'another-option-value'],
             ['--option-for-other-command', 'some value']),
        ),
    ])
def test_form_post_to_commandline_arguments(data, expected):
    with app.test_request_context('/command', data=data):
        r = RequestToCommandArgs()
        for i, expect in enumerate(expected):
            assert r.command_args(i) == expected[i]
