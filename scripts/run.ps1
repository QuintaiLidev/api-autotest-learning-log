param(
    [ValidateSet("lint","unit","network","all","perf")]
    [string]$Mode = "unit",

    [string]$Env = "",

    [string]$Marker = "",

    [string]$Report = "",

    # ------ perf only ------
    [ValidateSet("A","B")]
    [string]$PerfGroup = "A",

    [string]$TargetHost = "https://postman-echo.com",

    [string]$Duration = "60s"
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

function Run-Perf([string]$group, [string]$TargetHost, [string]$duration) {
    if (-not (Test-Path ".\perf\locustfile.py")) {
        throw "perf/locustfile.py not found. Please create .\perf\locustfile.py first"
    }

    # A/B 两组负载（按你现在的口径）
    $users = 10
    $spawn = 2
    $csvPrefix = ".\reports\locust"
    $html = ".\reports\locust.html"

    if ($group -eq "B") {
        $users = 20
        $spawn = 4
        $csvPrefix = ".\reports\locust_B"
        $html = ".\reports\locust_B.html"
    }

    Write-Host "[run] locust group=$group users=$users spawn=$spawn duration=$duration host=$targetHost"
    Write-Host "[run] report -> $html"

    locust -f .\perf\locustfile.py `
        --headless -u $users -r $spawn -t $duration `
        --host $targetHost `
        --csv $csvPrefix `
        --html $html

    Write-Host "[run] perf done -> $html"
}

# perf 模式优先（比卖你你误传 Marker 导致跑 pytest）
if ($Mode -eq "perf") {
    Run-Perf $PerfGroup $TargetHost $Duration
    exit 0
}

# 优先级： Marker 手动指定 > Mode 默认策略
if ($Marker -ne "") {
    $reportName = $(if ($Report -ne "") { $Report } else { "custom.html" })
    Run-Pytest $Marker $reportName
    exit 0
}

switch ($Mode) {
    "lint"    { Run-Lint }
    "unit"    { Run-Pytest "not (network or integration or db)" $(if ($Report -ne "") { $Report } else { "unit.html" }) }
    "network" { Run-Pytest "network or integration" $(if ($Report -ne "") { $Report } else { "network.html" }) }
    "all"     { Run-Lint; Run-Pytest "not (network or integration)" "unit.html"; Run-Pytest "network or integration" "network.html" }
}
