from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
)


class PersonalizationCenter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel("Central de Personalização")
        title.setStyleSheet("font-size:20px;font-weight:bold;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._appearance_tab(), "Aparência")
        tabs.addTab(self._layout_tab(), "Layout")
        tabs.addTab(self._desktop_tab(), "Área de trabalho")
        tabs.addTab(self._profiles_tab(), "Perfis")
        layout.addWidget(tabs)

        btns = QHBoxLayout()
        for txt in [
            "Aplicar alterações",
            "Visualizar",
            "Salvar personalização",
            "Restaurar padrão",
            "Cancelar",
            "Exportar tema",
            "Importar tema",
        ]:
            btns.addWidget(QPushButton(txt))
        layout.addLayout(btns)

    def _appearance_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(
            QLabel("Tema claro/escuro/futurista/gamer/minimalista/profissional")
        )
        l.addWidget(
            QLabel(
                "Cores personalizadas, destaque, menus, botões, transparência, bordas"
            )
        )
        l.addStretch()
        return w

    def _layout_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(
            QLabel("Menu lateral, posição, módulos, painéis, widgets, tela inicial")
        )
        l.addStretch()
        return w

    def _desktop_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(
            QLabel("Papel de parede, relógio flutuante, widgets, atalhos, temas")
        )
        l.addStretch()
        return w

    def _profiles_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(
            QLabel(
                "Perfis: Gamer, Futurista, Minimalista, Escritório, Produtividade, Personalizado"
            )
        )
        l.addStretch()
        return w
