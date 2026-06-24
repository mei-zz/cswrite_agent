from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_env_file(path: Path) -> None:
    """读取 .env 文件；不覆盖系统中已经存在的环境变量。"""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# 兼容当前 KG 工程中的 .env，也允许本工程单独放 .env。
load_env_file(PROJECT_ROOT / ".env")
load_env_file(Path("C:/Users/meigang90240/Desktop/KG/.env"))


@dataclass(frozen=True)
class AgentConfig:
    """LangGraph Agent 的集中配置。"""

    project_root: Path = PROJECT_ROOT
    workspace_root: Path = Path(
        os.getenv("CSWRITE_AGENT_WORKSPACE", "C:/Users/meigang90240/Desktop/烧录器agent")
    )
    code_root: Path = Path(
        os.getenv("CSWRITE_CODE_ROOT", "C:/Users/meigang90240/Desktop/KG/code/git_CSWrite3.0")
    )
    runs_root: Path = PROJECT_ROOT / "runs"
    memory_db: Path = PROJECT_ROOT / "memory" / "cswrite_agent.sqlite3"
    skill_path: Path = Path(
        "C:/Users/meigang90240/.config/opencode/skills/eb-tool-test-case/SKILL.md"
    )
    llm_base_url: str = os.getenv(
        "BAILIAN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    llm_model: str = os.getenv("BAILIAN_MODEL", "qwen3.7-plus")
    llm_api_key: str = os.getenv("BAILIAN_API_KEY") or os.getenv("GRAPHRAG_API_KEY", "")
    kg_root: Path = Path("C:/Users/meigang90240/Desktop/KG")
    python_exe: str = "D:/anaconda3/python.exe"
    taskpath_script: Path = Path(
        "C:/Users/meigang90240/Desktop/KG/scripts/taskpath_memory_mcp_proxy.py"
    )
    kg_script: Path = Path("C:/Users/meigang90240/Desktop/KG/scripts/kg_rag_mcp_server.py")
    codegraph_script: Path = Path(
        "C:/Users/meigang90240/Desktop/KG/scripts/start_codegraph_cswrite.ps1"
    )


def get_config() -> AgentConfig:
    cfg = AgentConfig()
    cfg.runs_root.mkdir(parents=True, exist_ok=True)
    cfg.memory_db.parent.mkdir(parents=True, exist_ok=True)
    return cfg

