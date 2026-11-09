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
        for key in ("colors", "palette", "theme"):
            if isinstance(theme.get(key), dict):
                nested = theme[key]
                if all(k in nested for k in REQUIRED_COLOR_KEYS):
                    return {k: str(nested[k]) for k in REQUIRED_COLOR_KEYS}
        result = {}
        for k in REQUIRED_COLOR_KEYS:
            if k in theme:
                result[k] = str(theme[k])
        if result:
            base = dict(THEMES["claro"])
            base.update(result)
            return base
    colors = getattr(theme, "colors", None) or getattr(theme, "palette", None)
    if isinstance(colors, dict):
        return _resolve_theme(colors)
    return dict(THEMES["claro"])


def build_qss(theme: Any) -> str:
    """Gera uma QSS completa, futurista, com gradientes e neon."""
    c = _resolve_theme(theme)
    bg = c["background"]
    surface = c["surface"]
    text = c["text"]
    accent = c["accent"]
    menu = c["menu"]
    button = c["button"]
    border = c["border"]

    return f"""
/* GP Desktop Ultimate AI - tema futurista */
* {{
    font-family: "Segoe UI Variable", "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
}}

QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {bg}, stop:0.5 {surface}, stop:1 {bg});
}}

QWidget {{
    background-color: transparent;
    color: {text};
    font-size: 10pt;
}}

QWidget#central, QWidget#page {{
    background: transparent;
}}

/* Sidebar */
QWidget#sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {menu}, stop:1 {bg});
    border-right: 1px solid {border};
}}

QFrame#sidebarHeader {{
    background: transparent;
    border-bottom: 1px solid {border};
    padding-bottom: 8px;
}}

QLabel#logoBadge {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {accent}, stop:1 {button});
    color: {bg};
    border-radius: 12px;
    font-size: 14pt;
    font-weight: 800;
}}

QLabel#sidebarTitle {{
    color: {text};
    font-size: 13pt;
    font-weight: 700;
}}

QLabel#sidebarSubtitle {{
    color: {accent};
    font-size: 9pt;
    font-weight: 600;
}}

QLabel#sidebarFooter {{
    color: {border};
    font-size: 8pt;
}}

QListWidget#menu {{
    background: transparent;
    border: none;
    outline: 0;
    padding: 4px;
}}

QListWidget#menu::item {{
    color: {text};
    padding: 10px 12px;
    margin: 3px 2px;
    border-radius: 10px;
    border: 1px solid transparent;
    font-weight: 500;
}}

QListWidget#menu::item:hover {{
    background-color: {surface};
    border: 1px solid {border};
    color: {accent};
}}

QListWidget#menu::item:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {accent}, stop:1 {button});
    color: {bg};
    font-weight: 700;
    border: 1px solid {accent};
}}

QListWidget#menu::item:selected:hover {{
    color: {bg};
}}

/* Conteúdo */
QLabel#title {{
    color: {accent};
    font-size: 18pt;
    font-weight: 800;
    letter-spacing: 0.5px;
}}

QLabel#muted {{
    color: {border};
    font-size: 10pt;
}}

/* Cards */
QFrame#card {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {surface}, stop:1 {bg});
    border: 1px solid {border};
    border-radius: 16px;
}}

/* Botões */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {button}, stop:1 {accent});
    color: {bg};
    border: none;
    border-radius: 10px;
    padding: 8px 18px;
    font-weight: 700;
    font-size: 10pt;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {accent}, stop:1 {button});
    border: 1px solid {accent};
}}

QPushButton:pressed {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
}}

QPushButton:disabled {{
    background-color: {surface};
    color: {border};
    border: 1px solid {border};
}}

QPushButton#btnPrimary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {accent}, stop:1 {button});
}}

QPushButton#btnSuccess {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #22c55e, stop:1 {accent});
    color: #0b1020;
}}

QPushButton#btnDanger {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ef4444, stop:1 #b91c1c);
    color: #ffffff;
}}

/* Campos */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QSlider {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {accent};
    selection-color: {bg};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border: 1px solid {accent};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {surface};
    color: {text};
    selection-background-color: {accent};
    selection-color: {bg};
    border: 1px solid {border};
    border-radius: 8px;
}}

QCheckBox {{
    color: {text};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {border};
    background-color: {surface};
}}

QCheckBox::indicator:checked {{
    background-color: {accent};
    border: 1px solid {accent};
}}

/* Cards / painéis */
QGroupBox {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 12px;
    margin-top: 14px;
    padding: 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {accent};
    font-weight: 700;
}}

/* Tabelas / listas */
QTableView, QListView, QTreeView {{
    background-color: {surface};
    alternate-background-color: {bg};
    color: {text};
    gridline-color: {border};
    border: 1px solid {border};
    border-radius: 10px;
}}

QHeaderView::section {{
    background-color: {menu};
    color: {text};
    border: 1px solid {border};
    padding: 6px 10px;
    font-weight: 700;
}}

/* Abas */
QTabWidget::pane {{
    border: 1px solid {border};
    background-color: {surface};
    border-radius: 12px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {menu};
    color: {text};
    padding: 8px 16px;
    margin-right: 4px;
    border: 1px solid {border};
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {surface}, stop:1 {bg});
    color: {accent};
    font-weight: 800;
}}

QTabBar::tab:hover {{
    color: {accent};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {bg};
    width: 10px;
    margin: 2px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {accent};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {bg};
    height: 10px;
    margin: 2px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 5px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {accent};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* Menus / toolbar / status */
QMenuBar {{
    background-color: {menu};
    color: {text};
    border-bottom: 1px solid {border};
}}

QMenuBar::item:selected {{
    background-color: {accent};
    color: {bg};
    border-radius: 6px;
}}

QMenu {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 18px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: {accent};
    color: {bg};
}}

QToolBar {{
    background-color: {menu};
    border-bottom: 1px solid {border};
    spacing: 6px;
    padding: 4px;
}}

QStatusBar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {menu}, stop:1 {bg});
    color: {text};
    border-top: 1px solid {border};
    font-size: 9pt;
}}

QToolTip {{
    background-color: {surface};
    color: {text};
    border: 1px solid {accent};
    border-radius: 6px;
    padding: 6px 8px;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {border};
}}

/* Progress */
QProgressBar {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 8px;
    text-align: center;
    color: {text};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {accent}, stop:1 {button});
    border-radius: 7px;
}}

/* Spinners */
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {menu};
    border: none;
    width: 16px;
}}

/* Frameless cards hover glow (best-effort) */
QFrame#card:hover {{
    border: 1px solid {accent};
}}
"""
