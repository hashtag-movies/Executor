"""Hashtag Dynamic Capability Engine & Hot-Injection Registry.

Enables Hashtag Executor to receive, register, and physically execute
new capabilities autonomously synthesized, tested, and learned by Hashtag Core.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("executor.dynamic_capabilities")


class DynamicCapabilityRegistry:
    """Registry of dynamically injected capabilities learned by Core."""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            base_dir = Path(__file__).parent.parent
            storage_path = str(base_dir / "data" / "dynamic_capabilities.json")
        self.storage_path = Path(storage_path)
        self.capabilities: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._register_default_handlers()
        self._load()

    def _register_default_handlers(self):
        """Register built-in capability templates that Core can activate or extend."""
        self.register(
            capability_id="crypto.hash",
            description="Calculate cryptographic hashes (md5, sha1, sha256, sha512) of text or files.",
            handler=self._handle_crypto_hash,
            metadata={"source": "builtin_template", "domain": "cryptography"}
        )
        self.register(
            capability_id="data.markdown_table_to_json",
            description="Parse markdown tables into structured JSON records.",
            handler=self._handle_markdown_to_json,
            metadata={"source": "builtin_template", "domain": "data_processing"}
        )
        self.register(
            capability_id="text.extract_patterns",
            description="Extract emails, URLs, phone numbers, or IPs from input text.",
            handler=self._handle_extract_patterns,
            metadata={"source": "builtin_template", "domain": "text_analysis"}
        )
        self.register(
            capability_id="filesystem.compress_zip",
            description="Compress files or folders into a zip archive.",
            handler=self._handle_compress_zip,
            metadata={"source": "builtin_template", "domain": "filesystem"}
        )
        self.register(
            capability_id="data.csv_to_json",
            description="Convert CSV formatted text or files into structured JSON.",
            handler=self._handle_csv_to_json,
            metadata={"source": "builtin_template", "domain": "data_processing"}
        )

    def _load(self):
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                for cap_id, cap_data in data.items():
                    self.capabilities[cap_id] = cap_data
                    code = cap_data.get("code")
                    if code and cap_id not in self.handlers:
                        compiled = self._compile_code(code)
                        if compiled:
                            self.handlers[cap_id] = compiled
            except Exception as exc:
                logger.warning(f"Could not load dynamic capabilities: {exc}")

    def _save(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            serializable = {}
            for cap_id, cap_data in self.capabilities.items():
                entry = dict(cap_data)
                serializable[cap_id] = entry
            self.storage_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning(f"Could not save dynamic capabilities: {exc}")

    def _compile_code(self, code_str: str) -> Optional[Callable]:
        """Compile a dynamically synthesized Python function into a callable handler."""
        try:
            safe_globals = {
                "json": json,
                "re": re,
                "hashlib": hashlib,
                "time": time,
                "os": os,
                "Path": Path,
                "zipfile": zipfile,
            }
            local_vars: Dict[str, Any] = {}
            exec(code_str, safe_globals, local_vars)
            # Find the main handler function (usually handle or run or same as cap name)
            for name, val in local_vars.items():
                if callable(val) and not name.startswith("_"):
                    return val
            return None
        except Exception as exc:
            logger.error(f"Error compiling dynamic capability code: {exc}")
            return None

    def register(
        self,
        capability_id: str,
        description: str,
        handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register or hot-inject a new capability."""
        if code and not handler:
            handler = self._compile_code(code)

        if not handler and not code:
            return False

        if handler:
            self.handlers[capability_id] = handler

        self.capabilities[capability_id] = {
            "id": capability_id,
            "description": description,
            "has_handler": bool(handler),
            "code": code,
            "metadata": metadata or {},
            "registered_at": time.time(),
        }
        self._save()
        logger.info(f"Dynamically registered capability: {capability_id}")
        return True

    def has_handler(self, capability_id: str) -> bool:
        return capability_id in self.handlers

    def execute(self, capability_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a dynamic capability."""
        if not self.has_handler(capability_id):
            raise NotImplementedError(f"Dynamic capability '{capability_id}' not found or has no handler.")

        fn = self.handlers[capability_id]
        start_t = time.time()
        try:
            res = fn(arguments)
            duration_ms = round((time.time() - start_t) * 1000, 2)
            if isinstance(res, dict):
                res.setdefault("ok", True)
                res.setdefault("dynamic_execution", True)
                res["duration_ms"] = duration_ms
                return res
            return {
                "ok": True,
                "result": res,
                "dynamic_execution": True,
                "duration_ms": duration_ms,
            }
        except Exception as exc:
            duration_ms = round((time.time() - start_t) * 1000, 2)
            return {
                "ok": False,
                "error": str(exc),
                "dynamic_execution": True,
                "duration_ms": duration_ms,
            }

    def list_capabilities(self) -> List[str]:
        return sorted(list(self.capabilities.keys()))

    def get_catalog(self) -> List[Dict[str, Any]]:
        return list(self.capabilities.values())

    # -------------------------------------------------------------
    # Built-in handler implementations
    # -------------------------------------------------------------

    def _handle_crypto_hash(self, args: Dict[str, Any]) -> Dict[str, Any]:
        algo = str(args.get("algorithm") or args.get("algo") or "sha256").lower()
        text = args.get("text") or args.get("input") or args.get("string")
        file_path = args.get("path") or args.get("file")

        if not hasattr(hashlib, algo):
            return {"ok": False, "error": f"Unsupported hash algorithm: {algo}"}

        hasher = getattr(hashlib, algo)()
        if file_path and os.path.isfile(str(file_path)):
            with open(file_path, "rb") as fp:
                while chunk := fp.read(8192):
                    hasher.update(chunk)
            target = f"file:{file_path}"
        elif text is not None:
            hasher.update(str(text).encode("utf-8"))
            target = f"text_length:{len(str(text))}"
        else:
            return {"ok": False, "error": "crypto.hash requires 'text' or 'path'"}

        digest = hasher.hexdigest()
        return {"ok": True, "algorithm": algo, "digest": digest, "target": target}

    def _handle_markdown_to_json(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = str(args.get("text") or args.get("markdown") or "").strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
        if len(table_lines) < 2:
            return {"ok": False, "error": "No valid markdown table found in input"}

        def parse_row(row_str):
            return [col.strip() for col in row_str.strip("|").split("|")]

        headers = parse_row(table_lines[0])
        # Skip divider row (e.g. |---|---|)
        rows_start = 2 if len(table_lines) > 1 and "---" in table_lines[1] else 1
        data = []
        for line in table_lines[rows_start:]:
            cols = parse_row(line)
            record = {}
            for i, h in enumerate(headers):
                record[h] = cols[i] if i < len(cols) else ""
            data.append(record)

        return {"ok": True, "headers": headers, "count": len(data), "records": data}

    def _handle_extract_patterns(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = str(args.get("text") or args.get("input") or "")
        pattern_type = str(args.get("type") or "emails").lower()

        patterns = {
            "emails": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "urls": r"https?://[^\s/$.?#].[^\s]*",
            "ips": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "phones": r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        }
        regex = patterns.get(pattern_type, patterns["emails"])
        matches = list(set(re.findall(regex, text)))
        return {"ok": True, "type": pattern_type, "count": len(matches), "matches": matches}

    def _handle_compress_zip(self, args: Dict[str, Any]) -> Dict[str, Any]:
        source = Path(str(args.get("source") or args.get("path") or "."))
        output_zip = Path(str(args.get("output") or f"{source.name}.zip"))
        if not source.exists():
            return {"ok": False, "error": f"Source does not exist: {source}"}

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            if source.is_file():
                zf.write(source, arcname=source.name)
            else:
                for root, _, files in os.walk(source):
                    for file in files:
                        p = Path(root) / file
                        arcname = p.relative_to(source.parent)
                        zf.write(p, arcname=str(arcname))

        return {
            "ok": True,
            "archive_path": str(output_zip),
            "size_bytes": output_zip.stat().st_size,
        }

    def _handle_csv_to_json(self, args: Dict[str, Any]) -> Dict[str, Any]:
        import csv
        import io
        text = args.get("text") or args.get("csv")
        file_path = args.get("path") or args.get("file")

        if file_path and os.path.isfile(str(file_path)):
            with open(file_path, "r", encoding="utf-8", errors="replace") as fp:
                reader = csv.DictReader(fp)
                rows = list(reader)
        elif text:
            reader = csv.DictReader(io.StringIO(str(text)))
            rows = list(reader)
        else:
            return {"ok": False, "error": "data.csv_to_json requires 'text' or 'path'"}

        return {"ok": True, "count": len(rows), "records": rows}


dynamic_registry = DynamicCapabilityRegistry()
