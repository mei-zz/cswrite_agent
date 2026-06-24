$ErrorActionPreference = "Stop"

# 修改为目标电脑实际路径。
$PythonExe = "D:/anaconda3/python.exe"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$McpRoot = Split-Path -Parent $ScriptDir

# kg_rag_mcp_server.py 会读取 $McpRoot/.env。
Set-Location $McpRoot
& $PythonExe (Join-Path $ScriptDir "kg_rag_mcp_server.py")
exit $LASTEXITCODE
