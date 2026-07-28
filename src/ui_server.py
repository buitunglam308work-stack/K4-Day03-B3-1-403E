"""Local browser UI for the Chatbot/ReAct lab.

The UI deliberately uses only Python's standard library so the lab can be
started without adding another web framework or frontend build step.
"""

from __future__ import annotations

import contextlib
import io
import json
import mimetypes
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import app as core
import tools
from providers import MockProvider, get_llm_provider


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = Path(__file__).resolve().parent / "ui"
CROSS_AUDIT_PATH = PROJECT_ROOT / "config" / "moc4_cross_audit_cases.json"
FLOWCHART_PATH = PROJECT_ROOT / "docs" / "hybrid_flowchart.mermaid"


def _quiet_call(function, *args, **kwargs):
    """Run core functions without dumping their trace into the HTTP log."""
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args, **kwargs)


def _provider(provider_name: str | None):
    name = (provider_name or "env").strip().lower()
    if name in {"", "env", "default"}:
        return get_llm_provider()
    if name in {"mock", "demo", "offline"}:
        return MockProvider()
    return get_llm_provider(name)


def _trace_items(trace: list[str]) -> list[dict]:
    """Turn raw trace entries into UI-friendly timeline cards."""
    items: list[dict] = []
    section_pattern = re.compile(
        r"^(Thought|Action|Observation|Final Answer):\s*(.*)$"
    )
    for raw in trace:
        current_label = "System"
        current_lines: list[str] = []

        def flush():
            if not current_lines:
                return
            label = current_label
            kind = {
                "Thought": "thought",
                "Action": "action",
                "Observation": "observation",
                "Final Answer": "final",
            }.get(label, "system")
            items.append(
                {
                    "kind": kind,
                    "label": label,
                    "text": "\n".join(current_lines).strip(),
                }
            )

        for line in str(raw).strip().splitlines():
            match = section_pattern.match(line.strip())
            if match:
                flush()
                current_label = match.group(1)
                current_lines = [match.group(2)] if match.group(2) else []
            else:
                current_lines.append(line)
        flush()
    return items


def _load_cross_audit_cases() -> list[dict]:
    with CROSS_AUDIT_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


class _ScriptedProvider:
    """Provider dùng trong audit UI để mô phỏng output độc hại của model."""

    def __init__(self, outputs: list[str], repeat_last: bool = False):
        self.outputs = list(outputs)
        self.repeat_last = repeat_last
        self.index = 0

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self.index < len(self.outputs):
            value = self.outputs[self.index]
            self.index += 1
            return value
        if self.repeat_last and self.outputs:
            return self.outputs[-1]
        return "Thought: Dừng an toàn.\nFinal Answer: Dừng an toàn."


def _expected_result(result: dict, expected: dict) -> tuple[bool, list[str]]:
    """Compare a core result với expectation trong cross-audit JSON."""
    failures = []
    for key in ("path", "status", "tool_calls", "guardrail_triggered"):
        if key in expected and result.get(key) != expected[key]:
            failures.append(
                f"{key}: expected {expected[key]!r}, got {result.get(key)!r}"
            )

    answer = str(result.get("answer", ""))
    trace = "\n".join(
        item.get("text", "") for item in _trace_items(result.get("trace", []))
    )
    if "answer_contains" in expected and expected["answer_contains"] not in answer:
        failures.append(f"answer thiếu: {expected['answer_contains']}")
    if (
        "answer_not_contains" in expected
        and expected["answer_not_contains"] in answer
    ):
        failures.append(f"answer chứa cấm: {expected['answer_not_contains']}")
    if "trace_contains" in expected and expected["trace_contains"] not in trace:
        failures.append(f"trace thiếu: {expected['trace_contains']}")
    return not failures, failures


def _run_audit_case(case: dict) -> dict:
    """Run one cross-audit scenario and return a serializable UI record."""
    expected = case.get("expected", {})
    mode = case.get("mode")
    tools.reset_mock_bookings()
    record = {
        "id": case["id"],
        "attack_type": case.get("attack_type", "unknown"),
        "question": case.get("question", ""),
        "mode": mode,
        "passed": False,
        "status": "not_run",
        "guardrail_triggered": False,
        "tool_calls": 0,
        "steps": 0,
        "path": None,
        "answer": "",
        "trace": [],
        "failures": [],
    }

    if mode == "hybrid":
        result = _quiet_call(
            core.run_hybrid_query,
            case["question"],
            MockProvider(),
        )
        passed, failures = _expected_result(result, expected)
        record.update(result)
        record["trace"] = _trace_items(result.get("trace", []))
        record["passed"] = passed
        record["failures"] = failures
        return record

    if mode == "react_scripted":
        provider = _ScriptedProvider(
            case.get("model_outputs", []),
            case.get("repeat_last_output", False),
        )
        result = _quiet_call(
            core.run_react_agent,
            case["question"],
            provider,
        )
        passed, failures = _expected_result(result, expected)
        record.update(result)
        record["path"] = "react"
        record["trace"] = _trace_items(result.get("trace", []))
        record["passed"] = passed
        record["failures"] = failures
        return record

    if mode == "tool_direct":
        tool_name = case["tool"]
        raw_result = str(getattr(tools, tool_name)(*case["args"]))
        passed = (
            expected.get("result_contains", "") in raw_result
            and expected.get("result_not_contains", "") not in raw_result
        )
        record.update(
            {
                "path": "tool",
                "status": "completed" if passed else "safe_fallback",
                "answer": raw_result,
                "passed": passed,
                "trace": [
                    {
                        "kind": "observation",
                        "label": "Tool Observation",
                        "text": raw_result,
                    }
                ],
                "failures": []
                if passed
                else ["Tool output không khớp expectation."],
            }
        )
        return record

    if mode == "booking_roundtrip":
        booking = tools.schedule_viewing(
            "NT01", "2026-08-01", "09:00", "Nguyễn An"
        )
        match = re.search(r"BOOK-[A-Z0-9]+-[A-F0-9]{8}", booking)
        cancel = (
            tools.cancel_viewing(match.group(0), "Nguyễn An")
            if match
            else "Không tạo được booking."
        )
        passed = (
            expected.get("booking_contains", "") in booking
            and expected.get("cancel_contains", "") in cancel
        )
        record.update(
            {
                "path": "tool",
                "status": "completed" if passed else "safe_fallback",
                "answer": f"{booking}\n\n{cancel}",
                "passed": passed,
                "trace": [
                    {
                        "kind": "observation",
                        "label": "Booking control",
                        "text": booking,
                    },
                    {
                        "kind": "final",
                        "label": "Cancel control",
                        "text": cancel,
                    },
                ],
                "failures": []
                if passed
                else ["Booking roundtrip không đạt expectation."],
            }
        )
        return record

    record["failures"] = [f"Mode không hỗ trợ: {mode}"]
    return record


def run_cross_audit() -> dict:
    """Run all audit cases for the UI Defense Center."""
    cases = [_run_audit_case(case) for case in _load_cross_audit_cases()]
    passed = sum(1 for case in cases if case["passed"])
    return {
        "cases": cases,
        "total": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "ready": passed == len(cases),
    }


def _demo_catalog() -> list[dict]:
    return [
        {
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "expected_behavior": case["expected_behavior"],
        }
        for case in core.load_test_cases()
    ]


def _json_response(handler, payload: dict, status: int = 200):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


class LabRequestHandler(BaseHTTPRequestHandler):
    """Small JSON API + static file server for the local UI."""

    server_version = "NestReactLab/1.0"

    def log_message(self, format, *args):
        # Keep the terminal quiet; the user operates the lab in the browser.
        return

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            _json_response(
                self,
                {
                    "ok": True,
                    "provider_from_env": os.getenv("LLM_PROVIDER") or "mock",
                    "model_from_env": os.getenv("LLM_MODEL") or "",
                    "ui_provider_default": os.getenv("LLM_PROVIDER") or "mock",
                    "max_iterations": core.MAX_ITERATIONS,
                    "tool_count": len(core.AVAILABLE_TOOLS),
                    "audit_count": len(_load_cross_audit_cases()),
                },
            )
            return
        if path == "/api/test-cases":
            _json_response(
                self,
                {
                    "main_cases": _demo_catalog(),
                    "audit_cases": _load_cross_audit_cases(),
                },
            )
            return
        if path == "/api/flowchart":
            _json_response(
                self,
                {
                    "mermaid": FLOWCHART_PATH.read_text(encoding="utf-8")
                    if FLOWCHART_PATH.exists()
                    else ""
                },
            )
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 1_000_000:
                _json_response(self, {"error": "Payload quá lớn."}, 413)
                return
            raw = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            _json_response(self, {"error": f"JSON không hợp lệ: {exc}"}, 400)
            return

        try:
            if path == "/api/chat":
                self._handle_chat(payload)
                return
            if path == "/api/audit/run":
                _json_response(self, run_cross_audit())
                return
            if path == "/api/demo":
                self._handle_demo(payload)
                return
            _json_response(self, {"error": "Endpoint không tồn tại."}, 404)
        except Exception as exc:
            _json_response(
                self,
                {"error": f"Ứng dụng gặp lỗi an toàn: {type(exc).__name__}: {exc}"},
                500,
            )

    def _handle_chat(self, payload: dict):
        message = str(payload.get("message", "")).strip()
        if not message:
            _json_response(self, {"error": "Hãy nhập câu hỏi trước."}, 400)
            return
        mode = str(payload.get("mode", "hybrid")).lower()
        provider = _provider(payload.get("provider", "env"))
        if mode == "chatbot":
            answer = _quiet_call(core.run_baseline_chatbot, message, provider)
            result = {
                "path": "chatbot",
                "status": "completed",
                "answer": answer,
                "tool_calls": 0,
                "steps": 1,
                "trace": [],
            }
        elif mode == "react":
            result = _quiet_call(core.run_react_agent, message, provider)
            result["path"] = "react"
            result["trace"] = _trace_items(result.get("trace", []))
        else:
            result = _quiet_call(core.run_hybrid_query, message, provider)
            result["trace"] = _trace_items(result.get("trace", []))
        _json_response(self, result)

    def _handle_demo(self, payload: dict):
        provider = _provider(payload.get("provider", "env"))
        results = []
        for case in core.load_test_cases():
            result = _quiet_call(
                core.run_hybrid_query,
                case["question"],
                provider,
            )
            result.update(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "question": case["question"],
                    "trace": _trace_items(result.get("trace", [])),
                }
            )
            results.append(result)
        _json_response(
            self,
            {
                "results": results,
                "completed": len(results),
                "safe_fallbacks": sum(
                    1 for result in results if result["status"] == "safe_fallback"
                ),
            },
        )

    def _serve_static(self, path: str):
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        target = (UI_ROOT / relative).resolve()
        if UI_ROOT.resolve() not in target.parents and target != UI_ROOT.resolve():
            _json_response(self, {"error": "Đường dẫn không hợp lệ."}, 400)
            return
        if not target.exists() or not target.is_file():
            _json_response(self, {"error": "Không tìm thấy tài nguyên."}, 404)
            return
        data = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str = "127.0.0.1", port: int = 8765):
    """Start the browser app; Ctrl+C is only needed to stop the local server."""
    server = ThreadingHTTPServer((host, port), LabRequestHandler)
    print(f"NestReact Lab UI đang chạy tại http://{host}:{port}")
    print("Mở URL trên trình duyệt để chat và chạy Cross-Audit.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng NestReact Lab UI.")
    finally:
        server.server_close()
