"""Notificações (toast) no Windows."""

from __future__ import annotations

from typing import Any


def show_toast(
    title: str, message: str, duration: int = 5, threaded: bool = True
) -> bool:
    """Exibe uma notificação. Usa win10toast se disponível, senão fallback."""
    # Tenta win10toast
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=duration, threaded=threaded)
        return True
    except Exception:
        pass

    # Fallback: PowerShell toast (best-effort)
    try:
        import subprocess

        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
            "$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            "$textNodes = $template.GetElementsByTagName('text'); "
            f"$textNodes.Item(0).AppendChild($template.CreateTextNode('{title}')) | Out-Null; "
            f"$textNodes.Item(1).AppendChild($template.CreateTextNode('{message}')) | Out-Null; "
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('GP Desktop').Show($toast);"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            timeout=15,
        )
        return True
    except Exception:
        pass

    # Fallback final: MessageBox
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, str(message), str(title), 0x40)
        return True
    except Exception:
        return False


def show_message_box(title: str, message: str, style: int = 0) -> int:
    try:
        import ctypes

        return int(ctypes.windll.user32.MessageBoxW(0, str(message), str(title), style))
    except Exception:
        return 0


__all__ = ["show_toast", "show_message_box"]
