# 人脸识别资料知识库

本知识库用于维护当前文件夹内的人脸识别模组、SDK、调试工具、照片下发与配套驱动资料。

维护方式采用：

- Obsidian：本地编辑、双链、图谱和资料卡管理。
- GitHub：版本管理与一键推送。
- GitHub Pages + Docsify：把 Markdown 和原始附件渲染为在线文档站点。

## 快速入口

- [知识库总览](00-入口/知识库总览.md)
- [资料地图](00-入口/资料地图.md)
- [编辑与发布流程](00-入口/编辑与发布流程.md)
- [PDF 全文索引](60-PDF全文/全文索引.md)
- [附件索引](90-附件/附件索引.md)
- [大文件与发布限制](90-附件/大文件与发布限制.md)

## 资料分区

| 分区 | 内容 |
| --- | --- |
| [硬件规格](10-硬件规格/AI-10.md) | AI-10、AI-10W、FO101-KIT 测试板、结构文件 |
| [软件开发](20-软件开发/软件开发手册.md) | 模组软件开发手册、SDK、JNA 参考、裁剪 SDK |
| [工具与驱动](30-工具与驱动/工具与驱动总览.md) | AI-10 调试工具、串口助手、串口驱动 |
| [照片下发](40-照片下发/照片下发总览.md) | 照片格式要求、照片下发开发手册 |
| [PDF 全文](60-PDF全文/全文索引.md) | 已从全部 PDF 提取的分页全文 Markdown |
| [附件](90-附件/附件索引.md) | 所有原始 PDF、ZIP、RAR 文件清单 |

## 当前资料概况

本次本地扫描时间：2026-06-16。

| 类型 | 数量 | 说明 |
| --- | ---: | --- |
| PDF | 6 | 产品规格、开发手册、图片要求、SDK 文档 |
| PDF 全文页 | 6 | 已提取为 `60-PDF全文` 下的 Markdown |
| ZIP | 4 | 驱动、串口助手、JNA 参考、裁剪 SDK |
| RAR | 2 | AI-10 调试工具、STEP 结构文件 |

原始资料保留在仓库根目录，知识库页面只做索引、关联和发布入口，不改动原文件名。

## 本地使用

1. 用 Obsidian 打开当前文件夹。
2. 从 `README.md` 或 `00-入口/知识库总览.md` 进入。
3. 编辑 Markdown 资料卡时，优先使用相对链接，确保 Docsify 和 Obsidian 都能打开。
4. PDF 有新增或替换后，运行 `scripts/extract-pdf-fulltext.ps1` 重新生成全文页。
5. 运行 `scripts/generate-pdf-preview.ps1` 重新生成在线 PDF 预览图。
6. 发布前运行 `scripts/check-kb.ps1` 检查基础文件、PDF 全文和 PDF 预览是否齐全。

## 在线发布

目标仓库：

```text
https://github.com/likangjie110/Facial-recognition-data-zh-.git
```

GitHub Pages 访问地址：

```text
https://likangjie110.github.io/Facial-recognition-data-zh-/
```

当前发布方式：`main` 分支维护源码和资料，`gh-pages` 分支提供 GitHub Pages 静态站点。

首次推送到 GitHub：

```powershell
.\scripts\publish-github-pages.ps1 -RemoteUrl "https://github.com/likangjie110/Facial-recognition-data-zh-.git"
```

后续更新：

```powershell
.\scripts\publish-github-pages.ps1
```

GitHub Pages 建议配置为从 `main` 分支的 `/root` 目录发布。

当前仓库已推送 `gh-pages` 分支，GitHub Pages 可直接从 `gh-pages` 分支根目录发布。
