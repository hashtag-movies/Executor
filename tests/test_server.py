from fastapi.testclient import TestClient
from executor.server import app, body

def test_permission_endpoints():
    body.permissions.revoke_all()
    c = TestClient(app)
    r = c.post('/v1/body/execute', json={'operation':'filesystem.inspect','arguments':{'path':'C:/Hashtag-Test','roots':['C:/Hashtag-Test']}})
    assert r.status_code == 200
    d = r.json(); assert d['status'] == 'permission_required'
    rid = d['permission_request']['request_id']
    r = c.post('/v1/body/permissions/decide', json={'request_id':rid,'allowed':True,'scope':'once'})
    assert r.status_code == 200
    r = c.post('/v1/body/execute', json={'operation':'filesystem.inspect','arguments':{'path':'C:/Hashtag-Test','roots':['C:/Hashtag-Test']}})
    assert r.status_code == 200
    assert r.json()['status'] == 'success'
