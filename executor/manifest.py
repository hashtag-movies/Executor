"""Hashtag Executor Body manifest V1.3 / G9-S8 local repository support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BodyManifest:
    body_id: str = "hashtag-executor"
    name: str = "Hashtag the Executor"
    protocol_version: str = "1.1"
    version: str = "1.3.0"

    capabilities: tuple[str, ...] = (
        "filesystem.inspect",
        "filesystem.list",
        "filesystem.search",
        "filesystem.read",
        "filesystem.write",
        "filesystem.create",
        "filesystem.move",
        "filesystem.copy",
        "filesystem.delete",
        "terminal.inspect",
        "terminal.execute",
        "process.inspect",
        "tests.run",
        "git.inspect",
        "git.modify",
        "github.read",
        "github.search",
        "github.repository.inspect",
        "github.files.list",
        "github.file.read",
        "github.file.write",
        "github.file.fix",
        "github.repositories.list",
        "github.branches.list",
        "github.branch.inspect",
        "github.branch.create",
        "github.commits.list",
        "github.commit.create",
        "github.pull_request.create",
        "github.backup.zip",
        "github.file.delete",
        "github.auth.status",
        "github.auth.login",
        "repository.identify",
        "repository.inspect",
        "repository.list_files",
        "repository.read_file",
        "repository.search",
        "repository.write_file",
        "repository.backup_zip",
        "repository.delete_file",
        "repository.run_tests",
        "repository.list_branches",
        "repository.inspect_branch",
        "repository.list_history",
        "repository.create_branch",
        "repository.create_pull_request",
        "github.sync_path",
        "repository.sync_path",
        "github.upload_path",
        "repository.upload_path",
        "github.deploy_core",
        "repository.deploy_core",
    )

    def to_dict(self) -> dict:
        caps = set(self.capabilities)
        try:
            from .dynamic_capabilities import dynamic_registry
            caps.update(dynamic_registry.list_capabilities())
        except Exception:
            pass
        return {
            "body_id": self.body_id,
            "name": self.name,
            "protocol_version": self.protocol_version,
            "version": self.version,
            "capabilities": sorted(list(caps)),
        }

