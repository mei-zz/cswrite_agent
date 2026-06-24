$ErrorActionPreference = "Stop"

# 修改为目标电脑实际路径。
$PythonExe = "D:/anaconda3/python.exe"
$KgRoot = "C:/Users/meigang90240/Desktop/KG"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServerScript = Join-Path $ScriptDir "taskpath_memory_mcp_server.py"

$env:TASKPATH_DIR = Join-Path $KgRoot "task_paths"

& $PythonExe $ServerScript
exit $LASTEXITCODE

