from pathlib import Path

from executor.body import HashtagBody
from executor.permissions import PermissionDecision, PermissionScope
from executor.protocol import Operation


class AllowAllPermissions:
    def request(self, request):
        return PermissionDecision(True, PermissionScope.ONCE, "allowed")


class DenyUntilApproved:
    def __init__(self):
        from executor.permissions import PermissionEngine
        self.engine = PermissionEngine(auto_permit=False)

    def request(self, request):
        return self.engine.request(request)

    def pending(self):
        return self.engine.pending()

    def decide(self, request_id):
        return self.engine.decide(
            request_id,
            PermissionDecision(True, PermissionScope.ONCE, "approved"),
        )


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "Repository"
    (repo / "tests").mkdir(parents=True)

    (repo / "hello.py").write_text(
        "def add(a, b):\n"
        "    return a - b\n",
        encoding="utf-8",
    )

    (repo / "tests" / "test_hello.py").write_text(
        "from hello import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    return repo


def test_local_repository_read_maps_to_filesystem(tmp_path):
    repo = make_repo(tmp_path)
    body = HashtagBody(permissions=AllowAllPermissions())

    result = body.dispatch(
        "repository.read_file",
        {
            "repository": str(repo),
            "path": "hello.py",
        },
    )

    assert result["path"] == str(repo / "hello.py")
    assert "return a - b" in result["text"]


def test_local_repository_write_maps_to_filesystem_write(tmp_path):
    repo = make_repo(tmp_path)
    body = HashtagBody(permissions=AllowAllPermissions())

    result = body.dispatch(
        "repository.write_file",
        {
            "repository": str(repo),
            "path": "hello.py",
            "file_content": "def add(a, b):\n    return a + b\n",
        },
    )

    assert result["written"] is True
    assert (repo / "hello.py").read_text(encoding="utf-8") == (
        "def add(a, b):\n    return a + b\n"
    )


def test_local_repository_tests_run_through_tests_capability(tmp_path):
    repo = make_repo(tmp_path)
    body = HashtagBody(permissions=AllowAllPermissions())

    first = body.dispatch(
        "repository.run_tests",
        {"repository": str(repo)},
    )

    assert first["passed"] is False
    assert first["returncode"] != 0
    assert "FAILED" in first["stdout"]

    body.dispatch(
        "repository.write_file",
        {
            "repository": str(repo),
            "path": "hello.py",
            "file_content": "def add(a, b):\n    return a + b\n",
        },
    )

    second = body.dispatch(
        "repository.run_tests",
        {"repository": str(repo)},
    )

    assert second["passed"] is True
    assert second["returncode"] == 0


def test_local_repository_write_permission_pause_and_resume(tmp_path):
    repo = make_repo(tmp_path)
    permissions = DenyUntilApproved()
    body = HashtagBody(permissions=permissions)

    operation = Operation(
        operation="repository.write_file",
        arguments={
            "repository": str(repo),
            "path": "hello.py",
            "file_content": "def add(a, b):\n    return a + b\n",
        },
        reason="Fix the failing add function",
    )

    paused = body.execute(operation)

    assert paused.status == "permission_required"
    pending = permissions.pending()
    assert len(pending) == 1
    assert pending[0].operation == "filesystem.write"
    assert pending[0].resource == str(repo / "hello.py")

    permissions.decide(pending[0].request_id)

    completed = body.execute(operation)

    assert completed.status == "success"
    assert completed.audit["operation"] == "filesystem.write"
    assert "return a + b" in (repo / "hello.py").read_text(encoding="utf-8")

def test_local_repository_list_branches_permission_pause_and_resume(tmp_path):
    repo = make_repo(tmp_path)

    # Initialize a real Git repository so the operation has actual branches
    # to inspect.
    import shutil
    import subprocess

    git = shutil.which("git")
    if not git:
        raise RuntimeError(
            "Git executable is required for this test but was not found on PATH"
        )

    subprocess.run(
        [git, "init", "-b", "main", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [git, "-C", str(repo), "config", "user.email", "hashtag@test.local"],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [git, "-C", str(repo), "config", "user.name", "Hashtag Test"],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [git, "-C", str(repo), "add", "."],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [git, "-C", str(repo), "commit", "-m", "initial"],
        check=True,
        capture_output=True,
        text=True,
    )

    permissions = DenyUntilApproved()
    body = HashtagBody(permissions=permissions)

    operation = Operation(
        operation="repository.list_branches",
        arguments={
            "repository": str(repo),
            "provider": "local",
        },
        reason="List branches in the local repository",
    )

    paused = body.execute(operation)

    assert paused.status == "permission_required"

    pending = permissions.pending()
    assert len(pending) == 1
    assert pending[0].operation == "terminal.execute"
    assert str(repo) in pending[0].resource

    permissions.decide(pending[0].request_id)

    completed = body.execute(operation)

    assert completed.status == "success"
    assert completed.audit["operation"] == "local.git.list_branches"

    result = completed.result

    assert result["ok"] is True
    assert result["returncode"] == 0
    assert "main" in result["branches"]
