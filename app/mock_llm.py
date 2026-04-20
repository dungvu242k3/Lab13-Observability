from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE
from .tracing import observe


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self._cache: dict[str, str] = {}

    @observe(as_type="generation")
    def generate(self, prompt: str) -> FakeResponse:
        if prompt in self._cache:
            # Cache hit: 0 tokens cost
            return FakeResponse(text=self._cache[prompt], usage=FakeUsage(0, 0), model=self.model)
        
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
        answer = (
            "Dạ chào bạn, tôi là Trợ lý Y khoa ảo. Dựa trên thông tin y tế thu thập được: "
            f"'{prompt[:20]}...', đây là lời khuyên tham khảo. Lưu ý: Xin vui lòng đến cơ sở y tế để được bác sĩ khám trực tiếp."
        )
        self._cache[prompt] = answer
        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
