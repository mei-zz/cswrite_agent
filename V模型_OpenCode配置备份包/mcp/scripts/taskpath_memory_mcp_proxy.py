from __future__ import annotations

import runpy
from pathlib import Path


SCRIPT = (
    Path.home()
    / "Desktop"
    / "\u70e7\u5f55\u5668agent"
    / "scripts"
    / "taskpath_memory_mcp_server.py"
)

runpy.run_path(str(SCRIPT), run_name="__main__")
