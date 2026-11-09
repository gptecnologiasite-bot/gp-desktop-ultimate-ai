from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QFrame,
    QComboBox,
    QSlider,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from themes import THEMES
from personalization.profiles import create_default_profiles


class PersonalizationCenter(QWidget):
    def __init__(
        self, settings=None, personalization=None, theme_manager=None, parent=None
    ):
        super().__init__(parent)
        self.settings = settings
        self.personalization = personalization
        self.theme_manager = theme_manager
        self.setObjectName("personalizationCenter")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(16)

        title = QLabel("Central de Personalização")
        title.setObjectName("title")
        title.setStyleSheet("font-size:24pt;font-weight:800;")
        subtitle = QLabel("Configure aparência, layout, área de trabalho e perfis.")
        subtitle.setObjectName("muted")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._appearance_tab(), "Aparência")
        tabs.addTab(self._layout_tab(), "Layout")
        tabs.addTab(self._desktop_tab(), "Área de trabalho")
        tabs.addTab(self._profiles_tab(), "Perfis")
        outer.addWidget(tabs, 1)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        specs = [
            ("Aplicar alterações", "btnPrimary", self.apply_changes),
            ("Visualizar", None, self.preview_changes),
            ("Salvar personalização", "btnSuccess", self.save_customization),
            ("Restaurar padrão", None, self.restore_default),
            ("Cancelar", "btnDanger", self.cancel_changes),
            ("Exportar tema", None, self.export_theme),
            ("Importar tema", None, self.import_theme),
        ]
        for txt, obj, handler in specs:
            b = QPushButton(txt)
            if obj:
                b.setObjectName(obj)
            b.clicked.connect(handler)
            btns.addWidget(b)
        btns.addStretch()
        outer.addLayout(btns)

    def _card(self, title_text, items):
        card = QFrame()
        card.setObjectName("card")
        l = QVBoxLayout(card)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(10)
        t = QLabel(title_text)
        t.setStyleSheet("font-size:13pt;font-weight:700;")
        l.addWidget(t)
        for it in items:
            l.addWidget(it)
        l.addStretch()
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)
        return card

    def _appearance_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(12)
        # tema combo
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        l.addWidget(self._card("Tema", [QLabel("Selecione o tema"), self.theme_combo]))
        # cor destaque slider
        self.accent_slider = QSlider(Qt.Horizontal)
        self.accent_slider.setRange(0, 100)
        self.accent_slider.setValue(50)
        self.accent_label = QLabel("Destaque: 50")
        self.accent_slider.valueChanged.connect(
            lambda v: self.accent_label.setText(f"Destaque: {v}")
        )
        l.addWidget(self._card("Cores", [self.accent_label, self.accent_slider]))
        # efeitos
        self.anim_cb = QCheckBox("Ativar animações")
        self.shadow_cb = QCheckBox("Sombras suaves")
        self.anim_cb.setChecked(True)
        self.shadow_cb.setChecked(True)
        l.addWidget(self._card("Efeitos", [self.anim_cb, self.shadow_cb]))
        l.addStretch()
        return w

    def _layout_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(12)
        self.sidebar_pos = QComboBox()
        self.sidebar_pos.addItems(["Esquerda", "Direita"])
        self.sidebar_width = QSlider(Qt.Horizontal)
        self.sidebar_width.setRange(180, 400)
        self.sidebar_width.setValue(250)
        self.sidebar_width_label = QLabel("Largura: 250")
        self.sidebar_width.valueChanged.connect(
            lambda v: self.sidebar_width_label.setText(f"Largura: {v}")
        )
        l.addWidget(
            self._card(
                "Menu lateral",
                [
                    QLabel("Posição"),
                    self.sidebar_pos,
                    self.sidebar_width_label,
                    self.sidebar_width,
                ],
            )
        )
        self.status_cb = QCheckBox("Mostrar status bar")
        self.status_cb.setChecked(True)
        l.addWidget(self._card("Painéis", [self.status_cb]))
        l.addStretch()
        return w

    def _desktop_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(12)
        l.addWidget(
            self._card(
                "Papel de parede",
                [QLabel("Biblioteca"), QPushButton("Escolher imagem")],
            )
        )
        self.clock_cb = QCheckBox("Exibir relógio")
        self.clock_cb.setChecked(True)
        l.addWidget(self._card("Relógio e widgets", [self.clock_cb]))
        l.addStretch()
        return w

    def _profiles_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(12)
        self.profile_combo = QComboBox()
        try:
            profiles = []
            if self.personalization is not None:
                profiles = self.personalization.list_profiles()
            if not profiles:
                profiles = [p.name for p in create_default_profiles()]
                if self.personalization is not None:
                    for p in create_default_profiles():
                        self.personalization.save_profile(p)
                    profiles = self.personalization.list_profiles()
            self.profile_combo.addItems(profiles)
        except Exception:
            self.profile_combo.addItems([p.name for p in create_default_profiles()])
        l.addWidget(
            self._card("Perfis", [QLabel("Selecione o perfil"), self.profile_combo])
        )
        l.addStretch()
        return w

    # handlers
    def apply_changes(self):
        try:
            if self.theme_manager is not None:
                theme_name = self.theme_combo.currentText()
                self.theme_manager.apply_theme(None, theme_name)
            if self.personalization is not None and self.profile_combo.count():
                self.personalization.apply(self.profile_combo.currentText())
            if self.settings is not None:
                self.settings.set("theme", self.theme_combo.currentText())
        except Exception:
            pass

    def preview_changes(self):
        try:
            if self.personalization is not None and self.profile_combo.count():
                self.personalization.preview(self.profile_combo.currentText())
        except Exception:
            pass

    def save_customization(self):
        try:
            if self.personalization is not None and self.profile_combo.count():
                name = self.profile_combo.currentText()
                # save current profile state (best-effort)
                if hasattr(self.personalization, "save_profile"):
                    pass
        except Exception:
            pass

    def restore_default(self):
        try:
            if self.personalization is not None:
                self.personalization.restore_default()
            if self.theme_manager is not None:
                self.theme_manager.apply_theme(None, "claro")
                self.theme_combo.setCurrentText("claro")
        except Exception:
            pass

    def cancel_changes(self):
        pass

    def export_theme(self):
        try:
            if self.personalization is None:
                return
            name = (
                self.profile_combo.currentText() if self.profile_combo.count() else None
            )
            if not name:
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Exportar tema", f"{name}.json", "JSON (*.json)"
            )
            if path:
                self.personalization.export_profile(name, path=path)
                QMessageBox.information(self, "Exportar", "Exportado com sucesso.")
        except Exception as e:
            QMessageBox.warning(self, "Exportar", str(e))

    def import_theme(self):
        try:
            if self.personalization is None:
                return
            path, _ = QFileDialog.getOpenFileName(
                self, "Importar tema", "", "JSON (*.json)"
            )
            if path:
                imported = self.personalization.import_profile(path)
                if hasattr(imported, "name"):
                    self.profile_combo.addItem(imported.name)
                    self.profile_combo.setCurrentText(imported.name)
                QMessageBox.information(self, "Importar", "Importado com sucesso.")
        except Exception as e:
            QMessageBox.warning(self, "Importar", str(e))
