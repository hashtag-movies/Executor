import json
import os
import threading
import time
import uuid


class MemoryStore:
    """Best-effort local memory that survives transient Windows/OneDrive locks."""

    def __init__(self, path="data/memory.json"):
        self.path = os.path.abspath(path)
        self.lock = threading.Lock()
        self.data = {"events": [], "learned": []}
        self._load()

    def _load(self):
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, dict):
                self.data.update(obj)
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
            pass

    def _save(self):
        directory = os.path.dirname(self.path) or "."
        os.makedirs(directory, exist_ok=True)
        payload = json.dumps(self.data, ensure_ascii=False, indent=2)
        tmp = os.path.join(directory, f".memory-{os.getpid()}-{uuid.uuid4().hex}.tmp")
        try:
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                f.write(payload)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass
            for delay in (0.0, 0.05, 0.15, 0.35, 0.75):
                if delay:
                    time.sleep(delay)
                try:
                    os.replace(tmp, self.path)
                    return True
                except OSError:
                    pass
            try:
                with open(self.path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(payload)
                    f.flush()
                return True
            except OSError:
                return False
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass

    def remember(self, event):
        with self.lock:
            self.data.setdefault("events", []).append({"time": time.time(), **event})
            self.data["events"] = self.data["events"][-1000:]
            self._save()

    def learn(self, recipe):
        with self.lock:
            recipe = {"time": time.time(), **recipe}
            items = self.data.setdefault("learned", [])
            tool_id, intent = recipe.get("tool_id"), recipe.get("intent", "")
            items[:] = [x for x in items if not (x.get("tool_id") == tool_id and x.get("intent") == intent and x.get("kind") == recipe.get("kind"))]
            items.append(recipe)
            self.data["learned"] = items[-500:]
            self._save()

    def find_recipe(self, tool_id, signature):
        with self.lock:
            for x in reversed(self.data.get("learned", [])):
                if x.get("tool_id") == tool_id and x.get("intent") == signature:
                    return x.get("actions", [])
        return []

    def find_skills(self, tool_id, signature):
        with self.lock:
            return [x for x in self.data.get("learned", []) if x.get("kind") == "learned_skill" and x.get("tool_id") == tool_id and x.get("intent") == signature]

    def find_skills_any(self, tool_id, signature):
        with self.lock:
            exact=[]; shared=[]
            for x in self.data.get("learned", []):
                if x.get("kind") != "learned_skill" or x.get("intent") != signature: continue
                if x.get("tool_id") == tool_id: exact.append(x)
                elif x.get("scope") == "shared": shared.append(x)
            return list(reversed(exact)) + list(reversed(shared))

    def recent(self, limit=20):
        with self.lock:
            return self.data.get("events", [])[-limit:]

    def learned(self, limit=50):
        with self.lock:
            return self.data.get("learned", [])[-limit:]
