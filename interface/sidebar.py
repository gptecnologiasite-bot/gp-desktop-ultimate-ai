from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


from interface.icons import ICONS


class Sidebar(QWidget):
    itemClicked = Signal(str)

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self._visible = {i: True for i in self.items}
        self.setObjectName("sidebar")
        self.setMinimumWidth(200)
        self.setMaximumWidth(360)
        self.setFixedWidth(250)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 16, 14, 16)
        self.layout.setSpacing(10)

        # Header com logo
        header = QFrame()
        header.setObjectName("sidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 6, 6, 6)
        logo = QLabel("GP")
        logo.setObjectName("logoBadge")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(40, 40)
        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("GP Desktop")
        title.setObjectName("sidebarTitle")
        subtitle = QLabel("Ultimate AI")
        subtitle.setObjectName("sidebarSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_layout.addWidget(logo)
        header_layout.addLayout(title_col)
        header_layout.addStretch()
        self.layout.addWidget(header)

        # Lista de itens
        self.list = QListWidget()
        self.list.setObjectName("menu")
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.itemClicked.connect(self._on_click)
        self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.list, 1)

        # Footer
        footer = QLabel("v1.0 • Neon Theme")
        footer.setObjectName("sidebarFooter")
        footer.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(footer)

        self.refresh()

        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(2, 0)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    def refresh(self):
        self.list.clear()
        for name in self.items:
            if not self._visible.get(name, True):
                continue
            icon = ICONS.get(name, "•")
            item = QListWidgetItem(f"  {icon}   {name}")
            item.setData(Qt.UserRole, name)
            self.list.addItem(item)

    def set_visible(self, name, visible):
        if name in self._visible:
            self._visible[name] = visible
            self.refresh()

    def set_width(self, width):
        try:
            w = int(width)
        except (TypeError, ValueError):
            return
        w = max(180, min(400, w))
        self.setFixedWidth(w)

    def _on_click(self, item):
        name = item.data(Qt.UserRole)
        if not name:
            name = item.text().strip()
        # remove icon prefix if needed
        if name not in self.items:
            for it in self.items:
                if it in item.text():
                    name = it
                    break
        self.itemClicked.emit(name)
