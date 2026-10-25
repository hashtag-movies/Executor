"""GitHub execution client for Hashtag the Executor Body V1.4.

This module contains GitHub API mechanics only.

Planning, learning, verification, and approval decisions remain
responsibilities of Hashtag Core and the Body permission layer.
"""

from __future__ import annotations

import base64
import logging
import time
from typing import Any, Callable, Optional

import requests

logger = logging.getLogger("executor.github")


class TokenBucketRateLimiter:
    """Token bucket rate limiter for GitHub API.

    GitHub allows 5000 requests/hour for authenticated users.
    We use a conservative 4500/hour = 1.25 req/sec baseline.
    Burst allowance handles short spikes.
    """

    def __init__(
        self,
        rate_per_hour: int = 4500,
        burst: int = 50,
    ):
        self.rate_per_second = rate_per_hour / 3600.0
        self.burst = burst
        self.tokens = float(burst)
        self.last_update = time.monotonic()
        self._lock = __import__("threading").Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate_per_second)
        self.last_update = now

    def acquire(self, tokens: int = 1, timeout: float = 30.0) -> bool:
        """Acquire tokens, blocking until available or timeout."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
            time.sleep(0.05)
        return False

    def update_from_headers(self, headers: dict[str, str]) -> None:
        """Update bucket state from GitHub rate limit headers."""
        try:
            remaining = headers.get("X-RateLimit-Remaining")
            reset = headers.get("X-RateLimit-Reset")
            limit = headers.get("X-RateLimit-Limit")

            if remaining is not None and reset is not None:
                with self._lock:
                    # If we're close to limit, throttle more aggressively
                    rem = int(remaining)
                    if rem < 100:
                        # Reduce token generation rate
                        self.rate_per_second = max(0.1, self.rate_per_second * 0.5)
                    elif rem > 1000:
                        # Restore normal rate
                        self.rate_per_second = 4500 / 3600.0

                    # If reset time is in the future, calculate tokens from reset
                    reset_ts = int(reset)
                    now_ts = int(time.time())
                    if reset_ts > now_ts:
                        seconds_to_reset = reset_ts - now_ts
                        self.tokens = min(self.burst, rem * 0.8)
        except Exception:
            pass  # Best effort only


class GitHubClient:
    """GitHub REST API client used by the Executor Body."""

    # Retry configuration
    MAX_RETRIES = 3
    BASE_BACKOFF = 1.0  # seconds
    MAX_BACKOFF = 30.0
    RETRYABLE_STATUS = {429, 500, 502, 503, 504}

    def __init__(
        self,
        token: str,
        api_url: str = "https://api.github.com",
        timeout: int = 30,
        rate_limiter: Optional[TokenBucketRateLimiter] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter()

        self.token = str(token).strip() if token else ""
        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

        if token:
            self.session.headers["Authorization"] = (
                f"Bearer {token}"
            )

    # ------------------------------------------------------------------
    # Internal HTTP helpers with rate limiting & retry/backoff
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.api_url}/{path.lstrip('/')}"

    def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> requests.Response:
        """Execute HTTP request with rate limiting and exponential backoff retry."""
        url = self._url(path)

        # Acquire rate limit token before request
        if not self.rate_limiter.acquire(timeout=30.0):
            raise RuntimeError("Rate limiter timeout: unable to acquire token")

        last_exception = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )

                # Update rate limiter from response headers
                self.rate_limiter.update_from_headers(response.headers)

                # Check for retryable status codes
                if response.status_code in self.RETRYABLE_STATUS:
                    if attempt < self.MAX_RETRIES:
                        # Handle 429 with Retry-After header if present
                        if response.status_code == 429:
                            retry_after = response.headers.get("Retry-After")
                            if retry_after:
                                try:
                                    wait_time = min(float(retry_after), self.MAX_BACKOFF)
                                except ValueError:
                                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                            else:
                                wait_time = self.BASE_BACKOFF * (2 ** attempt)
                        else:
                            wait_time = self.BASE_BACKOFF * (2 ** attempt)

                        # Add jitter
                        import random
                        wait_time *= (0.5 + random.random())
                        wait_time = min(wait_time, self.MAX_BACKOFF)

                        logger.warning(
                            "GitHub API %s %s (attempt %d/%d), backing off %.1fs",
                            response.status_code, url, attempt + 1, self.MAX_RETRIES, wait_time
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        response.raise_for_status()

                # Success - raise for other error codes (4xx except 429)
                response.raise_for_status()
                return response

            except requests.Timeout as exc:
                last_exception = exc
                if attempt < self.MAX_RETRIES:
                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                    logger.warning("GitHub API timeout (attempt %d/%d), retrying in %.1fs", attempt + 1, self.MAX_RETRIES, wait_time)
                    time.sleep(wait_time)
                    continue
            except requests.RequestException as exc:
                last_exception = exc
                if attempt < self.MAX_RETRIES:
                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                    logger.warning("GitHub API error: %s (attempt %d/%d), retrying in %.1fs", exc, attempt + 1, self.MAX_RETRIES, wait_time)
                    time.sleep(wait_time)
                    continue

        # All retries exhausted
        raise RuntimeError(f"GitHub API request failed after {self.MAX_RETRIES} retries: {last_exception}") from last_exception

    def _get(self, path: str) -> Any:
        response = self._request_with_retry("GET", path)
        return response.json()

    def _post(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> Any:
        response = self._request_with_retry("POST", path, json=payload)
        return response.json()

    def _put(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> Any:
        response = self._request_with_retry("PUT", path, json=payload)
        return response.json()

    def _delete(self, path: str) -> Any:
        response = self._request_with_retry("DELETE", path)
        return response.json()

    def _patch(self, path: str, payload: dict[str, Any]) -> Any:
        response = self._request_with_retry("PATCH", path, json=payload)
        return response.json()

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.api_url}/{path.lstrip('/')}"

    def _get(self, path: str) -> Any:
        response = self.session.get(
            self._url(path),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _post(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> Any:
        response = self.session.post(
            self._url(path),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _put(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> Any:
        response = self.session.put(
            self._url(path),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Read / inspect
    # ------------------------------------------------------------------

    def get_authenticated_user(self) -> dict[str, Any]:
        """Return the GitHub account associated with the token."""
        return self._get("user")

    def list_repositories(
        self,
        owner: str,
    ) -> list[dict[str, Any]]:
        """List repositories visible to a public owner."""
        return self._get(
            f"users/{owner}/repos?per_page=100"
        )

    def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        """Inspect repository metadata.

        GitHub's REST API returns ``owner`` as a nested user/org object.
        The Executor repository contract exposes repository identity fields
        in a stable scalar form, so normalize ``owner`` to its login/name
        string while preserving the rest of GitHub's metadata.
        """
        data = self._get(
            f"repos/{owner}/{repo}"
        )

        if not isinstance(data, dict):
            raise TypeError(
                "GitHub repository response must be a JSON object"
            )

        normalized = dict(data)

        github_owner = normalized.get("owner")
        if isinstance(github_owner, dict):
            normalized["owner"] = (
                github_owner.get("login")
                or github_owner.get("name")
                or owner
            )
        elif not isinstance(github_owner, str):
            normalized["owner"] = owner

        if not normalized.get("name"):
            normalized["name"] = repo

        if not normalized.get("full_name"):
            normalized["full_name"] = (
                f"{normalized['owner']}/{normalized['name']}"
            )

        return normalized

    def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True,
    ) -> dict[str, Any]:
        """Create a new GitHub repository for the authenticated user."""
        payload = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        return self._post("user/repos", payload)

    def get_tree(
        self,
        owner: str,
        repo: str,
        tree_sha: str = "main",
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Fetch the full git tree of a repository."""
        endpoint = f"repos/{owner}/{repo}/git/trees/{tree_sha}"
        if recursive:
            endpoint += "?recursive=1"
        return self._get(endpoint)

    def list_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: str | None = None,
    ) -> Any:
        """List repository contents at a path."""
        endpoint = (
            f"repos/{owner}/{repo}/contents"
        )

        if path:
            endpoint += f"/{path.strip('/')}"

        if ref:
            endpoint += f"?ref={ref}"

        return self._get(endpoint)

    def get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str | None = None,
    ) -> dict[str, Any]:
        """Get a single repository file."""
        endpoint = (
            f"repos/{owner}/{repo}/contents/{path}"
        )

        if ref:
            endpoint += f"?ref={ref}"

        return self._get(endpoint)

    def get_file_text(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str | None = None,
    ) -> str:
        """Get and decode the text content of a repository file."""
        data = self.get_file(
            owner=owner,
            repo=repo,
            path=path,
            ref=ref,
        )

        encoded = data.get("content", "")

        # GitHub normally returns base64 content with newlines.
        encoded = encoded.replace("\n", "")

        if not encoded:
            return ""

        return base64.b64decode(
            encoded
        ).decode(
            "utf-8",
            errors="replace",
        )

    def list_commits(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        ref: str | None = None,
    ) -> list[dict[str, Any]]:
        """List commits, optionally for a specific branch/ref."""
        endpoint = (
            f"repos/{owner}/{repo}/commits"
            f"?per_page={per_page}"
        )

        if ref:
            endpoint += f"&sha={ref}"

        return self._get(endpoint)

    def list_branches(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:
        """List repository branches."""
        return self._get(
            f"repos/{owner}/{repo}/branches"
            f"?per_page={per_page}"
        )

    def get_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> dict[str, Any]:
        """Inspect a single branch."""
        return self._get(
            f"repos/{owner}/{repo}/branches/{branch}"
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_repositories(
        self,
        query: str,
        per_page: int = 30,
    ) -> dict[str, Any]:
        """Search repositories visible to the authenticated user."""
        from urllib.parse import quote

        encoded_query = quote(
            query,
            safe="",
        )

        return self._get(
            f"search/repositories"
            f"?q={encoded_query}"
            f"&per_page={per_page}"
        )

    # ------------------------------------------------------------------
    # Branch creation
    # ------------------------------------------------------------------

    def create_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
        from_branch: str = "main",
    ) -> dict[str, Any]:
        """Create a branch from an existing branch/ref."""

        source = self.get_branch(
            owner=owner,
            repo=repo,
            branch=from_branch,
        )

        sha = (
            source.get("commit", {})
            .get("sha")
        )

        if not sha:
            raise RuntimeError(
                "Unable to determine source branch commit SHA"
            )

        payload = {
            "ref": f"refs/heads/{branch}",
            "sha": sha,
        }

        return self._post(
            f"repos/{owner}/{repo}/git/refs",
            payload,
        )

    # ------------------------------------------------------------------
    # File modification
    # ------------------------------------------------------------------

    def write_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Create or update a repository file.

        This uses GitHub's Contents API.

        IMPORTANT:
        The caller must enforce permission/approval before invoking
        this method.
        """

        encoded = base64.b64encode(
            content.encode("utf-8")
        ).decode("ascii")

        payload: dict[str, Any] = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }

        # If sha is not supplied, check if the file already exists on GitHub to obtain its SHA
        if sha is None:
            try:
                existing = self.get_file(owner=owner, repo=repo, path=path, ref=branch)
                if isinstance(existing, dict) and "sha" in existing:
                    sha = existing["sha"]
            except Exception:
                pass

        # Updating an existing file requires its current blob SHA.
        if sha:
            payload["sha"] = sha

        return self._put(
            f"repos/{owner}/{repo}/contents/{path}",
            payload,
        )

    def download_zip(
        self,
        owner: str,
        repo: str,
        output_path: str,
        ref: str = "main",
    ) -> str:
        """Download a zip archive of the repository at a given ref/branch."""
        from pathlib import Path

        # Acquire rate limit token
        if not self.rate_limiter.acquire(timeout=30.0):
            raise RuntimeError("Rate limiter timeout: unable to acquire token")

        url = self._url(f"repos/{owner}/{repo}/zipball/{ref}")

        last_exception = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = self.session.get(url, stream=True, timeout=120)

                # Update rate limiter from response headers
                self.rate_limiter.update_from_headers(response.headers)

                if response.status_code in self.RETRYABLE_STATUS:
                    if attempt < self.MAX_RETRIES:
                        if response.status_code == 429:
                            retry_after = response.headers.get("Retry-After")
                            if retry_after:
                                try:
                                    wait_time = min(float(retry_after), self.MAX_BACKOFF)
                                except ValueError:
                                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                            else:
                                wait_time = self.BASE_BACKOFF * (2 ** attempt)
                        else:
                            wait_time = self.BASE_BACKOFF * (2 ** attempt)

                        import random
                        wait_time *= (0.5 + random.random())
                        wait_time = min(wait_time, self.MAX_BACKOFF)

                        logger.warning(
                            "GitHub zip download %s (attempt %d/%d), backing off %.1fs",
                            response.status_code, attempt + 1, self.MAX_RETRIES, wait_time
                        )
                        response.close()
                        time.sleep(wait_time)
                        continue
                    else:
                        response.raise_for_status()

                response.raise_for_status()

                out = Path(output_path)
                out.parent.mkdir(parents=True, exist_ok=True)
                with open(out, "wb") as f:
                    for chunk in response.iter_content(chunk_size=16384):
                        if chunk:
                            f.write(chunk)
                return str(out.resolve())

            except requests.Timeout as exc:
                last_exception = exc
                if attempt < self.MAX_RETRIES:
                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                    logger.warning("GitHub zip download timeout (attempt %d/%d), retrying in %.1fs", attempt + 1, self.MAX_RETRIES, wait_time)
                    time.sleep(wait_time)
                    continue
            except requests.RequestException as exc:
                last_exception = exc
                if attempt < self.MAX_RETRIES:
                    wait_time = self.BASE_BACKOFF * (2 ** attempt)
                    logger.warning("GitHub zip download error: %s (attempt %d/%d), retrying in %.1fs", exc, attempt + 1, self.MAX_RETRIES, wait_time)
                    time.sleep(wait_time)
                    continue

        raise RuntimeError(f"GitHub zip download failed after {self.MAX_RETRIES} retries: {last_exception}") from last_exception

    def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        branch: str = "main",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Delete a file in a repository."""
        if sha is None:
            existing = self.get_file(owner=owner, repo=repo, path=path, ref=branch)
            sha = existing.get("sha")
            if not sha:
                raise RuntimeError(f"Unable to find SHA for file {path} to delete")
        payload = {
            "message": message,
            "sha": sha,
            "branch": branch,
        }
        return self._delete(
            f"repos/{owner}/{repo}/contents/{path}",
            payload,
        )

    def write_file_from_existing(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict[str, Any]:
        """Update a known existing file using its current SHA."""

        current = self.get_file(
            owner=owner,
            repo=repo,
            path=path,
            ref=branch,
        )

        current_sha = current.get("sha")

        if not current_sha:
            raise RuntimeError(
                "Unable to determine existing file SHA"
            )

        return self.write_file(
            owner=owner,
            repo=repo,
            path=path,
            content=content,
            message=message,
            branch=branch,
            sha=current_sha,
        )

    # ------------------------------------------------------------------
    # Pull requests
    # ------------------------------------------------------------------

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = "",
    ) -> dict[str, Any]:
        """Create a pull request.

        IMPORTANT:
        The caller must enforce explicit approval before invoking
        this method.
        """

        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
        }

        return self._post(
            f"repos/{owner}/{repo}/pulls",
            payload,
        )

    def push_files(
        self,
        owner: str,
        repo: str,
        files: dict[str, str],
        message: str,
        branch: str = "main",
    ) -> dict[str, Any]:
        """Push multiple files atomically in a single Git commit using Git Trees API."""
        branch_info = self.get_branch(owner, repo, branch)
        parent_sha = branch_info["commit"]["sha"]
        base_tree_sha = branch_info["commit"]["commit"]["tree"]["sha"]

        tree_entries = []
        for path, content in files.items():
            tree_entries.append({
                "path": path.replace("\\", "/").lstrip("/"),
                "mode": "100644",
                "type": "blob",
                "content": content,
            })

        new_tree = self._post(f"repos/{owner}/{repo}/git/trees", {
            "base_tree": base_tree_sha,
            "tree": tree_entries,
        })

        new_commit = self._post(f"repos/{owner}/{repo}/git/commits", {
            "message": message,
            "tree": new_tree["sha"],
            "parents": [parent_sha],
        })

        self._patch(
            f"repos/{owner}/{repo}/git/refs/heads/{branch}",
            {"sha": new_commit["sha"]},
        )

        return {
            "ok": True,
            "commit_sha": new_commit["sha"],
            "tree_sha": new_tree["sha"],
            "files_count": len(files),
            "message": message,
            "url": f"https://github.com/{owner}/{repo}/commit/{new_commit['sha']}",
        }