from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = ROOT / "assets" / "pdf-preview"
TARGET_WIDTH = 1200
JPG_QUALITY = 82


def make_slug(file_name: str) -> str:
    stem = Path(file_name).stem
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-")[:40] or "pdf"
    digest = hashlib.sha1(file_name.encode("utf-8")).hexdigest()[:8]
    return f"{safe}-{digest}"


def render_pdf(pdf_path: Path, output_dir: Path) -> dict:
    doc = fitz.open(pdf_path)
    pages: list[str] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for page_index, page in enumerate(doc, start=1):
        scale = min(2.0, max(1.0, TARGET_WIDTH / page.rect.width))
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        image_path = output_dir / f"page-{page_index:03d}.jpg"
        pixmap.save(image_path, jpg_quality=JPG_QUALITY)
        pages.append(image_path.relative_to(ROOT).as_posix())

    return {
        "title": pdf_path.name,
        "pageCount": len(pages),
        "pages": pages,
    }


def main() -> None:
    pdf_files = sorted(ROOT.glob("*.pdf"), key=lambda item: item.name.casefold())
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    manifest = {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "items": {},
    }

    for pdf_path in pdf_files:
        slug = make_slug(pdf_path.name)
        manifest["items"][pdf_path.name] = render_pdf(pdf_path, OUTPUT_ROOT / slug)

    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated preview images for {len(pdf_files)} PDF files.")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
