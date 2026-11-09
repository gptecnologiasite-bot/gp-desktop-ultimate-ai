"""Operações de arquivo: busca, organização e exclusão."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

DEFAULT_EXT_MAP = {
    "Imagens": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"],
    "Documentos": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    ],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "Arquivos": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Codigo": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml"],
}


def find_files(
    root: str, pattern: str = "*", recursive: bool = True, max_results: int = 10000
) -> List[str]:
    """Busca arquivos por padrão (glob)."""
    base = Path(root)
    results: List[str] = []
    if not base.exists():
        return results
    iterator = base.rglob(pattern) if recursive else base.glob(pattern)
    for p in iterator:
        if p.is_file():
            results.append(str(p))
            if len(results) >= max_results:
                break
    return results


def _category_for_ext(ext: str, mapping: Optional[Dict[str, List[str]]] = None) -> str:
    m = mapping or DEFAULT_EXT_MAP
    low = ext.lower()
    for category, exts in m.items():
        if low in [e.lower() for e in exts]:
            return category
    return "Outros"


def organize_folder(
    folder: str, mapping: Optional[Dict[str, List[str]]] = None, dry_run: bool = False
) -> Dict[str, Any]:
    """Organiza arquivos de uma pasta em subpastas por extensão."""
    base = Path(folder)
    summary: Dict[str, Any] = {"moved": 0, "skipped": 0, "errors": [], "details": []}
    if not base.is_dir():
        summary["errors"].append("Pasta não existe")
        return summary
    for item in list(base.iterdir()):
        if not item.is_file():
            continue
        category = _category_for_ext(item.suffix, mapping)
        target_dir = base / category
        target = target_dir / item.name
        # evitar sobrescrever
        if target.exists() and target != item:
            stem = item.stem
            suffix = item.suffix
            i = 1
            while (base / category / f"{stem}_{i}{suffix}").exists():
                i += 1
            target = base / category / f"{stem}_{i}{suffix}"
        if dry_run:
            summary["details"].append({"from": str(item), "to": str(target)})
            summary["moved"] += 1
            continue
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(target))
            summary["moved"] += 1
            summary["details"].append({"from": str(item), "to": str(target)})
        except Exception as e:
            summary["errors"].append(str(e))
            summary["skipped"] += 1
    return summary


def delete_file(path: str, confirm: Optional[Callable[[str], bool]] = None) -> bool:
    """Exclui arquivo. Se confirm fornecido, exige True."""
    p = Path(path)
    if not p.exists():
        return False
    if confirm is not None and not confirm(str(p)):
        return False
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return True
    except Exception:
        return False
