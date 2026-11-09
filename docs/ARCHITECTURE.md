# Arquitetura — GP Desktop Ultimate AI

## Visão geral

Aplicativo desktop Windows em Python/PySide6. Entrada em `main.py`, que
inicializa Qt, managers e a janela principal. Integração com Supabase para
auth/dados/sync.

## Estrutura de módulos

```
gp-desktop-ultimate-ai/
├── main.py                     # entrypoint
├── pyproject.toml / requirements.txt
├── .env.example
├── assistant/                  # chat, comandos, voz
│   ├── chat.py
│   ├── commands.py
│   ├── manager.py
│   └── voice.py
├── automation/                 # arquivos, programas, tarefas
├── clock/                      # relógio flutuante + modelos
├── interface/                  # janela principal (Qt) — main_window
├── migrations/                 # SQL inicial (espelho)
├── monitor/                    # monitoramento do sistema
├── personalization/            # perfis e personalização
├── providers/                  # provedores de IA
│   ├── base.py, registry.py
│   ├── openai_compatible.py, anthropic.py, gemini.py
│   ├── cohere.py, huggingface.py, ollama.py, lmstudio.py
├── security/                   # DPAPI + credential manager
├── settings/                   # settings manager
├── supabase/                   # integração Supabase
│   ├── client.py (singleton)
│   ├── auth.py, database.py, storage.py, realtime.py, edge_functions.py
│   └── migrations/             # SQL versionado
├── synchronization/            # sync manager
├── themes/                     # definições, stylesheet, manager
├── wallpaper/                  # biblioteca, player, wallpaper Windows
├── widgets/                    # base, manager, system widget
├── windows/                    # display, manager, notifications, registry, shortcuts, startup
├── installer/                  # build.py, build_installer.py
├── tests/                      # pytest
└── docs/                       # README, ARCHITECTURE
```

## Fluxo de inicialização

1. `main.load_env()` carrega `.env` (python-dotenv) se existir.
2. `QApplication` criada com atributos de High DPI.
3. Managers instanciados: `SettingsManager`, `PersonalizationManager`,
   `SyncManager`, `ThemeManager`.
4. `MainWindow` criada com os managers e exibida.
5. `app.exec()` inicia o loop de eventos.

## Integração Supabase

- `supabase/client.py` mantém singleton thread-safe do `Client`.
- Lê `SUPABASE_URL` e `SUPABASE_ANON_KEY` do ambiente.
- `reset_client()` permite troca de credenciais em testes.
- O pacote local `supabase/` faz shadow do pacote instalado; o client
  manipula `sys.path`/`sys.modules` para importar o `supabase-py` real.

## Build

- `installer/build.py` gera `.spec` programaticamente e invoca PyInstaller
  (onefile/onedir), incluindo módulos locais como hidden imports e arquivos
  de dados (migrations, assets).
- `installer/build_installer.py` gera `.iss` para Inno Setup (apenas texto).

## Testes

- pytest em `tests/`, com `SUPABASE_URL`/`SUPABASE_ANON_KEY` padrão via
  `os.environ.setdefault`.
- Sem dependência de rede para a maior parte da suíte.
