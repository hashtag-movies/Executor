from executor.permissions import PermissionEngine, PermissionDecision, PermissionScope, PermissionRequest

def test_default_deny_creates_pending():
    p = PermissionEngine()
    req = PermissionRequest("filesystem.read", "C:/x", "test")
    assert not p.request(req).allowed
    assert p.pending()[0].request_id == req.request_id

def test_scoped_approval():
    p = PermissionEngine(lambda req: PermissionDecision(True, PermissionScope.TASK, "approved"))
    req = PermissionRequest("filesystem.read", "C:/x", "test", task_id="t1")
    assert p.request(req).allowed
    assert p.request(req).allowed

def test_explicit_pending_decision():
    p = PermissionEngine()
    req = PermissionRequest("filesystem.read", "C:/x", "test")
    p.request(req)
    p.decide(req.request_id, PermissionDecision(True, PermissionScope.OPERATION, "user approved"))
    assert p.request(req).allowed
