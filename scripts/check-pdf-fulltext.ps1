[CmdletBinding()]
param(
  [int]$MinimumCharactersPerPdf = 20
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$IndexPath = Join-Path $Root '60-PDF全文/全文索引.md'
if (-not (Test-Path -LiteralPath $IndexPath)) {
  Write-Error 'PDF full-text check failed: Missing full-text index: 60-PDF全文/全文索引.md'
}

$ExpectedFullTextFiles = @(
  '60-PDF全文/AI-10SDK-全文.md',
  '60-PDF全文/AI视觉算法模组产品规格书AI-10_V1.1-20250731-全文.md',
  '60-PDF全文/AI视觉算法模组产品规格书（AI-10W）V1.0-20250812(海外版)-全文.md',
  '60-PDF全文/FO101-KIT人脸模组测试板工具板规格书V1.1-20250514-全文.md',
  '60-PDF全文/照片下发图片要求2024_250305-全文.md',
  '60-PDF全文/照片下发系列人脸识别模组用户软件开发手册V2.63-20250828-20250917-全文.md'
)

$Failures = New-Object System.Collections.Generic.List[string]

foreach ($RelativePath in $ExpectedFullTextFiles) {
  $FullPath = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $FullPath)) {
    $Failures.Add("Missing full-text page: $RelativePath")
    continue
  }

  $Content = Get-Content -LiteralPath $FullPath -Raw
  if ($Content -notmatch '## 提取状态') {
    $Failures.Add("Missing extraction status section: $RelativePath")
  }
  if ($Content -notmatch '## 全文内容') {
    $Failures.Add("Missing full text section: $RelativePath")
  }
  if ($Content -notmatch '### 第\s+1\s+页') {
    $Failures.Add("Missing page 1 heading: $RelativePath")
  }

  $TextMatch = [regex]::Match($Content, '<!-- extracted-text-start -->(?<text>[\s\S]*?)<!-- extracted-text-end -->')
  if (-not $TextMatch.Success) {
    $Failures.Add("Missing extracted text markers: $RelativePath")
    continue
  }

  $ExtractedText = $TextMatch.Groups['text'].Value.Trim()
  if ($ExtractedText.Length -lt $MinimumCharactersPerPdf) {
    $Failures.Add("Extracted text too short ($($ExtractedText.Length) chars): $RelativePath")
  }
}

if ($Failures.Count -gt 0) {
  Write-Error ("PDF full-text check failed:`n- " + ($Failures -join "`n- "))
}

Write-Host 'PDF full-text check passed.'
Write-Host "Full-text pages: $($ExpectedFullTextFiles.Count)"
