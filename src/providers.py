"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import re
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

MOCK_ERROR_MARKERS = ("lỗi", "không tìm thấy", "timeout", "exception")


class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API)"""

    @staticmethod
    def _extract_booking_details(question: str):
        date = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", question)
        time = re.search(r"\b(\d{1,2}:\d{2})\b", question)
        customer = re.search(
            r"cho khách\s+(.+?)(?:\.|\n|$)", question, re.IGNORECASE
        )
        if not all((date, time, customer)):
            return None
        return (
            date.group(1),
            time.group(1),
            customer.group(1).strip(),
        )

    @classmethod
    def _extract_booking_args(cls, question: str):
        apartment = re.search(
            r"phòng\s+([A-Z]{2}\d+)", question, re.IGNORECASE
        )
        details = cls._extract_booking_details(question)
        if not apartment or not details:
            return None
        return apartment.group(1).upper(), *details

    @staticmethod
    def _extract_search_args(question: str):
        district = re.search(
            r"\bở\s+(.+?)\s+có giá", question, re.IGNORECASE
        )
        price = re.search(r"(\d[\d.]*)\s*VND", question, re.IGNORECASE)
        if not district or not price:
            return None
        return district.group(1).strip(), int(price.group(1).replace(".", ""))

    def _generate_rental_react(self, prompt: str) -> str:
        """Mô phỏng quyết định ReAct deterministic cho bộ test offline."""
        question = prompt.split("\n\n", 1)[0]
        if question.startswith("Question:"):
            question = question.removeprefix("Question:").strip()

        observations = prompt.count("Observation:")
        last_observation = (
            prompt.rsplit("Observation:", 1)[1].strip()
            if observations
            else ""
        )
        normalized_question = question.casefold()
        normalized_observation = last_observation.casefold()

        if observations:
            if any(
                marker in normalized_observation
                for marker in MOCK_ERROR_MARKERS
            ):
                return (
                    "Thought: Tool đã báo lỗi nên tôi phải dừng an toàn và "
                    "hướng dẫn người dùng sửa dữ liệu.\n"
                    f"Final Answer: Không thể hoàn tất yêu cầu. "
                    f"{last_observation} Vui lòng cung cấp lại ngày hoặc tham "
                    f"số hợp lệ rồi thử lại."
                )

            if "nếu có phòng phù hợp" in normalized_question and observations == 1:
                booking_details = self._extract_booking_details(question)
                apartment = re.search(r"\[([A-Z]{2}\d+)\]", last_observation)
                if booking_details and apartment:
                    date, time, customer = booking_details
                    args = [apartment.group(1), date, time, customer]
                    return (
                        "Thought: Đã có mã phòng phù hợp từ Observation và "
                        "người dùng đã xác nhận, nên có thể đặt lịch.\n"
                        f"Action: schedule_viewing"
                        f"[{', '.join(json.dumps(arg, ensure_ascii=False) for arg in args)}]"
                    )

            return (
                "Thought: Tôi đã có đủ bằng chứng từ Observation để trả lời.\n"
                f"Final Answer: {last_observation}"
            )

        if "nêu 3 điều" in normalized_question:
            return (
                "Thought: Đây là câu hỏi kiến thức chung, không cần gọi tool.\n"
                "Final Answer: Hãy kiểm tra thông tin người cho thuê và quyền "
                "cho thuê; đọc kỹ giá, tiền cọc, chi phí phát sinh; đồng thời "
                "kiểm tra thời hạn, điều kiện hoàn cọc và biên bản bàn giao."
            )

        if "tiền cọc" in normalized_question and "tiền thuê" in normalized_question:
            return (
                "Thought: Đây là câu hỏi khái niệm chung, không cần gọi tool.\n"
                "Final Answer: Tiền cọc là khoản bảo đảm thực hiện hợp đồng và "
                "có thể được hoàn lại theo điều khoản; tiền thuê tháng đầu là "
                "chi phí sử dụng chỗ ở trong tháng đầu và không được hoàn lại."
            )

        search_args = self._extract_search_args(question)
        if search_args:
            district, max_price = search_args
            return (
                "Thought: Cần tra cứu dữ liệu phòng thật theo khu vực và ngân sách.\n"
                f"Action: search_apartments"
                f"[{json.dumps(district, ensure_ascii=False)}, {max_price}]"
            )

        booking_args = self._extract_booking_args(question)
        if booking_args:
            return (
                "Thought: Người dùng đã cung cấp đủ dữ liệu và xác nhận đặt lịch.\n"
                f"Action: schedule_viewing"
                f"[{', '.join(json.dumps(arg, ensure_ascii=False) for arg in booking_args)}]"
            )

        return (
            "Thought: Thiếu dữ liệu để chọn công cụ an toàn.\n"
            "Final Answer: Vui lòng cung cấp rõ khu vực, ngân sách hoặc thông "
            "tin lịch xem nhà cần thực hiện."
        )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if "react agent hỗ trợ tìm nhà trọ" in system_prompt.casefold():
            return self._generate_rental_react(prompt)

        text = prompt.lower()
        if "thời tiết" in text and "hà nội" in text:
            return "Thought: Cần tra cứu thời tiết Hà Nội.\nAction: get_weather['Hà Nội']"
        return "🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test."


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
