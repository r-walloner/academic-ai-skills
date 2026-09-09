#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


BASE_URL = os.environ.get("CLAUDE_PROJECT_SYNC_BASE_URL", "https://claude.ai/api").rstrip("/")
SESSION_KEY = os.environ.get("CLAUDE_PROJECT_SYNC_SESSION_KEY", "")
PROJECT_ID = os.environ.get("CLAUDE_PROJECT_SYNC_PROJECT_ID", "")
ORGANIZATION_ID = os.environ.get("CLAUDE_PROJECT_SYNC_ORGANIZATION_ID", "")
ALLOWED_OUTPUT_ROOT = os.environ.get("CLAUDE_PROJECT_SYNC_OUTPUT_ROOT", "/mnt/user-data/outputs")
CANONICAL_FILE_RE = re.compile(r"^(course-state\.md|exam-brief\.md|digest-[a-zA-Z0-9-]+\.md)$")
USER_AGENT = "academic-ai-skills-project-sync/0.1"


class ConfigError(RuntimeError):
    pass


class APIError(RuntimeError):
    pass


class ClaudeProjectSyncClient:
    def __init__(self) -> None:
        if not SESSION_KEY:
            raise ConfigError(
                "Missing CLAUDE_PROJECT_SYNC_SESSION_KEY. "
                "Experimental sync is disabled until the student provides it."
            )
        if not PROJECT_ID:
            raise ConfigError(
                "Missing CLAUDE_PROJECT_SYNC_PROJECT_ID. "
                "Experimental sync is disabled until the student provides it."
            )
        self.base_url = BASE_URL
        self.session_key = SESSION_KEY
        self.project_id = PROJECT_ID
        self.organization_id = ORGANIZATION_ID or self._resolve_organization_id()

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.8",
            "Referer": "https://claude.ai/chats",
            "Content-Type": "application/json",
            "Cookie": f"sessionKey={self.session_key}",
        }

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        expected_statuses: Tuple[int, ...] = (200,),
    ) -> Any:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=self._headers(),
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                status = response.getcode()
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise APIError(f"{method} {path} failed with {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise APIError(f"{method} {path} failed: {exc.reason}") from exc

        if status not in expected_statuses:
            raise APIError(f"{method} {path} returned unexpected status {status}")

        if not body:
            return None
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return body.decode("utf-8", errors="replace")

    def _resolve_organization_id(self) -> str:
        organizations = self._request("GET", "/organizations", expected_statuses=(200,))
        if not isinstance(organizations, list) or not organizations:
            raise APIError("Could not resolve a Claude organization for this session key.")
        for organization in organizations:
            capabilities = organization.get("capabilities", [])
            if "chat" in capabilities or "claude_pro" in capabilities:
                return organization["uuid"]
        return organizations[0]["uuid"]

    def _docs_path(self) -> str:
        return f"/organizations/{self.organization_id}/projects/{self.project_id}/docs"

    def get_project_status(self) -> Dict[str, Any]:
        docs = self.list_docs()
        return {
            "organization_id": self.organization_id,
            "project_id": self.project_id,
            "doc_count": len(docs),
            "experimental": True,
            "supported_surface": "best effort only",
        }

    def list_docs(self) -> List[Dict[str, Any]]:
        docs = self._request("GET", self._docs_path(), expected_statuses=(200,))
        if not isinstance(docs, list):
            raise APIError("Project docs response was not a list.")
        normalized = []
        for doc in docs:
            normalized.append(
                {
                    "uuid": doc.get("uuid"),
                    "file_name": doc.get("file_name") or doc.get("filename") or doc.get("name"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                }
            )
        return normalized

    def put_doc(self, filename: str, content: str) -> Dict[str, Any]:
        payload = {"file_name": filename, "content": content}
        response = self._request("POST", self._docs_path(), payload=payload, expected_statuses=(200, 201))
        if not isinstance(response, dict):
            raise APIError("Upload response was not an object.")
        return response

    def delete_doc_by_uuid(self, file_uuid: str) -> None:
        self._request("DELETE", f"{self._docs_path()}/{file_uuid}", expected_statuses=(200, 204))


def read_message():
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        key, _, value = line.decode("utf-8").partition(":")
        headers[key.lower().strip()] = value.strip()

    content_length = int(headers.get("content-length", "0"))
    body = sys.stdin.buffer.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8"))


def send_message(message: Dict[str, Any]) -> None:
    encoded = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(encoded)}\r\n\r\n".encode("utf-8"))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def send_response(message_id, result: Dict[str, Any]) -> None:
    send_message({"jsonrpc": "2.0", "id": message_id, "result": result})


def send_error(message_id, code: int, message: str) -> None:
    send_message({"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}})


def canonical_filename(filename: str) -> str:
    if not CANONICAL_FILE_RE.match(filename):
        raise ValueError(
            "Only canonical course files may be synced: course-state.md, exam-brief.md, or digest-*.md."
        )
    return filename


def resolve_content(arguments: Dict[str, Any]) -> Tuple[str, str]:
    filename = canonical_filename(arguments.get("filename", ""))
    content = arguments.get("content")
    source_path = arguments.get("source_path")
    if bool(content) == bool(source_path):
        raise ValueError("Provide exactly one of `content` or `source_path`.")
    if source_path:
        real_path = os.path.realpath(source_path)
        if os.path.commonpath([ALLOWED_OUTPUT_ROOT, real_path]) != ALLOWED_OUTPUT_ROOT:
            raise ValueError("source_path must stay under /mnt/user-data/outputs.")
        if os.path.basename(real_path) != filename:
            raise ValueError("source_path basename must match filename.")
        with open(real_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    return filename, content


def success(text: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": data,
    }


def tool_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "get_project",
            "description": "Show the configured Claude Project sync target and basic status.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "list_docs",
            "description": "List docs currently stored in the configured Claude Project.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "put_doc",
            "description": "Upload a canonical course file to the configured Claude Project.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                    "source_path": {"type": "string"},
                },
                "required": ["filename"],
                "additionalProperties": False,
            },
        },
        {
            "name": "delete_doc",
            "description": "Delete a canonical course file from the configured Claude Project by filename.",
            "inputSchema": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
                "additionalProperties": False,
            },
        },
        {
            "name": "replace_doc",
            "description": "Replace a canonical course file in the configured Claude Project while keeping the same filename.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                    "source_path": {"type": "string"},
                },
                "required": ["filename"],
                "additionalProperties": False,
            },
        },
    ]


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    client = ClaudeProjectSyncClient()
    if name == "get_project":
        status = client.get_project_status()
        return success(
            f"Experimental sync target ready for project {status['project_id']} "
            f"({status['doc_count']} docs visible).",
            status,
        )
    if name == "list_docs":
        docs = client.list_docs()
        return success(
            f"Found {len(docs)} docs in the configured Claude Project.",
            {"project_id": client.project_id, "organization_id": client.organization_id, "docs": docs, "experimental": True},
        )
    if name == "put_doc":
        filename, content = resolve_content(arguments)
        response = client.put_doc(filename, content)
        return success(
            f"Uploaded {filename} to the configured Claude Project. Experimental path; verify in Claude.",
            {
                "project_id": client.project_id,
                "organization_id": client.organization_id,
                "filename": filename,
                "action": "uploaded",
                "response": response,
                "experimental": True,
            },
        )
    if name == "delete_doc":
        filename = canonical_filename(arguments.get("filename", ""))
        matches = [doc for doc in client.list_docs() if doc.get("file_name") == filename]
        for match in matches:
            if match.get("uuid"):
                client.delete_doc_by_uuid(match["uuid"])
        return success(
            f"Deleted {len(matches)} matching copy/copies of {filename} from the configured Claude Project.",
            {
                "project_id": client.project_id,
                "organization_id": client.organization_id,
                "filename": filename,
                "deleted_count": len(matches),
                "experimental": True,
            },
        )
    if name == "replace_doc":
        filename, content = resolve_content(arguments)
        matches = [doc for doc in client.list_docs() if doc.get("file_name") == filename]
        for match in matches:
            if match.get("uuid"):
                client.delete_doc_by_uuid(match["uuid"])
        response = client.put_doc(filename, content)
        return success(
            f"Replaced {filename} in the configured Claude Project. Experimental path; still verify in Claude.",
            {
                "project_id": client.project_id,
                "organization_id": client.organization_id,
                "filename": filename,
                "replaced_existing": bool(matches),
                "deleted_count": len(matches),
                "response": response,
                "experimental": True,
            },
        )
    raise ValueError(f"Unknown tool: {name}")


def main() -> int:
    while True:
        message = read_message()
        if message is None:
            return 0

        message_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        try:
            if method == "initialize":
                send_response(
                    message_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "uni-project-sync", "version": "0.1.0-experimental"},
                    },
                )
            elif method == "notifications/initialized":
                continue
            elif method == "ping":
                send_response(message_id, {})
            elif method == "tools/list":
                send_response(message_id, {"tools": tool_definitions()})
            elif method == "tools/call":
                result = call_tool(params.get("name", ""), params.get("arguments", {}))
                send_response(message_id, result)
            else:
                send_error(message_id, -32601, f"Method not found: {method}")
        except (ConfigError, APIError, OSError, ValueError) as exc:
            if method == "tools/call":
                send_response(
                    message_id,
                    {
                        "content": [{"type": "text", "text": str(exc)}],
                        "isError": True,
                    },
                )
            else:
                send_error(message_id, -32000, str(exc))
        except Exception as exc:  # pragma: no cover - defensive last resort
            if method == "tools/call":
                send_response(
                    message_id,
                    {
                        "content": [{"type": "text", "text": f"Unexpected error: {exc}"}],
                        "isError": True,
                    },
                )
            else:
                send_error(message_id, -32001, f"Unexpected error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
