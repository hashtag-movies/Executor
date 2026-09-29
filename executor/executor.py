"""High-level read-only Executor operations for V1."""
from .github import GitHubClient
class HashtagExecutor:
    def __init__(self, github: GitHubClient): self.github = github
    def inspect_repository(self, owner: str, repo: str) -> dict:
        r = self.github.get_repository(owner, repo)
        return {k: r.get(k) for k in ("full_name", "default_branch", "private", "description", "language", "updated_at")}
    def inspect_root(self, owner: str, repo: str): return self.github.list_files(owner, repo)
