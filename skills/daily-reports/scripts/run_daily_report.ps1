param(
    [string]$ProjectDir = "D:\DailyReports",
    [string]$OutputDir = "D:\DailyReports",
    [string]$Date = "",
    [switch]$DryRun,
    [switch]$Sample,
    [switch]$NoNotify
)

$config = Join-Path $ProjectDir "config\default_config.json"

$arguments = @(
    "-m",
    "daily_research_report",
    "--config",
    $config,
    "--output-dir",
    $OutputDir
)

if ($Date) {
    $arguments += @("--date", $Date)
}

if ($DryRun) {
    $arguments += "--dry-run"
}

if ($Sample) {
    $arguments += "--sample"
}

if ($NoNotify) {
    $arguments += "--no-notify"
}

Push-Location -LiteralPath $ProjectDir
try {
    & python @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
