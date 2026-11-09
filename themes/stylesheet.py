"""Geração de QSS (Qt StyleSheet) a partir de um tema."""

from __future__ import annotations

from typing import Any, Dict

from .theme_definitions import THEMES, get_theme, REQUIRED_COLOR_KEYS


def _resolve_theme(theme: Any) -> Dict[str, str]:
    if isinstance(theme, str):
        return get_theme(theme)
    if isinstance(theme, dict):
        if all(k in theme for k in REQUIRED_COLOR_KEYS):
            return {k: str(theme[k]) for k in REQUIRED_COLOR_KEYS}
        # pode ser um dict aninhado com "colors"
        for key in ("colors", "palette", "theme"):
            if isinstance(theme.get(key), dict):
                nested = theme[key]
                if all(k in nested for k in REQUIRED_COLOR_KEYS):
                    return {k: str(nested[k]) for k in REQUIRED_COLOR_KEYS}
        # tenta mapear chaves presentes
        result = {}
        for k in REQUIRED_COLOR_KEYS:
            if k in theme:
                result[k] = str(theme[k])
        if result:
            # completa com defaults do tema claro
            base = dict(THEMES["claro"])
            base.update(result)
            return base
    # objeto com atributo colors
    colors = getattr(theme, "colors", None) or getattr(theme, "palette", None)
    if isinstance(colors, dict):
        return _resolve_theme(colors)
    # fallback
    return dict(THEMES["claro"])


def build_qss(theme: Any) -> str:
    """Gera uma QSS completa com base nas cores do tema."""
    c = _resolve_theme(theme)
    bg = c["background"]
    surface = c["surface"]
    text = c["text"]
    accent = c["accent"]
    menu = c["menu"]
    button = c["button"]
    border = c["border"]

    return f"""
/* GP Desktop Ultimate AI - tema gerado */
QMainWindow, QWidget {{
    background-color: {bg};
    color: {text};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 10pt;
}}

QMainWindow::separator {{
    background: {border};
    width: 1px;
    height: 1px;
}}

/* Sidebar / menu lateral */
QWidget#sidebar, QFrame#sidebar, .QSidebar {{
    background-color: {menu};
    border-right: 1px solid {border};
}}

QListWidget#menu, QTreeWidget#menu {{
    background-color: {menu};
    border: none;
    color: {text};
    outline: 0;
}}

QListWidget#menu::item, QTreeWidget#menu::item {{
    padding: 8px 12px;
    border-radius: 6px;
}}

QListWidget#menu::item:selected, QTreeWidget#menu::item:selected {{
    background-color: {accent};
    color: {bg};
}}

/* Botões */
QPushButton {{
    background-color: {button};
    color: {bg};
    border: 1px solid {button};
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {accent};
    border-color: {accent};
}}

QPushButton:pressed {{
    background-color: {surface};
    color: {text};
}}

QPushButton:disabled {{
    background-color: {surface};
    color: {border};
    border-color: {border};
}}

/* Campos de entrada */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: {accent};
    selection-color: {bg};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border: 1px solid {accent};
}}

/* Cards / painéis */
QFrame#card, QWidget#card, .Card {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 12px;
}}

QGroupBox {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: {accent};
}}

/* Tabelas / listas */
QTableView, QListView, QTreeView {{
    background-color: {surface};
    alternate-background-color: {bg};
    color: {text};
    gridline-color: {border};
    border: 1px solid {border};
    border-radius: 6px;
}}

QHeaderView::section {{
    background-color: {menu};
    color: {text};
    border: 1px solid {border};
    padding: 4px 8px;
    font-weight: 600;
}}

/* Abas */
QTabWidget::pane {{
    border: 1px solid {border};
    background-color: {surface};
}}

QTabBar::tab {{
    background-color: {menu};
    color: {text};
    padding: 6px 12px;
    border: 1px solid {border};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {surface};
    color: {accent};
    font-weight: 600;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {bg};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {accent};
}}

QScrollBar:horizontal {{
    background: {bg};
    height: 10px;
}}

QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 5px;
    min-width: 20px;
}}

/* Menus / toolbar */
QMenuBar {{
    background-color: {menu};
    color: {text};
}}

QMenuBar::item:selected {{
    background-color: {accent};
    color: {bg};
}}

QMenu {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
}}

QMenu::item:selected {{
    background-color: {accent};
    color: {bg};
}}

QToolBar {{
    background-color: {menu};
    border-bottom: 1px solid {border};
}}

QStatusBar {{
    background-color: {menu};
    color: {text};
}}

QToolTip {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    padding: 4px;
}}

/* Labels de destaque */
QLabel#title {{
    color: {accent};
    font-size: 14pt;
    font-weight: 700;
}}

QLabel#muted {{
    color: {border};
}}
"""
