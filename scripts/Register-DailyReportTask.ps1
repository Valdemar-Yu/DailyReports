param(
    [string]$ProjectDir = "D:\DailyReports",
    [string]$Python = "python",
    [string]$At = "08:30"
)

$config = Join-Path $ProjectDir "config\default_config.json"
$argument = "-m daily_research_report --config `"$config`" --output-dir `"D:\DailyReports`""

$action = New-ScheduledTaskAction -Execute $Python -Argument $argument -WorkingDirectory $ProjectDir
$trigger = New-ScheduledTaskTrigger -Daily -At $At

Register-ScheduledTask `
    -TaskName "DailyResearchReport" `
    -Action $action `
    -Trigger $trigger `
    -Description "Generate daily AI research frontier report." `
    -Force
