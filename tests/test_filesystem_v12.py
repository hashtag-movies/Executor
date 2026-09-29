import pytest
from executor.body import HashtagBody


def approve_once(body, operation, resource, purpose="test"):
    pending = body.permissions.pending()
    assert pending
    req = next(r for r in pending if r.operation == operation and r.resource == resource)
    from executor.permissions import PermissionDecision, PermissionScope
    body.permissions.decide(req.request_id, PermissionDecision(True, PermissionScope.ONCE, purpose))


def test_list_search_read(tmp_path):
    (tmp_path / "hello.txt").write_text("Hello from Hashtag Body", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("another file", encoding="utf-8")
    body = HashtagBody()
    args = {"path": str(tmp_path), "roots": [str(tmp_path)]}
    with pytest.raises(PermissionError):
        body.dispatch("filesystem.list", args)
    approve_once(body, "filesystem.list", str(tmp_path))
    listed = body.dispatch("filesystem.list", args)
    assert listed["count"] == 2
    assert any(x["name"] == "hello.txt" for x in listed["entries"])

    search_args = {"root": str(tmp_path), "roots": [str(tmp_path)], "name": "hello"}
    with pytest.raises(PermissionError):
        body.dispatch("filesystem.search", search_args)
    approve_once(body, "filesystem.search", str(tmp_path))
    found = body.dispatch("filesystem.search", search_args)
    assert found["count"] == 1
    assert found["results"][0]["name"] == "hello.txt"

    read_args = {"path": str(tmp_path / "hello.txt"), "roots": [str(tmp_path)]}
    with pytest.raises(PermissionError):
        body.dispatch("filesystem.read", read_args)
    approve_once(body, "filesystem.read", str(tmp_path / "hello.txt"))
    content = body.dispatch("filesystem.read", read_args)
    assert content["text"] == "Hello from Hashtag Body"


def test_manifest_has_v12_filesystem_capabilities():
    caps = HashtagBody().capabilities()["capabilities"]
    assert "filesystem.list" in caps
    assert "filesystem.search" in caps
