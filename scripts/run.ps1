param(
    [ValidateSet("lint","unit","network","all")]
    [string]$Mode = "unit",

    [string]$Env = "",

    [string]$Marker = "",

    [string]$Report = ""
)

$ErrorActionPreference = "Stop"

# 可选：把环境名塞进环境变量（如果你的 config_loader 支持读取）
if ($Env -ne "") {
    $env:AUTOFW_ENV = $Env
    $env:ENV = $Env
    Write-Host "[run] Env set: $Env"
}

# reports 目录确保存在
if (-not (Test-Path ".\reports")) {
    New-Item -ItemType Directory -Path ".\reports" | Out-Null
}

function Run-Lint {
    Write-Host "[run] ruff check ."
    ruff check .
}

function Run-Pytest([string]$expr, [string]$reportName) {
    $html = ".\reports\$reportName"
    write-host "[run] pytest -m `"$expr`" -q -> $html"
    pytest -m "$expr" -q --html="$html" --self-contained-html
}

# 优先级： Marker 手动指定 > Mode 默认策略
if ($Marker -ne "") {
    $reportName = $(if ($Report -ne "") { $Report } else { "custom.html" })
    Run-Pytest $Marker $reportName
    exit 0
}

switch ($Mode) {
    "lint"    { Run-Lint }
    "unit"    { Run-Pytest "not (network or integration)" $(if ($Report -ne "") { $Report } else { "unit.html" }) }
    "network" { Run-Pytest "network or integration" $(if ($Report -ne "") { $Report } else { "network.html" }) }
    "all"     { Run-Lint; Run-Pytest "not (network or integration)" "unit.html"; Run-Pytest "network or integration" "network.html" }
}