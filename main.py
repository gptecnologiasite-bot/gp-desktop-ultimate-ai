"""GP Desktop Ultimate AI - entrypoint."""

import os
import sys

# garantir import do pacote local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from interface.main_window import MainWindow
from themes.manager import ThemeManager
from settings.settings_manager import SettingsManager
from personalization.manager import PersonalizationManager
from synchronization.sync_manager import SyncManager
from supabase.client import get_supabase_client
from supabase.auth import AuthManager


def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv

            load_dotenv(env_path)
        except Exception:
            pass


def main():
    load_env()
    app = QApplication(sys.argv)
    app.setApplicationName("GP Desktop Ultimate AI")
    app.setOrganizationName("GP")

    # High DPI
    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    except Exception:
        pass

    settings = SettingsManager()
    personalization = PersonalizationManager()
    sync = SyncManager()
    theme_manager = ThemeManager()

    window = MainWindow(
        settings=settings,
        personalization=personalization,
        sync=sync,
        theme_manager=theme_manager,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
