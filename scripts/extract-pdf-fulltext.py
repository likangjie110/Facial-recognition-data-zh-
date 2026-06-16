from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


try:
    import pdfplumber
except ImportError:  # pragma: no cover - checked at runtime
    pdfplumber = None

try:
    import fitz
except ImportError:  # pragma: no cover - checked at runtime
    fitz = None


OUTPUT_DIR_NAME = "60-PDF全文"
INDEX_FILE_NAME = "全文索引.md"
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str
    method: str


@dataclass(frozen=True)
class PdfExtraction:
    source_path: Path
    output_path: Path
    page_count: int
    extracted_characters: int
    empty_pages: int
    methods: str


def clean_output_stem(pdf_path: Path) -> str:
    stem = pdf_path.stem.strip()
    stem = INVALID_FILENAME_CHARS.sub("-", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or "untitled"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines).strip()
    return re.sub(r"\n{4,}", "\n\n\n", text)


def extract_with_pdfplumber(pdf_path: Path) -> list[str]:
    if pdfplumber is None:
        return []

    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            pages.append(normalize_text(page.extract_text() or ""))
    return pages


def extract_with_fitz(pdf_path: Path) -> list[str]:
    if fitz is None:
        return []

    pages: list[str] = []
    doc = fitz.open(str(pdf_path))
    try:
        for page in doc:
            pages.append(normalize_text(page.get_text("text") or ""))
    finally:
        doc.close()
    return pages


def choose_pages(pdf_path: Path) -> list[PageText]:
    plumber_pages = extract_with_pdfplumber(pdf_path)
    fitz_pages = extract_with_fitz(pdf_path)

    page_count = max(len(plumber_pages), len(fitz_pages))
    pages: list[PageText] = []
    for index in range(page_count):
        plumber_text = plumber_pages[index] if index < len(plumber_pages) else ""
        fitz_text = fitz_pages[index] if index < len(fitz_pages) else ""

        if len(fitz_text) > len(plumber_text):
            text = fitz_text
            method = "fitz"
        else:
            text = plumber_text
            method = "pdfplumber"

        if not text:
            text = "【未提取到可复制文本】"
            method = "none"

        pages.append(PageText(page_number=index + 1, text=text, method=method))
    return pages


def markdown_link(target: str, label: str) -> str:
    return f"[{label}](<{target}>)"


def render_pdf_page(pdf_path: Path, output_path: Path, pages: list[PageText], generated_at: str) -> str:
    title = pdf_path.stem.strip()
    methods = sorted({page.method for page in pages})
    extracted_characters = sum(len(page.text) for page in pages if page.method != "none")
    empty_pages = sum(1 for page in pages if page.method == "none")
    source_link = markdown_link("../" + pdf_path.name, pdf_path.name)

    lines = [
        f"# {title} 全文",
        "",
        "标签：#PDF全文 #自动提取 #原始资料",
        "",
        "> 本页由 `scripts/extract-pdf-fulltext.py` 从原始 PDF 自动提取。全文内容保留分页结构，仍建议对关键参数回看原始 PDF。",
        "",
        "## 提取状态",
        "",
        "| 字段 | 值 |",
        "| --- | --- |",
        f"| 原始 PDF | {source_link} |",
        f"| 输出文件 | `{output_path.as_posix()}` |",
        f"| 页数 | {len(pages)} |",
        f"| 提取字符数 | {extracted_characters} |",
        f"| 未提取到文本页数 | {empty_pages} |",
        f"| 提取方式 | {', '.join(methods)} |",
        f"| 生成时间 | {generated_at} |",
        "",
        "## 全文内容",
        "",
        "<!-- extracted-text-start -->",
        "",
    ]

    for page in pages:
        lines.extend(
            [
                f"### 第 {page.page_number} 页",
                "",
                "````text",
                page.text,
                "````",
                "",
            ]
        )

    lines.extend(["<!-- extracted-text-end -->", ""])
    return "\n".join(lines)


def render_index(extractions: Iterable[PdfExtraction], generated_at: str) -> str:
    rows = []
    for item in extractions:
        source_link = markdown_link("../" + item.source_path.name, item.source_path.name)
        output_name = item.output_path.name
        output_link = f"[{output_name}](/60-PDF全文/{output_name})"
        rows.append(
            f"| {source_link} | {output_link} | {item.page_count} | {item.extracted_characters} | {item.empty_pages} | {item.methods} |"
        )

    return "\n".join(
        [
            "# PDF 全文索引",
            "",
            "标签：#PDF全文 #索引 #自动提取",
            "",
            f"生成时间：{generated_at}",
            "",
            "本页索引从根目录 PDF 自动提取出来的全文 Markdown。每个全文页保留分页结构，并链接回原始 PDF。",
            "",
            "| 原始 PDF | 全文页 | 页数 | 提取字符数 | 未提取页数 | 提取方式 |",
            "| --- | --- | ---: | ---: | ---: | --- |",
            *rows,
            "",
        ]
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def extract_all(root: Path) -> list[PdfExtraction]:
    output_dir = root / OUTPUT_DIR_NAME
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_paths = sorted(root.glob("*.pdf"), key=lambda path: path.name.casefold())

    if not pdf_paths:
        raise SystemExit("No PDF files found in repository root.")
    if pdfplumber is None and fitz is None:
        raise SystemExit("Install pdfplumber or PyMuPDF (fitz) before extracting PDF text.")

    extractions: list[PdfExtraction] = []
    for pdf_path in pdf_paths:
        output_name = f"{clean_output_stem(pdf_path)}-全文.md"
        output_path = output_dir / output_name
        pages = choose_pages(pdf_path)
        content = render_pdf_page(pdf_path, output_path.relative_to(root), pages, generated_at)
        write_text(output_path, content)

        method_set = sorted({page.method for page in pages})
        extractions.append(
            PdfExtraction(
                source_path=pdf_path,
                output_path=output_path.relative_to(output_dir),
                page_count=len(pages),
                extracted_characters=sum(len(page.text) for page in pages if page.method != "none"),
                empty_pages=sum(1 for page in pages if page.method == "none"),
                methods=", ".join(method_set),
            )
        )

    index_content = render_index(extractions, generated_at)
    write_text(output_dir / INDEX_FILE_NAME, index_content)
    return extractions


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract all root PDF files into Markdown full-text pages.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    root = args.root.resolve()
    extractions = extract_all(root)
    print(json.dumps([item.__dict__ | {"source_path": item.source_path.name, "output_path": str(item.output_path)} for item in extractions], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
