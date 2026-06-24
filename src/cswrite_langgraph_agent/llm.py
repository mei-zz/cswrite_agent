from __future__ import annotations

from openai import OpenAI

from .config import AgentConfig


class LLMClient:
    """百炼 OpenAI-compatible 调用封装。

    workflow 默认可以使用 template 模式稳定测试；切到 bailian 模式后，
    节点可以调用该客户端做需求归纳、方案润色、冲突判断等。
    """

    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg

    def complete(self, system: str, user: str, temperature: float = 0.2) -> str:
        if not self.cfg.llm_api_key:
            raise RuntimeError("缺少 BAILIAN_API_KEY 或 GRAPHRAG_API_KEY。")
        client = OpenAI(api_key=self.cfg.llm_api_key, base_url=self.cfg.llm_base_url)
        response = client.chat.completions.create(
            model=self.cfg.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

