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
        self.resize(1320, 840)
        self.setMinimumSize(960, 640)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(MENU_ITEMS)
        self.sidebar.itemClicked.connect(self.navigate_to)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        self.pages = {}
        for name in MENU_ITEMS:
            if name == "Personalização":
                page = PersonalizationCenter(
                    settings=self.settings,
                    personalization=self.personalization,
                    theme_manager=self.theme_manager,
                )
            else:
                page = create_page(
                    name,
                    settings=self.settings,
                    personalization=self.personalization,
                    sync=self.sync,
                    theme_manager=self.theme_manager,
                )
            self.pages[name] = page
            self.stack.addWidget(page)
        layout.addWidget(self.stack, 1)

        status = QStatusBar()
        status.setObjectName("statusBar")
        self.setStatusBar(status)
        status.showMessage("Pronto • GP Desktop Ultimate AI")

        self.navigate_to("Início")
        try:
            theme_name = "escuro"
            if self.settings is not None:
                theme_name = self.settings.get("theme", theme_name)
            self.theme_manager.apply_theme(self, theme_name)
        except Exception:
            pass

    def navigate_to(self, name):
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])
            try:
                self.statusBar().showMessage(f"  {name}")
            except Exception:
                pass
            # sincroniza selecao da sidebar
            try:
                for i in range(self.sidebar.list.count()):
                    item = self.sidebar.list.item(i)
                    if item.data(Qt.UserRole) == name:
                        self.sidebar.list.setCurrentItem(item)
                        break
            except Exception:
                pass
