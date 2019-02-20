import pytest


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
