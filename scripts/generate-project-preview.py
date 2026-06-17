from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "50-项目案例" / "源码预览"


@dataclass(frozen=True)
class ProjectPreview:
    title: str
    doc_name: str
    project_dir: str
    description: str


PROJECTS = [
    ProjectPreview(
        title="Java项目文件预览",
        doc_name="Java项目文件预览.md",
        project_dir="examples/java-face-register",
        description="Maven CLI 示例，展示照片注册协议封包和 mock transport 调用链。",
    ),
    ProjectPreview(
        title="Cpp项目文件预览",
        doc_name="Cpp项目文件预览.md",
        project_dir="examples/cpp-face-register",
        description="CMake + C++17 示例，展示协议函数拆分、文件读取和离线 mock 发送。",
    ),
    ProjectPreview(
        title="Qt项目文件预览",
        doc_name="Qt项目文件预览.md",
        project_dir="examples/qt-face-register",
        description="Qt 6 Widgets + SerialPort 示例，展示图形界面、串口发送和 mock 模式。",
    ),
    ProjectPreview(
        title="Python项目文件预览",
        doc_name="Python项目文件预览.md",
        project_dir="examples/python-face-register",
        description="Python CLI 示例，展示标准库封包、mock transport 和 pyserial transport。",
    ),
]

EXCLUDED_DIRS = {"build", "target", "__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".class", ".jar", ".exe", ".dll", ".so", ".dylib"}

LANGUAGE_BY_SUFFIX = {
    ".cpp": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".md": "markdown",
    ".py": "python",
    ".ps1": "powershell",
    ".txt": "text",
    ".xml": "xml",
}


def should_include(project_root: Path, relative_path: Path) -> bool:
    parts = set(relative_path.parts)
    if parts & EXCLUDED_DIRS:
        return False
    if relative_path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return (project_root / relative_path).is_file()


def project_files(project_root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in project_root.rglob("*")
            if should_include(project_root, path.relative_to(project_root))
        ),
        key=lambda item: item.relative_to(project_root).as_posix().casefold(),
    )


def language_for(path: Path) -> str:
    if path.name == "CMakeLists.txt":
        return "cmake"
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "text")


def fence_for(text: str) -> str:
    longest = 0
    current = 0
    for char in text:
        if char == "`":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return "`" * max(3, longest + 1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def build_tree(project_root: Path, files: list[Path]) -> str:
    lines = [project_root.name]

    included = {file_path.relative_to(project_root) for file_path in files}

    def walk(directory: Path, depth: int) -> None:
        children = []
        for child in directory.iterdir():
            relative = child.relative_to(project_root)
            if child.is_dir():
                if child.name in EXCLUDED_DIRS:
                    continue
                if any(item.parts[: len(relative.parts)] == relative.parts for item in included):
                    children.append(child)
            elif relative in included:
                children.append(child)

        children.sort(key=lambda item: (item.is_file(), item.name.casefold()))
        for child in children:
            suffix = "/" if child.is_dir() else ""
            lines.append(f"{'  ' * depth}- {child.name}{suffix}")
            if child.is_dir():
                walk(child, depth + 1)

    walk(project_root, 1)
    return "\n".join(lines)


def render_project(project: ProjectPreview) -> str:
    project_root = ROOT / project.project_dir
    files = project_files(project_root)
    lines = [
        f"# {project.title}",
        "",
        project.description,
        "",
        f"工程位置：`{project.project_dir}`",
        "",
        "## 项目结构",
        "",
        "```text",
        build_tree(project_root, files),
        "```",
        "",
        "## 文件内容",
        "",
    ]

    for file_path in files:
        relative_path = file_path.relative_to(project_root).as_posix()
        text = read_text(file_path)
        fence = fence_for(text)
        lines.extend(
            [
                f"### `{relative_path}`",
                "",
                f"{fence}{language_for(file_path)}",
                text.rstrip(),
                fence,
                "",
            ]
        )

    lines.extend(
        [
            "## 返回",
            "",
            "- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)",
            "- [项目案例总览](/50-项目案例/项目案例总览.md)",
            "",
        ]
    )
    return "\n".join(lines)


def render_index() -> str:
    lines = [
        "# 项目文件预览索引",
        "",
        "这里集中预览 Java、C++、Qt、Python 四个完整调用项目的目录结构和全部文件内容。",
        "",
        "## 预览入口",
        "",
    ]
    for project in PROJECTS:
        lines.append(f"- [{project.title}](/50-项目案例/源码预览/{project.doc_name})：`{project.project_dir}`")
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 预览内容由 `scripts/generate-project-preview.py` 生成。",
            "- `build`、`target`、`__pycache__` 等本地构建产物不会进入预览页。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "项目文件预览索引.md").write_text(render_index(), encoding="utf-8")

    for project in PROJECTS:
        (OUTPUT_DIR / project.doc_name).write_text(render_project(project), encoding="utf-8")

    print(f"Generated project preview pages: {len(PROJECTS) + 1}")
    print(f"Output: {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
