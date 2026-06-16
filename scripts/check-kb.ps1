[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$RequiredSiteFiles = @(
  'index.html',
  'README.md',
  '_sidebar.md',
  '_navbar.md',
  '_coverpage.md',
  '.nojekyll',
  'assets/docsify-custom.css',
  '00-入口/知识库总览.md',
  '00-入口/资料地图.md',
  '00-入口/编辑与发布流程.md',
  '60-PDF全文/全文索引.md',
  '90-附件/附件索引.md'
)

$RequiredScriptFiles = @(
  'scripts/extract-pdf-fulltext.py',
  'scripts/extract-pdf-fulltext.ps1',
  'scripts/check-pdf-fulltext.ps1',
  'scripts/check-pdf-preview.ps1',
  'scripts/generate-pdf-preview.py',
  'scripts/generate-pdf-preview.ps1'
)

$RequiredSourceFiles = @(
  'AI-10SDK .pdf',
  'AI-10.stp.rar',
  'AI-10-Tool-1.86-VSIR.rar',
  'AI视觉算法模组产品规格书AI-10_V1.1-20250731.pdf',
  'AI视觉算法模组产品规格书（AI-10W）V1.0-20250812(海外版).pdf',
  'FO101-KIT人脸模组测试板工具板规格书V1.1-20250514.pdf',
  'THFaceCropper-SDK-aarch64linux-V4.10.0.35-NT.zip',
  'java参考JNA_2.zip',
  '串口助手_sscom5.13.1.zip',
  '串口驱动.zip',
  '照片下发图片要求2024_250305 .pdf',
  '照片下发系列人脸识别模组用户软件开发手册V2.63-20250828-20250917.pdf'
)

$Missing = New-Object System.Collections.Generic.List[string]

foreach ($RelativePath in ($RequiredSiteFiles + $RequiredScriptFiles + $RequiredSourceFiles)) {
  $FullPath = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $FullPath)) {
    $Missing.Add($RelativePath)
  }
}

if ($Missing.Count -gt 0) {
  Write-Error ("Knowledge base check failed. Missing files:`n- " + ($Missing -join "`n- "))
}

$MarkdownCount = (Get-ChildItem -LiteralPath $Root -Recurse -File -Filter '*.md' |
  Where-Object { $_.FullName -notmatch '\\.git\\' }).Count

$SourceCount = $RequiredSourceFiles.Count

& (Join-Path $PSScriptRoot 'check-pdf-fulltext.ps1')
& (Join-Path $PSScriptRoot 'check-pdf-preview.ps1')

Write-Host "Knowledge base check passed."
Write-Host "Markdown files: $MarkdownCount"
Write-Host "Indexed source files: $SourceCount"
