from executor.body import HashtagBody
from executor.permissions import (
    PermissionEngine,
    PermissionDecision,
    PermissionScope,
)
from executor.protocol import Operation


class FakeGitHubClient:
    """Fake GitHub API used for safe local tests."""

    def __init__(self):
        self.calls = []

    def get_repository(self, owner, repo):
        self.calls.append(
            ("get_repository", owner, repo)
        )
        return {
            "full_name": f"{owner}/{repo}",
            "default_branch": "main",
        }

    def get_file_text(
        self,
        owner,
        repo,
        path,
        ref=None,
    ):
        self.calls.append(
            (
                "get_file_text",
                owner,
                repo,
                path,
                ref,
            )
        )
        return "hello from github"

    def write_file(
        self,
        owner,
        repo,
        path,
        content,
        message,
        branch="main",
        sha=None,
    ):
        self.calls.append(
            (
                "write_file",
                owner,
                repo,
                path,
                content,
                message,
                branch,
                sha,
            )
        )

        return {
            "content": {
                "path": path,
            },
            "commit": {
                "message": message,
            },
        }

    def create_branch(
        self,
        owner,
        repo,
        branch,
        from_branch="main",
    ):
        self.calls.append(
            (
                "create_branch",
                owner,
                repo,
                branch,
                from_branch,
            )
        )

        return {
            "ref": f"refs/heads/{branch}",
        }

    def create_pull_request(
        self,
        owner,
        repo,
        title,
        head,
        base="main",
        body="",
    ):
        self.calls.append(
            (
                "create_pull_request",
                owner,
                repo,
                title,
                head,
                base,
                body,
            )
        )

        return {
            "number": 1,
            "title": title,
        }


def approve_pending(
    permissions,
    scope=PermissionScope.ONCE,
):
    pending = permissions.pending()

    assert len(pending) == 1

    request = pending[0]

    permissions.decide(
        request.request_id,
        PermissionDecision(
            True,
            scope,
            "approved for test",
        ),
    )


def test_github_repository_inspect_requires_permission():
    permissions = PermissionEngine()
    github = FakeGitHubClient()

    body = HashtagBody(
        permissions=permissions,
        github_client=github,
    )

    operation = Operation(
        operation="github.repository.inspect",
        arguments={
            "owner": "hashtag-movies",
            "repo": "Hashtag-core",
        },
        reason="Inspect repository",
    )

    result = body.execute(operation)

    assert result.status == "permission_required"
    assert github.calls == []
    assert len(permissions.pending()) == 1

    approve_pending(permissions)

    result = body.execute(operation)

    assert result.status == "success"

    assert (
        result.result["full_name"]
        == "hashtag-movies/Hashtag-core"
    )

    assert github.calls == [
        (
            "get_repository",
            "hashtag-movies",
            "Hashtag-core",
        )
    ]


def test_github_file_read_uses_permission_gate():
    permissions = PermissionEngine()
    github = FakeGitHubClient()

    body = HashtagBody(
        permissions=permissions,
        github_client=github,
    )

    operation = Operation(
        operation="github.file.read",
        arguments={
            "owner": "hashtag-movies",
            "repo": "Hashtag-core",
            "path": "VERSION.txt",
            "ref": "main",
        },
        reason="Read the Core version",
    )

    result = body.execute(operation)

    assert result.status == "permission_required"
    assert github.calls == []

    approve_pending(permissions)

    result = body.execute(operation)

    assert result.status == "success"
    assert result.result["text"] == "hello from github"

    assert github.calls == [
        (
            "get_file_text",
            "hashtag-movies",
            "Hashtag-core",
            "VERSION.txt",
            "main",
        )
    ]


def test_github_file_write_requires_permission_before_api_call():
    permissions = PermissionEngine()
    github = FakeGitHubClient()

    body = HashtagBody(
        permissions=permissions,
        github_client=github,
    )

    operation = Operation(
        operation="github.file.write",
        arguments={
            "owner": "hashtag-movies",
            "repo": "Hashtag-core",
            "path": "TEST.txt",
            "content": "test",
            "message": "Test commit",
            "branch": "test-branch",
        },
        reason="Modify a test file",
    )

    result = body.execute(operation)

    assert result.status == "permission_required"
    assert github.calls == []

    approve_pending(permissions)

    result = body.execute(operation)

    assert result.status == "success"

    assert github.calls == [
        (
            "write_file",
            "hashtag-movies",
            "Hashtag-core",
            "TEST.txt",
            "test",
            "Test commit",
            "test-branch",
            None,
        )
    ]