import pytest

try:
    from PySide6.QtWidgets import QApplication

    HAS_QT = True
except Exception:
    HAS_QT = False


@pytest.mark.skipif(not HAS_QT, reason="PySide6 indisponível")
def test_main_window_navigate():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from interface.main_window import MainWindow

    w = MainWindow()
    assert w is not None
    w.navigate_to("Temas")
    assert w.stack.currentWidget() is w.pages["Temas"]
    w.close()


def test_pages_factory():
    from interface.pages import create_page

    for name in ["Início", "Temas", "Minha conta"]:
        p = create_page(name)
        assert p is not None


def test_personalization_center():
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
    except Exception:
        pytest.skip("no qt")
    from interface.personalization_center import PersonalizationCenter

    c = PersonalizationCenter()
    assert c is not None
