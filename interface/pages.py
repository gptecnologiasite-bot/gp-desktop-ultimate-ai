from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


def create_page(name):
    w = QWidget()
    layout = QVBoxLayout(w)
    title = QLabel(name)
    title.setStyleSheet("font-size:20px;font-weight:bold;")
    layout.addWidget(title)

    if name == "Início":
        layout.addWidget(QLabel("Bem-vindo ao GP Desktop Ultimate AI"))
        btn = QPushButton("Aplicar tema padrão")
        layout.addWidget(btn)
    elif name == "Assistente IA":
        layout.addWidget(QLabel("Chat com IA"))
        layout.addWidget(QPushButton("Enviar"))
    elif name == "Provedores de IA":
        layout.addWidget(QLabel("Configurar provedores"))
        layout.addWidget(QPushButton("Testar conexão"))
    elif name == "Personalização":
        layout.addWidget(QLabel("Central de personalização"))
    elif name == "Papéis de parede":
        layout.addWidget(QLabel("Biblioteca de wallpapers"))
        layout.addWidget(QPushButton("Aplicar wallpaper"))
    elif name == "Relógio":
        layout.addWidget(QLabel("Relógio flutuante"))
        layout.addWidget(QPushButton("Criar relógio"))
    elif name == "Widgets":
        layout.addWidget(QLabel("Widgets"))
        layout.addWidget(QPushButton("Adicionar widget"))
    elif name == "Monitoramento do PC":
        layout.addWidget(QLabel("CPU / RAM / Disco"))
    elif name == "Aplicativos":
        layout.addWidget(QLabel("Aplicativos"))
        layout.addWidget(QPushButton("Abrir programa"))
    elif name == "Automação":
        layout.addWidget(QLabel("Automação"))
        layout.addWidget(QPushButton("Executar rotina"))
    elif name == "Arquivos":
        layout.addWidget(QLabel("Arquivos"))
        layout.addWidget(QPushButton("Organizar pasta"))
    elif name == "Temas":
        layout.addWidget(QLabel("Temas"))
        layout.addWidget(QPushButton("Aplicar tema"))
    elif name == "Sincronização":
        layout.addWidget(QLabel("Sincronização"))
        layout.addWidget(QPushButton("Sincronizar agora"))
    elif name == "Configurações":
        layout.addWidget(QLabel("Configurações"))
    elif name == "Minha conta":
        layout.addWidget(QLabel("Minha conta"))
        layout.addWidget(QPushButton("Entrar"))
    layout.addStretch()
    return w
