[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$IndexPath = Join-Path $Root 'index.html'
$CssPath = Join-Path $Root 'assets/docsify-custom.css'
$ManifestPath = Join-Path $Root 'assets/pdf-preview/manifest.json'

$Index = Get-Content -LiteralPath $IndexPath -Raw
$Css = Get-Content -LiteralPath $CssPath -Raw

$Failures = New-Object System.Collections.Generic.List[string]

foreach ($RequiredText in @(
  'data-pdf-preview',
  'data-pdf-preview-bound',
  'loadPdfPreviewManifest',
  'renderPreviewPage',
  'createPdfViewer',
  'addInlinePdfPreview',
  'pdf-preview-image',
  'manifest.json',
  'pdf-preview-dialog',
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
  '.pdf-preview-image',
  '.pdf-preview-close',
  '.pdf-image-viewer',
  '.pdf-inline-preview',
  '.pdf-page-controls'
)) {
  if ($Css -notmatch [regex]::Escape($RequiredText)) {
    $Failures.Add("assets/docsify-custom.css missing PDF preview style: $RequiredText")
  }
}

if ($Index -match '<iframe class="pdf-preview-frame"') {
  $Failures.Add('index.html still uses iframe-based PDF preview instead of PDF.js canvas rendering')
}

if ($Index -match 'pdfjsLib|getDocument|pdf.worker.min.js') {
  $Failures.Add('index.html still depends on browser-side PDF loading; use generated preview images instead')
}

if (-not (Test-Path -LiteralPath $ManifestPath)) {
  $Failures.Add('assets/pdf-preview/manifest.json is missing')
} else {
  $Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
  $PdfFiles = Get-ChildItem -LiteralPath $Root -File -Filter '*.pdf'
  foreach ($PdfFile in $PdfFiles) {
    $Item = $Manifest.items.PSObject.Properties[$PdfFile.Name]
    if (-not $Item) {
      $Failures.Add("assets/pdf-preview/manifest.json missing PDF entry: $($PdfFile.Name)")
      continue
    }
    if ($Item.Value.pageCount -lt 1 -or $Item.Value.pages.Count -lt 1) {
      $Failures.Add("PDF preview manifest entry has no pages: $($PdfFile.Name)")
      continue
    }
    foreach ($PagePath in $Item.Value.pages) {
      $ResolvedPagePath = Join-Path $Root ($PagePath -replace '/', [IO.Path]::DirectorySeparatorChar)
      if (-not (Test-Path -LiteralPath $ResolvedPagePath)) {
        $Failures.Add("PDF preview image missing: $PagePath")
      }
    }
  }
}

if ($Failures.Count -gt 0) {
  Write-Error ("PDF preview check failed:`n- " + ($Failures -join "`n- "))
}

Write-Host 'PDF preview check passed.'
