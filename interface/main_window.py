from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QStatusBar,
    QLabel,
)
from PySide6.QtCore import Qt

from interface.sidebar import Sidebar
from interface.pages import create_page
from interface.personalization_center import PersonalizationCenter
from themes.manager import ThemeManager


MENU_ITEMS = [
    "Início",
    "Assistente IA",
    "Provedores de IA",
    "Personalização",
    "Papéis de parede",
    "Relógio",
    "Widgets",
    "Monitoramento do PC",
    "Aplicativos",
    "Automação",
    "Arquivos",
    "Temas",
    "Sincronização",
    "Configurações",
    "Minha conta",
]


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings=None,
        personalization=None,
        sync=None,
        theme_manager=None,
        parent=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.personalization = personalization
        self.sync = sync
        self.theme_manager = theme_manager or ThemeManager()

        self.setWindowTitle("GP Desktop Ultimate AI")
        self.resize(1280, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(MENU_ITEMS)
        self.sidebar.itemClicked.connect(self.navigate_to)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.pages = {}
        for name in MENU_ITEMS:
            if name == "Personalização":
                page = PersonalizationCenter()
            else:
                page = create_page(name)
            self.pages[name] = page
            self.stack.addWidget(page)
        layout.addWidget(self.stack, 1)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")

        self.navigate_to("Início")
        try:
            self.theme_manager.apply_theme(self, "escuro")
        except Exception:
            pass

    def navigate_to(self, name):
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])
            self.statusBar().showMessage(name)
