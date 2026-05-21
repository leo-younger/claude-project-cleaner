# Claude Project Cleaner — One-click install (Windows PowerShell)
# Usage: .\install.ps1 [-Global] [-Project <path>]

param(
    [switch]$Global,
    [string]$Project
)

$SKILL_NAME = "claude-project-cleaner"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Project) {
    $INSTALL_TARGET = Join-Path $Project ".claude\skills\$SKILL_NAME"
} elseif ($Global) {
    $INSTALL_TARGET = "$env:USERPROFILE\.claude\skills\$SKILL_NAME"
} elseif (Test-Path "$PWD\.claude") {
    $INSTALL_TARGET = "$PWD\.claude\skills\$SKILL_NAME"
} else {
    $INSTALL_TARGET = "$env:USERPROFILE\.claude\skills\$SKILL_NAME"
}

Write-Host "Installing $SKILL_NAME to: $INSTALL_TARGET" -ForegroundColor Cyan

# Remove old install
if (Test-Path $INSTALL_TARGET) {
    Remove-Item -Recurse -Force $INSTALL_TARGET
}

# Copy skill files
New-Item -ItemType Directory -Force -Path (Split-Path $INSTALL_TARGET) | Out-Null
Copy-Item -Recurse -Force "$SCRIPT_DIR\*" $INSTALL_TARGET

# Remove .git if copied
$gitDir = Join-Path $INSTALL_TARGET ".git"
if (Test-Path $gitDir) {
    Remove-Item -Recurse -Force $gitDir
}

Write-Host "Installed! Trigger Claude Code with: /cleanup" -ForegroundColor Green
Write-Host "  Or run: cd $INSTALL_TARGET\scripts; python scanner.py"
