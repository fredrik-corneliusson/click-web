def test_get_index(app, client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'the root command' in resp.data

def test_get_command(app, client):
    resp = client.get('/cli/simple-no-params-command')
    assert resp.status_code == 200
    assert b'<title>Simple-No-Params-Command</title>' in resp.data

def test_exec_command(app, client):
    resp = client.post('/exec/cli/simple-no-params-command')
    assert resp.status_code == 200
    assert b'Simpel noparams command called' in resp.data
