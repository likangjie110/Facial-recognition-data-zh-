[CmdletBinding()]
param(
  [int]$Port = 4180
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $Root

Write-Host "Serving Docsify knowledge base from $Root"
Write-Host "Open http://localhost:$Port in your browser."

python -m http.server $Port
