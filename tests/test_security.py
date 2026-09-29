import pytest
from executor.security import SecurityError, ensure_path_allowed

def test_path_outside_root_blocked(tmp_path):
    with pytest.raises(SecurityError): ensure_path_allowed(str(tmp_path.parent), [str(tmp_path)])

def test_path_inside_root_allowed(tmp_path):
    assert ensure_path_allowed(str(tmp_path), [str(tmp_path)]) == tmp_path.resolve()
