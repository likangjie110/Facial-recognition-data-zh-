[CmdletBinding()]
param(
  [string]$RemoteUrl,
  [string]$Branch = 'main',
  [string]$PagesBranch = 'gh-pages',
  [string]$Message = 'docs: update face recognition knowledge base',
  [switch]$SkipPush,
  [switch]$SkipPagesBranch
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $Root

Get-Command git -ErrorAction Stop | Out-Null

& (Join-Path $PSScriptRoot 'check-kb.ps1')

$LargeFiles = Get-ChildItem -LiteralPath $Root -File |
  Where-Object { $_.Length -gt 50MB } |
  Sort-Object Length -Descending

foreach ($File in $LargeFiles) {
  $SizeMb = [Math]::Round($File.Length / 1MB, 2)
  Write-Warning "$($File.Name) is $SizeMb MB. GitHub may warn for files over 50 MB."
}

if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) {
  & git init --initial-branch=$Branch
  if ($LASTEXITCODE -ne 0) {
    & git init
    & git branch -M $Branch
  }
}

if ($RemoteUrl) {
  $ExistingOrigin = & git remote get-url origin 2>$null
  if ($LASTEXITCODE -eq 0 -and $ExistingOrigin) {
    & git remote set-url origin $RemoteUrl
  } else {
    & git remote add origin $RemoteUrl
  }
}

$CurrentBranch = & git branch --show-current
if ($CurrentBranch -and $CurrentBranch -ne $Branch) {
  Write-Warning "Current branch is '$CurrentBranch', but target branch is '$Branch'. The script will not switch branches automatically."
}

& git add -A

$Status = & git status --porcelain
if (-not $Status) {
  Write-Host 'No changes to publish.'
  exit 0
}

& git commit -m $Message

if ($SkipPush) {
  Write-Host 'SkipPush was set. Local commit created, push skipped.'
  exit 0
}

$Origin = & git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or -not $Origin) {
  Write-Warning 'No origin remote configured. Re-run with -RemoteUrl or add origin manually before pushing.'
  exit 0
}

& git push -u origin $Branch

if (-not $SkipPagesBranch) {
  & git push origin "${Branch}:$PagesBranch"
}
