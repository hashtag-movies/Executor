import threading, time

DEFAULT_CAPABILITY_SCHEMAS = {
    "filesystem.inspect": {"type":"object","properties":{"path":{"type":"string"},"roots":{"type":"array"}}},
    "filesystem.list": {"type":"object","properties":{"path":{"type":"string"},"roots":{"type":"array"}}},
    "filesystem.search": {"type":"object","properties":{"root":{"type":"string"},"roots":{"type":"array"},"name":{"type":"string"},"contains":{"type":"string"}}},
    "filesystem.read": {"type":"object","properties":{"path":{"type":"string"},"roots":{"type":"array"}}},
}

class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._lock = threading.Lock()
    @staticmethod
    def _normalize_capability(cap):
        if isinstance(cap, str):
            return {"id": cap, "description": "", "input_schema": DEFAULT_CAPABILITY_SCHEMAS.get(cap, {})}
        out = dict(cap or {})
        cid = str(out.get("id","")).strip()
        out["id"] = cid
        out.setdefault("description","")
        out.setdefault("input_schema", DEFAULT_CAPABILITY_SCHEMAS.get(cid, {}))
        return out
    def register(self, manifest):
        tool_id = str(manifest.get("id","")).strip()
        if not tool_id: raise ValueError("manifest.id is required")
        normalized = dict(manifest)
        normalized["capabilities"] = [self._normalize_capability(c) for c in manifest.get("capabilities",[])]
        normalized.setdefault("context", {})
        with self._lock:
            self._tools[tool_id] = {**normalized, "last_seen":time.time(), "brain_protocol":"10.0"}
        return self._tools[tool_id]
    def heartbeat(self, tool_id):
        with self._lock:
            if tool_id in self._tools:
                self._tools[tool_id]["last_seen"]=time.time(); return True
        return False
    def get(self, tool_id): return self._tools.get(tool_id)
    def list(self):
        with self._lock: return [dict(x) for x in self._tools.values()]
    def capabilities(self, tool_id):
        t=self.get(tool_id); return t.get("capabilities",[]) if t else []
    def rank(self, query):
        terms=[t for t in str(query or "").lower().split() if len(t)>2]
        scored=[]
        for tool in self.list():
            caps=tool.get("capabilities",[])
            hay=" ".join([str(tool.get("name","")),str(tool.get("description",""))]+
                         [str(c.get("id",""))+" "+str(c.get("description","")) for c in caps]).lower()
            scored.append((sum(t in hay for t in terms),tool))
        scored.sort(key=lambda z:(z[0],str(z[1].get("name",""))),reverse=True)
        return [t for s,t in scored if s>0] or [t for _,t in scored]
    def public_list(self):
        return [{k:t.get(k) for k in ("id","name","version","description","capabilities","context","last_seen")}
                for t in self.list()]
