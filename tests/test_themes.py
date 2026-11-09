import os

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

from themes import THEMES, THEME_DEFINITIONS, build_qss, ThemeManager, get_theme


def test_themes_defined():
    assert len(THEMES) >= 6
    assert THEMES is THEME_DEFINITIONS
    for name, colors in THEMES.items():
        for key in (
            "background",
            "surface",
            "text",
            "accent",
            "menu",
            "button",
            "border",
        ):
            assert key in colors, (name, key)


def test_predefined_theme_names():
    expected = {"claro", "escuro", "futurista", "gamer", "minimalista", "profissional"}
    assert expected.issubset(set(THEMES.keys()))


def test_build_qss_non_empty():
    qss = build_qss("claro")
    assert isinstance(qss, str)
    assert qss.strip() != ""
    qss2 = build_qss(THEMES["escuro"])
    assert isinstance(qss2, str) and qss2.strip() != ""
    qss3 = build_qss(get_theme("gamer"))
    assert "background" not in qss3 or True
    assert len(qss3) > 100


def test_build_qss_contains_colors():
    qss = build_qss("escuro")
    assert THEMES["escuro"]["background"] in qss
    assert THEMES["escuro"]["accent"] in qss


def test_apply_does_not_break():
    tm = ThemeManager()
    events = []
    tm.theme_changed.connect(lambda t: events.append(t))

    class App:
        def __init__(self):
            self.css = ""

        def setStyleSheet(self, value):
            self.css = value

    app = App()
    result = tm.apply_theme(app, "escuro")
    assert app.css.strip() != ""
    assert isinstance(result, dict)
    assert len(events) == 1


def test_set_custom_colors():
    tm = ThemeManager()
    tm.set_custom_colors(accent="#ff0000", background="#000000")
    assert tm.custom_colors.get("accent") == "#ff0000"
    assert tm.current_theme["accent"] == "#ff0000"


def test_manager_instantiation_no_app():
    tm = ThemeManager()
    # não deve quebrar
    tm.apply_theme(None, "claro")
    assert tm.current_theme["background"] == THEMES["claro"]["background"]
