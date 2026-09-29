import pytest
from executor.body import HashtagBody

def test_manifest():
    caps = HashtagBody().capabilities()
    assert caps["body_id"] == "hashtag-executor"
    assert "filesystem.read" in caps["capabilities"]

def test_read_requires_permission(tmp_path):
    f = tmp_path / "x.txt"; f.write_text("hello", encoding="utf-8")
    with pytest.raises(PermissionError):
        HashtagBody().dispatch("filesystem.read", {"path": str(f), "roots": [str(tmp_path)]})
