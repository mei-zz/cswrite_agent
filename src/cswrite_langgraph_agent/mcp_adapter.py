from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .config import AgentConfig


def _content_to_jsonable(value: Any) -> Any:
    """把 MCP 返回对象转换成 JSON 友好结构。"""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list):
        return [_content_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _content_to_jsonable(item) for key, item in value.items()}
    return value


@dataclass
class MCPServerConfig:
    name: str
    command: str
    args: list[str]
    cwd: Path


class MCPClient:
    """最小 MCP stdio 客户端。

    为了让 LangGraph 不绑定 OpenCode，这里直接复用 MCP server 的启动命令。
    每次调用会启动一次 server，简单稳定；后续生产化可改成长连接连接池。
    """

    async def list_tools(self, server: MCPServerConfig) -> list[str]:
        async with stdio_client(
            StdioServerParameters(
                command=server.command,
                args=server.args,
                cwd=str(server.cwd),
            )
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()
                return [tool.name for tool in result.tools]

    async def call_tool(
        self, server: MCPServerConfig, tool_name: str, arguments: dict[str, Any]
    ) -> Any:
        async with stdio_client(
            StdioServerParameters(
                command=server.command,
                args=server.args,
                cwd=str(server.cwd),
            )
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                data = _content_to_jsonable(result)
                # FastMCP 常把 JSON 结果放在 content[0].text。
                try:
                    text = data["content"][0]["text"]
                    return json.loads(text)
                except Exception:
                    return data

    def call(self, server: MCPServerConfig, tool_name: str, arguments: dict[str, Any]) -> Any:
        return asyncio.run(self.call_tool(server, tool_name, arguments))

    def tools(self, server: MCPServerConfig) -> list[str]:
        return asyncio.run(self.list_tools(server))


def server_configs(cfg: AgentConfig) -> dict[str, MCPServerConfig]:
    return {
        "taskpath_memory": MCPServerConfig(
            name="taskpath_memory",
            command=cfg.python_exe,
            args=[str(cfg.taskpath_script)],
            cwd=cfg.kg_root,
        ),
        "kg_rag_neo4j": MCPServerConfig(
            name="kg_rag_neo4j",
            command=cfg.python_exe,
            args=[str(cfg.kg_script)],
            cwd=cfg.kg_root,
        ),
        "codegraph": MCPServerConfig(
            name="codegraph",
            command="powershell.exe",
            args=[
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(cfg.codegraph_script),
            ],
            cwd=cfg.code_root,
        ),
    }


class Retriever:
    """统一检索入口：demo 用本地文件，real 用 MCP。"""

    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg
        self.client = MCPClient()
        self.servers = server_configs(cfg)

    def retrieve(self, query: str, mode: str, repo_dir: str = "") -> dict[str, Any]:
        if mode == "demo":
            return self._demo_retrieve(query, Path(repo_dir) if repo_dir else None)
        return self._real_retrieve(query)

    def _demo_retrieve(self, query: str, repo_dir: Path | None) -> dict[str, Any]:
        docs_dir = self.cfg.project_root / "examples" / "fake_docs"
        doc_hits = []
        for path in docs_dir.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            doc_hits.append({"source": str(path), "text": text[:1200]})
        code_hits = []
        if repo_dir and repo_dir.exists():
            for path in repo_dir.rglob("*.[ch]"):
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(token.lower() in text.lower() for token in ["ICP", "CHIP", "VMODEL"]):
                    code_hits.append({"file": str(path), "snippet": text[:1200]})
        return {
            "taskpaths": [],
            "docs": doc_hits,
            "code": code_hits,
            "diagnostics": ["demo 模式：使用 examples/fake_docs 与示例仓库检索。"],
        }

    def _real_retrieve(self, query: str) -> dict[str, Any]:
        diagnostics: list[str] = []
        result: dict[str, Any] = {"taskpaths": [], "docs": [], "code": [], "diagnostics": diagnostics}
        try:
            result["taskpaths"] = self.client.call(
                self.servers["taskpath_memory"], "taskpath_search", {"query": query, "limit": 5}
            )
        except Exception as exc:
            diagnostics.append(f"taskpath_memory 调用失败：{exc}")
        try:
            result["docs"] = self.client.call(
                self.servers["kg_rag_neo4j"],
                "kg_hybrid_search",
                {"query": query, "top_k": 6, "include_graph": True},
            )
        except Exception as exc:
            diagnostics.append(f"kg_rag_neo4j 调用失败：{exc}")
        try:
            tools = self.client.tools(self.servers["codegraph"])
            preferred_order = [
                "codegraph_get_curated_context",
                "codegraph_symbol_search",
                "codegraph_search_by_pattern",
            ]
            preferred = next((name for name in preferred_order if name in tools), "")
            if preferred == "codegraph_get_curated_context":
                result["code"] = self.client.call(
                    self.servers["codegraph"],
                    preferred,
                    {"query": query, "maxTokens": 6000, "maxSymbols": 8},
                )
            elif preferred == "codegraph_symbol_search":
                result["code"] = self.client.call(
                    self.servers["codegraph"],
                    preferred,
                    {"query": query, "limit": 20, "symbolType": "any", "compact": True},
                )
            elif preferred == "codegraph_search_by_pattern":
                result["code"] = self.client.call(
                    self.servers["codegraph"],
                    preferred,
                    {"pattern": query, "limit": 50, "scope": "any", "node_type": "any"},
                )
            else:
                result["code"] = {"available_tools": tools}
        except Exception as exc:
            diagnostics.append(f"codegraph 调用失败：{exc}")
        return result
