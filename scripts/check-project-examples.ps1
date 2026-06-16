[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$RequiredFiles = @(
  '50-项目案例/项目案例总览.md',
  '50-项目案例/Java完整项目.md',
  '50-项目案例/Cpp完整项目.md',
  '50-项目案例/Qt完整项目.md',
  '50-项目案例/Python完整项目.md',
  'examples/java-face-register/README.md',
  'examples/java-face-register/pom.xml',
  'examples/java-face-register/src/main/java/com/aegis/face/Main.java',
  'examples/java-face-register/src/main/java/com/aegis/face/FaceProtocol.java',
  'examples/cpp-face-register/README.md',
  'examples/cpp-face-register/CMakeLists.txt',
  'examples/cpp-face-register/src/main.cpp',
  'examples/cpp-face-register/src/face_protocol.hpp',
  'examples/cpp-face-register/src/face_protocol.cpp',
  'examples/qt-face-register/README.md',
  'examples/qt-face-register/CMakeLists.txt',
  'examples/qt-face-register/src/main.cpp',
  'examples/qt-face-register/src/mainwindow.h',
  'examples/qt-face-register/src/mainwindow.cpp',
  'examples/python-face-register/README.md',
  'examples/python-face-register/requirements.txt',
  'examples/python-face-register/src/face_protocol.py',
  'examples/python-face-register/src/main.py'
)

$RequiredNavigation = @(
  '50-项目案例/项目案例总览.md',
  '50-项目案例/Java完整项目.md',
  '50-项目案例/Cpp完整项目.md',
  '50-项目案例/Qt完整项目.md',
  '50-项目案例/Python完整项目.md'
)

$Failures = New-Object System.Collections.Generic.List[string]

foreach ($RelativePath in $RequiredFiles) {
  if (-not (Test-Path -LiteralPath (Join-Path $Root $RelativePath))) {
    $Failures.Add("missing project example file: $RelativePath")
  }
}

$Sidebar = Get-Content -LiteralPath (Join-Path $Root '_sidebar.md') -Raw
foreach ($RelativePath in $RequiredNavigation) {
  if ($Sidebar -notmatch [regex]::Escape($RelativePath)) {
    $Failures.Add("_sidebar.md missing project example navigation: $RelativePath")
  }
}

$Overview = Join-Path $Root '50-项目案例/项目案例总览.md'
if (Test-Path -LiteralPath $Overview) {
  $OverviewText = Get-Content -LiteralPath $Overview -Raw
  foreach ($Keyword in @('Java', 'C++', 'Qt', 'Python', '0xEF 0xAA', '246 byte')) {
    if ($OverviewText -notmatch [regex]::Escape($Keyword)) {
      $Failures.Add("project examples overview missing keyword: $Keyword")
    }
  }
}

foreach ($RelativePath in @('README.md', '00-入口/资料地图.md', '00-入口/知识库总览.md', '20-软件开发/软件开发手册.md')) {
  $Text = Get-Content -LiteralPath (Join-Path $Root $RelativePath) -Raw
  if ($Text -notmatch [regex]::Escape('50-项目案例/项目案例总览.md') -and $RelativePath -ne '20-软件开发/软件开发手册.md') {
    $Failures.Add("$RelativePath missing project examples overview link")
  }
  if ($RelativePath -eq '20-软件开发/软件开发手册.md' -and $Text -notmatch [regex]::Escape('50-项目案例/Java完整项目.md')) {
    $Failures.Add("$RelativePath missing language project example links")
  }
}

if ($Failures.Count -gt 0) {
  Write-Error ("Project examples check failed:`n- " + ($Failures -join "`n- "))
}

Write-Host 'Project examples check passed.'
