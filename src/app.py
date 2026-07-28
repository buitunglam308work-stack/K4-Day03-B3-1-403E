"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import ast
import csv
import inspect
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    MAX_ITERATIONS,
    REACT_SYSTEM_PROMPT,
    TIMEOUT_SECONDS,
)
from providers import get_llm_provider

load_dotenv()


ACTION_PATTERN = re.compile(
    r"^Action:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*)\]\s*$",
    re.MULTILINE,
)
FINAL_ANSWER_PATTERN = re.compile(
    r"^Final Answer:\s*(.+)$",
    re.DOTALL | re.MULTILINE,
)
SIDE_EFFECT_TOOLS = {"schedule_viewing", "cancel_viewing"}
ERROR_MARKERS = ("lỗi", "không tìm thấy", "timeout", "exception")
REACT_ROUTE_MARKERS = (
    "tìm phòng",
    "tìm căn hộ",
    "giá tối đa",
    "mã phòng",
    "chi tiết phòng",
    "đặt lịch",
    "hủy lịch",
    "booking",
)
UNSAFE_CONFIRMATION_MARKERS = (
    "không xác nhận",
    "chưa xác nhận",
    "không đồng ý",
    "chưa đồng ý",
    "đừng đặt",
    "không đặt lịch",
    "đừng hủy",
    "không hủy lịch",
    "bỏ qua",
    "ignore",
    "giả sử",
    "coi như",
)


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider) -> str:
    """
    Chạy đúng một lượt sinh câu trả lời của Chatbot Baseline.

    Hàm này cố ý không đọc ``AVAILABLE_TOOLS`` và không thực thi tool để giữ
    đường cơ sở công bằng khi so sánh với ReAct Agent ở mốc sau.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")

    # Một test case tương ứng đúng một lần gọi LLM Provider.
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    print("📊 Telemetry: llm_calls=1, tool_calls=0")
    return response


def run_baseline_suite(test_cases: list[dict], provider) -> list[dict]:
    """Chạy Chatbot Baseline lần lượt trên toàn bộ test case của Role 1."""
    results = []

    for test_case in test_cases:
        print(
            f"\n{'-' * 50}\n"
            f"🧪 Test case #{test_case['id']} - {test_case['category']}"
        )
        response = run_baseline_chatbot(test_case["question"], provider)
        results.append(
            {
                "id": test_case["id"],
                "question": test_case["question"],
                "response": response,
                "llm_calls": 1,
                "tool_calls": 0,
            }
        )

    return results


def _coerce_unquoted_arg(value: str):
    """Chuyển một argument fallback thành số hoặc chuỗi."""
    cleaned = value.strip().strip("\"'")
    if re.fullmatch(r"-?\d+", cleaned):
        return int(cleaned)
    if re.fullmatch(r"-?\d+\.\d+", cleaned):
        return float(cleaned)
    return cleaned


def parse_action(model_output: str) -> tuple[str, list] | None:
    """
    Parse ``Action: tool_name[arg1, ...]`` mà không dùng ``eval``.

    Ưu tiên cú pháp literal an toàn (chuỗi có quote, số), sau đó fallback sang
    CSV để không crash khi model quên quote một chuỗi đơn giản.
    """
    match = ACTION_PATTERN.search(model_output)
    if not match:
        return None

    tool_name = match.group(1)
    raw_args = match.group(2).strip()
    if not raw_args:
        return tool_name, []

    try:
        parsed = ast.literal_eval(f"[{raw_args}]")
        if not isinstance(parsed, list):
            raise ValueError("Danh sách argument không hợp lệ.")
        return tool_name, parsed
    except (SyntaxError, ValueError):
        try:
            values = next(csv.reader([raw_args], skipinitialspace=True))
        except (csv.Error, StopIteration) as exc:
            raise ValueError(f"Không parse được arguments: {exc}") from exc
        return tool_name, [_coerce_unquoted_arg(value) for value in values]


def _has_explicit_confirmation(user_query: str, tool_name: str) -> bool:
    """Kiểm tra xác nhận tối thiểu trước tool có side effect."""
    normalized = user_query.casefold()
    if any(marker in normalized for marker in UNSAFE_CONFIRMATION_MARKERS):
        return False

    if tool_name == "schedule_viewing":
        markers = (
            "tôi xác nhận đặt lịch",
            "tôi đồng ý đặt lịch",
            "hãy đặt lịch",
            "xác nhận đặt lịch",
        )
    else:
        markers = (
            "tôi xác nhận hủy lịch",
            "tôi đồng ý hủy lịch",
            "hãy hủy lịch",
            "xác nhận hủy lịch",
        )
    return any(marker in normalized for marker in markers)


def choose_hybrid_path(user_query: str) -> str:
    """Phân luồng FAQ đơn giản sang Chatbot, tác vụ dữ liệu sang ReAct."""
    normalized = user_query.casefold()
    has_listing_id = bool(re.search(r"\b(?:NT|CH)\d{2}\b", user_query, re.I))
    needs_tool = has_listing_id or any(
        marker in normalized for marker in REACT_ROUTE_MARKERS
    )
    return "react" if needs_tool else "chatbot"


def run_hybrid_query(user_query: str, provider) -> dict:
    """Chạy đúng nhánh theo quyết định Hybrid Router."""
    path = choose_hybrid_path(user_query)
    if path == "chatbot":
        answer = run_baseline_chatbot(user_query, provider)
        return {
            "path": path,
            "answer": answer,
            "tool_calls": 0,
            "status": "completed",
        }

    result = run_react_agent(user_query, provider)
    return {"path": path, **result}


def execute_tool(tool_name: str, args: list, user_query: str) -> str:
    """Validate và thực thi đúng một tool, luôn chuyển lỗi thành Observation."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        allowed = ", ".join(sorted(AVAILABLE_TOOLS))
        return (
            f"LỖI UNKNOWN TOOL: '{tool_name}' không tồn tại. "
            f"Các tool hợp lệ: {allowed}."
        )

    if tool_name in SIDE_EFFECT_TOOLS and not _has_explicit_confirmation(
        user_query, tool_name
    ):
        return (
            f"LỖI GUARDRAIL: Chưa có xác nhận rõ ràng để gọi tool "
            f"'{tool_name}'."
        )

    try:
        inspect.signature(tool).bind(*args)
    except TypeError as exc:
        return f"LỖI ARGUMENTS cho tool '{tool_name}': {exc}"

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(tool, *args)
    try:
        result = future.result(timeout=TIMEOUT_SECONDS)
        return str(result)
    except FutureTimeoutError:
        future.cancel()
        return (
            f"LỖI TIMEOUT: Tool '{tool_name}' vượt quá "
            f"{TIMEOUT_SECONDS} giây."
        )
    except Exception as exc:
        return f"LỖI TOOL '{tool_name}': {type(exc).__name__}: {exc}"
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _is_error_observation(observation: str) -> bool:
    normalized = observation.casefold()
    return any(marker in normalized for marker in ERROR_MARKERS)


def _safe_fallback(last_observation: str = "") -> str:
    detail = last_observation.strip()
    if detail:
        return (
            "Tôi chưa thể hoàn tất yêu cầu một cách an toàn. "
            f"Kết quả cuối cùng từ hệ thống: {detail}"
        )
    return (
        "Tôi chưa thể hoàn tất yêu cầu trong giới hạn xử lý an toàn. "
        "Vui lòng kiểm tra lại thông tin và thử lại."
    )


def run_react_agent(user_query: str, provider) -> dict:
    """
    Chạy ReAct loop: LLM -> Action -> Tool -> Observation -> LLM.

    Kết quả trả về có trace, số bước, số tool call và trạng thái để Role 1/5
    có thể nghiệm thu edge case và lưu bằng chứng observability.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    trace = []
    seen_actions = set()
    tool_calls = 0
    last_observation = ""

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        history = "\n".join(trace)
        agent_input = f"Question: {user_query}"
        if history:
            agent_input = f"{agent_input}\n\n{history}"

        try:
            model_output = str(
                provider.generate(
                    agent_input, system_prompt=REACT_SYSTEM_PROMPT
                )
            ).strip()
        except Exception as exc:
            model_output = (
                "Thought: Provider gặp lỗi nên chưa thể chọn hành động.\n"
                f"Provider Error: {type(exc).__name__}: {exc}"
            )
        print(model_output)
        trace.append(model_output)

        try:
            action = parse_action(model_output)
        except ValueError as exc:
            last_observation = f"LỖI PARSE ARGUMENTS: {exc}"
            observation_line = f"Observation: {last_observation}"
            print(f"👁️ {observation_line}")
            trace.append(observation_line)
            continue

        final_match = FINAL_ANSWER_PATTERN.search(model_output)

        if action and final_match:
            last_observation = (
                "LỖI ĐỊNH DẠNG: Một lượt không được chứa đồng thời Action "
                "và Final Answer."
            )
            observation_line = f"Observation: {last_observation}"
            print(f"👁️ {observation_line}")
            trace.append(observation_line)
            continue

        if final_match:
            answer = final_match.group(1).strip()
            status = (
                "safe_fallback"
                if _is_error_observation(last_observation)
                else "completed"
            )
            return {
                "answer": answer,
                "trace": trace,
                "steps": step,
                "tool_calls": tool_calls,
                "status": status,
                "guardrail_triggered": status == "safe_fallback",
            }

        if action:
            tool_name, args = action
            action_key = (tool_name, repr(args))
            if action_key in seen_actions:
                last_observation = (
                    "LỖI GUARDRAIL: Phát hiện Action lặp lại với cùng tham số; "
                    "đã chặn để tránh vòng lặp vô hạn."
                )
            else:
                seen_actions.add(action_key)
                last_observation = execute_tool(tool_name, args, user_query)
                tool_calls += 1

            observation_line = f"Observation: {last_observation}"
            print(f"👁️ {observation_line}")
            trace.append(observation_line)
            continue

        last_observation = (
            "LỖI PARSE: Phản hồi phải chứa đúng một Action hoặc Final Answer."
        )
        observation_line = f"Observation: {last_observation}"
        print(f"👁️ {observation_line}")
        trace.append(observation_line)

    answer = _safe_fallback(last_observation)
    print(
        f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa "
        f"{MAX_ITERATIONS} bước."
    )
    print(f"🏁 Final Answer: {answer}")
    trace.append(f"Final Answer: {answer}")
    return {
        "answer": answer,
        "trace": trace,
        "steps": MAX_ITERATIONS,
        "tool_calls": tool_calls,
        "status": "safe_fallback",
        "guardrail_triggered": True,
    }


def run_react_suite(test_cases: list[dict], provider) -> list[dict]:
    """Chạy ReAct Agent trên toàn bộ test case và gom telemetry."""
    results = []
    for test_case in test_cases:
        print(
            f"\n{'=' * 50}\n"
            f"🧪 ReAct test #{test_case['id']} - {test_case['category']}"
        )
        result = run_react_agent(test_case["question"], provider)
        results.append({"id": test_case["id"], **result})
    return results


def run_cli():
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    print("--- MỐC 2: CHẠY CHATBOT BASELINE TRÊN TOÀN BỘ TEST CASE ---")
    results = run_baseline_suite(tests, provider)

    print("\n==================================================")
    print("📈 TỔNG KẾT CHATBOT BASELINE")
    print(f"✅ Test cases đã chạy: {len(results)}")
    print(f"🧠 Tổng số lần gọi LLM: {sum(item['llm_calls'] for item in results)}")
    print(f"🛠️ Tổng số lần gọi Tool: {sum(item['tool_calls'] for item in results)}")

    print("\n--- MỐC 3: CHẠY REACT AGENT TRÊN TOÀN BỘ TEST CASE ---")
    react_results = run_react_suite(tests, provider)

    print("\n==================================================")
    print("📈 TỔNG KẾT REACT AGENT")
    print(f"✅ Test cases đã chạy: {len(react_results)}")
    print(
        "🛠️ Tổng số lần gọi Tool: "
        f"{sum(item['tool_calls'] for item in react_results)}"
    )
    print(
        "🛡️ Safe fallback/Guardrail: "
        f"{sum(item['guardrail_triggered'] for item in react_results)}"
    )


if __name__ == "__main__":
    if "--ui" in sys.argv:
        from ui_server import run_server

        port = int(os.getenv("PORT", "8765"))
        run_server(port=port)
    else:
        run_cli()
