$ErrorActionPreference = "Stop"

# 修改为目标电脑实际代码库路径。
$workspace = "C:\Users\meigang90240\Desktop\KG\code\git_CSWrite3.0"
$homeDir = "C:\Users\meigang90240\Desktop\KG\.codegraph-wsl-home-cswrite"
$wslDistro = "Ubuntu"

function ConvertTo-WslPath([string]$PathValue) {
  $resolved = Resolve-Path $PathValue
  $drive = $resolved.Path.Substring(0, 1).ToLowerInvariant()
  $rest = $resolved.Path.Substring(2).Replace("\", "/")
  return "/mnt/$drive$rest"
}

function ConvertTo-BashLiteral([string]$Value) {
  return "'" + $Value.Replace("'", "'\''") + "'"
}

New-Item -ItemType Directory -Force -Path $homeDir | Out-Null

$workspaceArg = ConvertTo-BashLiteral (ConvertTo-WslPath $workspace)
$homeArg = ConvertTo-BashLiteral (ConvertTo-WslPath $homeDir)
$command = "export CODEGRAPH_TELEMETRY=off; export HOME=$homeArg; exec codegraph-mcp --graph-only --workspace $workspaceArg --profile all --max-files 5000"

& wsl.exe -d $wslDistro -- bash -lc $command
exit $LASTEXITCODE

