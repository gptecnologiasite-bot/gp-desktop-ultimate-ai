from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Qt, Signal


class Sidebar(QWidget):
    itemClicked = Signal(str)

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self._visible = {i: True for i in self.items}
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.title = QLabel("GP Desktop")
        self.title.setStyleSheet("font-weight:bold;font-size:16px;")
        self.layout.addWidget(self.title)
        self.list = QListWidget()
        self.list.itemClicked.connect(self._on_click)
        self.layout.addWidget(self.list)
        self.refresh()

    def refresh(self):
        self.list.clear()
        for name in self.items:
            if not self._visible.get(name, True):
                continue
            item = QListWidgetItem(name)
            self.list.addItem(item)

    def set_visible(self, name, visible):
        if name in self._visible:
            self._visible[name] = visible
            self.refresh()

    def set_width(self, width):
        self.setFixedWidth(width)

    def _on_click(self, item):
        self.itemClicked.emit(item.text())
