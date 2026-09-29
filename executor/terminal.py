import glob
import os
import subprocess
from .permissions import PermissionEngine, PermissionRequest

class TerminalExecutor:
    def __init__(self, permissions: PermissionEngine): self.permissions = permissions

    def execute(self, command: str, cwd: str | None = None, purpose: str = "Run a diagnostic command") -> dict:
        resource = f"command:{command} cwd:{cwd or ''}"
        d = self.permissions.request(PermissionRequest("terminal.execute", resource, purpose))
        if not d.allowed: raise PermissionError(d.reason)
        env = os.environ.copy()
        git_paths = glob.glob(r"C:\Users\ksdav\AppData\Local\GitHubDesktop\app-*\resources\app\git\cmd")
        git_paths += [r"C:\Program Files\Git\cmd", r"C:\Program Files\Git\bin"]
        extra = [p for p in git_paths if os.path.exists(p) and p not in env.get("PATH", "")]
        if extra:
            env["PATH"] = ";".join(extra) + ";" + env.get("PATH", "")
        completed = subprocess.run(command, cwd=cwd, shell=True, text=True, capture_output=True, timeout=120, env=env)
        return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
