from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from interface.icons import ICONS
from monitor.system_monitor import SystemMonitor


def _make_card():
    card = QFrame()
    card.setObjectName("card")
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(18, 18, 18, 18)
    card_layout.setSpacing(12)
    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(20)
    shadow.setOffset(0, 4)
    shadow.setColor(QColor(0, 0, 0, 90))
    card.setGraphicsEffect(shadow)
    return card, card_layout


def _handle_button(name, text, managers):
    settings = managers.get("settings")
    personalization = managers.get("personalization")
    sync = managers.get("sync")
    theme_manager = managers.get("theme_manager")
    # best-effort dispatch
    try:
        if text == "Aplicar tema padrão":
            if theme_manager:
                theme_manager.apply_theme(None, "escuro")
        elif text == "Atualizar":
            pass
        elif text == "Enviar":
            pass
        elif text == "Testar conexão":
            pass
        elif text == "Adicionar provedor":
            pass
        elif text == "Abrir central":
            pass
        elif text == "Aplicar wallpaper":
            pass
        elif text == "Explorar":
            pass
        elif text == "Criar relógio":
            pass
        elif text == "Adicionar widget":
            pass
        elif text == "Abrir programa":
            pass
        elif text == "Executar rotina":
            pass
        elif text == "Organizar pasta":
            pass
        elif text == "Aplicar tema":
            if theme_manager:
                theme_manager.apply_theme(None, "claro")
        elif text == "Sincronizar agora":
            if sync is not None and hasattr(sync, "sync_now"):
                sync.sync_now()
        elif text == "Entrar":
            pass
    except Exception:
        pass


def create_page(
    name,
    settings=None,
    personalization=None,
    sync=None,
    theme_manager=None,
    monitor=None,
):
    managers = {
        "settings": settings,
        "personalization": personalization,
        "sync": sync,
        "theme_manager": theme_manager,
    }
    w = QWidget()
    w.setObjectName("page")
    outer = QVBoxLayout(w)
    outer.setContentsMargins(28, 24, 28, 24)
    outer.setSpacing(18)

    # Header
    header = QVBoxLayout()
    header.setSpacing(4)
    icon = ICONS.get(name, "•")
    title = QLabel(f"{icon}  {name}")
    title.setObjectName("title")
    title.setStyleSheet("font-size:24pt;font-weight:800;")
    subtitle = QLabel(_subtitle(name))
    subtitle.setObjectName("muted")
    subtitle.setStyleSheet("font-size:11pt;")
    header.addWidget(title)
    header.addWidget(subtitle)
    outer.addLayout(header)

    # Card principal
    card, cl = _make_card()
    cl.addWidget(QLabel(_description(name)))

    # Botões por página
    btns = _buttons_for(name)
    if btns:
        row = QHBoxLayout()
        row.setSpacing(10)
        for txt, primary in btns:
            b = QPushButton(txt)
            if primary:
                b.setObjectName("btnPrimary")
            b.clicked.connect(
                lambda checked=False, t=txt: _handle_button(name, t, managers)
            )
            row.addWidget(b)
        row.addStretch()
        cl.addLayout(row)

    # Grid de métricas para início/monitor
    if name in ("Início", "Monitoramento do PC"):
        grid = QGridLayout()
        grid.setSpacing(12)
        monitor_inst = monitor or SystemMonitor()
        labels = []
        metrics = _metrics(name)
        for i, (k, v) in enumerate(metrics):
            mini, ml = _make_card()
            ml.addWidget(QLabel(k))
            val = QLabel(v)
            val.setStyleSheet("font-size:18pt;font-weight:700;")
            ml.addWidget(val)
            grid.addWidget(mini, i // 2, i % 2)
            labels.append((k, val))
        cl.addLayout(grid)

        def update_metrics():
            try:
                summary = monitor_inst.get_performance_summary()
            except Exception:
                return
            cpu = summary.get("cpu_percent", 0)
            ram = summary.get("ram", {})
            disk = summary.get("disk", {})
            net = summary.get("network", {})
            for k, val in labels:
                try:
                    if k == "CPU":
                        val.setText(f"{cpu:.1f}%")
                    elif k == "RAM":
                        val.setText(
                            f"{ram.get('used', 0) / (1024**3):.1f} GB"
                            if ram.get("used")
                            else f"{ram.get('percent', 0):.1f}%"
                        )
                    elif k == "Disco":
                        val.setText(f"{disk.get('percent', 0):.1f}%")
                    elif k == "Rede":
                        val.setText(f"{net.get('bytes_recv', 0)} B")
                    elif k == "Uptime":
                        pass
                except Exception:
                    pass

        timer = QTimer(w)
        timer.setInterval(2000)
        timer.timeout.connect(update_metrics)
        timer.start()
        update_metrics()
        w._metrics_timer = timer

    outer.addWidget(card)
    outer.addStretch()
    return w


def _subtitle(name):
    subs = {
        "Início": "Bem-vindo ao GP Desktop Ultimate AI",
        "Assistente IA": "Converse com modelos de IA locais e remotos",
        "Provedores de IA": "Configure e teste conexões com provedores",
        "Personalização": "Central de personalização do ambiente",
        "Papéis de parede": "Biblioteca e aplicação de wallpapers",
        "Relógio": "Relógio flutuante e alarmes",
        "Widgets": "Widgets de desktop",
        "Monitoramento do PC": "CPU, RAM, disco e rede em tempo real",
        "Aplicativos": "Gerencie aplicativos instalados",
        "Automação": "Rotinas e automações",
        "Arquivos": "Organização e busca de arquivos",
        "Temas": "Temas e aparência",
        "Sincronização": "Sincronize com a nuvem",
        "Configurações": "Preferências do aplicativo",
        "Minha conta": "Perfil e autenticação",
    }
    return subs.get(name, "")


def _description(name):
    descs = {
        "Início": "Painel principal com atalhos rápidos e status do sistema.",
        "Assistente IA": "Envie prompts e receba respostas inteligentes.",
    }
    return descs.get(name, f"Módulo de {name.lower()}.")


def _buttons_for(name):
    mapping = {
        "Início": [("Aplicar tema padrão", True), ("Atualizar", False)],
        "Assistente IA": [("Enviar", True)],
        "Provedores de IA": [("Testar conexão", True), ("Adicionar provedor", False)],
        "Personalização": [("Abrir central", True)],
        "Papéis de parede": [("Aplicar wallpaper", True), ("Explorar", False)],
        "Relógio": [("Criar relógio", True)],
        "Widgets": [("Adicionar widget", True)],
        "Aplicativos": [("Abrir programa", True)],
        "Automação": [("Executar rotina", True)],
        "Arquivos": [("Organizar pasta", True)],
        "Temas": [("Aplicar tema", True)],
        "Sincronização": [("Sincronizar agora", True)],
        "Minha conta": [("Entrar", True)],
    }
    return mapping.get(name, [])


def _metrics(name):
    if name == "Início":
        return [("CPU", "12%"), ("RAM", "4.2 GB"), ("Disco", "68%"), ("Uptime", "3h")]
    if name == "Monitoramento do PC":
        return [
            ("CPU", "12%"),
            ("RAM", "4.2 GB"),
            ("Disco", "68%"),
            ("Rede", "120 Mbps"),
        ]
    return []
