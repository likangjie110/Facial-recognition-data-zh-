[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

python (Join-Path $PSScriptRoot 'extract-pdf-fulltext.py') --root $Root

