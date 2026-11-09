"""Build script for GP Desktop Ultimate AI (PyInstaller).

Gera um arquivo .spec programaticamente e invoca o PyInstaller para produzir
um executável Windows (onefile ou onedir) chamado ``GPDesktopUltimateAI``.

Uso:
    python installer/build.py            # onefile (padrão)
    python installer/build.py --mode onedir
    python installer/build.py --clean
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INSTALLER_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
DEFAULT_NAME = "GPDesktopUltimateAI"

# Módulos de terceiros que o PyInstaller pode não detectar automaticamente.
THIRD_PARTY_HIDDEN = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtNetwork",
    "PySide6.QtSvg",
    "psutil",
    "supabase",
    "postgrest",
    "gotrue",
    "realtime",
    "storage3",
    "supafunc",
    "httpx",
    "httpcore",
    "h11",
    "anyio",
    "sniffio",
    "certifi",
    "charset_normalizer",
    "idna",
    "urllib3",
    "pydantic",
    "typing_extensions",
    "dotenv",
    "keyring",
    "keyring.backends",
    "keyring.backends.Windows",
    "win32cred",
    "win32api",
    "win32con",
    "win32gui",
    "pywintypes",
    "cryptography",
    "cryptography.hazmat",
    "cryptography.hazmat.primitives",
    "PIL",
    "PIL.Image",
    "cv2",
    "win32com",
    "win32com.client",
]


def collect_local_modules() -> list[str]:
    """Descobre todos os módulos locais (pacotes/arquivos .py) do projeto."""
    modules: list[str] = []
    for root, _dirs, files in os.walk(BASE_DIR):
        # ignora pastas de build/cache
        parts = Path(root).relative_to(BASE_DIR).parts
        if any(
            p in {".pytest_cache", ".ruff_cache", "build", "dist", "__pycache__"}
            for p in parts
        ):
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            if f == "__init__.py":
                continue
            rel = Path(root, f).relative_to(BASE_DIR)
            # main.py vira "main"
            module = ".".join(rel.with_suffix("").parts)
            modules.append(module)
    # pacotes (diretórios com __init__.py)
    for root, dirs, files in os.walk(BASE_DIR):
        parts = Path(root).relative_to(BASE_DIR).parts
        if any(
            p in {".pytest_cache", ".ruff_cache", "build", "dist", "__pycache__"}
            for p in parts
        ):
            continue
        if "__init__.py" in files:
            rel = Path(root).relative_to(BASE_DIR)
            if str(rel) == ".":
                continue
            modules.append(".".join(rel.parts))
    # dedup preservando ordem
    seen = set()
    out = []
    for m in modules:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def collect_data_files() -> list[tuple[str, str]]:
    """Coleta arquivos de dados (sql, json, ico, png, etc.) para embutir."""
    data: list[tuple[str, str]] = []
    data_dirs = ["migrations", "assets", "resources", "docs"]
    for d in data_dirs:
        src = BASE_DIR / d
        if src.is_dir():
            for root, _dirs, files in os.walk(src):
                for f in files:
                    full = Path(root) / f
                    rel = full.relative_to(BASE_DIR)
                    dst = str(rel.parent).replace("\\", "/")
                    data.append((str(full), dst))
    # migrations dentro de supabase/
    extra = BASE_DIR / "supabase" / "migrations"
    if extra.is_dir():
        for root, _dirs, files in os.walk(extra):
            for f in files:
                full = Path(root) / f
                rel = full.relative_to(BASE_DIR)
                dst = str(rel.parent).replace("\\", "/")
                data.append((str(full), dst))
    # .env.example
    env_example = BASE_DIR / ".env.example"
    if env_example.is_file():
        data.append((str(env_example), "."))
    return data


def find_icon() -> str | None:
    candidates = [
        BASE_DIR / "assets" / "icon.ico",
        BASE_DIR / "resources" / "icon.ico",
        BASE_DIR / "icon.ico",
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def build_spec(mode: str, name: str) -> Path:
    local_modules = collect_local_modules()
    hidden = THIRD_PARTY_HIDDEN + local_modules
    # remove duplicatas
    seen = set()
    hidden_unique = []
    for h in hidden:
        if h not in seen:
            seen.add(h)
            hidden_unique.append(h)

    datas = collect_data_files()
    icon = find_icon()

    datas_repr = "[" + ", ".join(f"(r'{s}', r'{d}')" for s, d in datas) + "]"
    hidden_repr = "[" + ", ".join(f"'{h}'" for h in hidden_unique) + "]"

    console_flag = "False"  # app GUI (windowed)

    if mode == "onefile":
        exe_block = f"""exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_flag},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={repr(icon)},
)"""
        collect_block = ""
    else:
        exe_block = f"""exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='{name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={console_flag},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={repr(icon)},
)"""
        collect_block = f"""
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{name}',
)"""

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# Gerado automaticamente por installer/build.py
import sys
from pathlib import Path

BASE_DIR = r'{BASE_DIR}'
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

block_cipher = None

a = Analysis(
    [r'{BASE_DIR / "main.py"}'],
    pathex=[r'{BASE_DIR}'],
    binaries=[],
    datas={datas_repr},
    hiddenimports={hidden_repr},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

{exe_block}
{collect_block}
"""

    spec_path = BASE_DIR / f"{name}.spec"
    spec_path.write_text(spec_content, encoding="utf-8")
    return spec_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GP Desktop Ultimate AI")
    parser.add_argument("--mode", choices=["onefile", "onedir"], default="onefile")
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--clean", action="store_true", help="Limpa build/dist antes")
    args = parser.parse_args()

    if args.clean:
        for d in (BUILD_DIR, DIST_DIR):
            if d.exists():
                import shutil

                shutil.rmtree(d)

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print(
            "PyInstaller não instalado. Instale com: pip install pyinstaller",
            file=sys.stderr,
        )
        return 1

    spec_path = build_spec(args.mode, args.name)
    print(f"Spec gerado: {spec_path}")

    import PyInstaller.__main__ as pyi

    pyi.run(
        [
            str(spec_path),
            "--noconfirm",
            "--clean",
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(BUILD_DIR),
        ]
    )
    print(f"Build concluído. Saída em: {DIST_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
