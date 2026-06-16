[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$IndexPath = Join-Path $Root 'index.html'
$CssPath = Join-Path $Root 'assets/docsify-custom.css'

$Index = Get-Content -LiteralPath $IndexPath -Raw
$Css = Get-Content -LiteralPath $CssPath -Raw

$Failures = New-Object System.Collections.Generic.List[string]

foreach ($RequiredText in @(
  'data-pdf-preview',
  'pdf-preview-dialog',
  'pdf-preview-frame',
  'openPdfPreview',
  'closePdfPreview',
  'stopImmediatePropagation'
)) {
  if ($Index -notmatch [regex]::Escape($RequiredText)) {
    $Failures.Add("index.html missing PDF preview behavior: $RequiredText")
  }
}

foreach ($RequiredText in @(
  '.pdf-preview-dialog',
  '.pdf-preview-shell',
  '.pdf-preview-frame',
  '.pdf-preview-close'
)) {
  if ($Css -notmatch [regex]::Escape($RequiredText)) {
    $Failures.Add("assets/docsify-custom.css missing PDF preview style: $RequiredText")
  }
}

if ($Failures.Count -gt 0) {
  Write-Error ("PDF preview check failed:`n- " + ($Failures -join "`n- "))
}

Write-Host 'PDF preview check passed.'
