[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ScriptPath = Join-Path $PSScriptRoot 'generate-project-preview.py'
python $ScriptPath
