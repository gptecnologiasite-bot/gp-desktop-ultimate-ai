"""Player de wallpapers (vÃ­deo/GIF) com controles de volume/pause/play/loop."""

from __future__ import annotations

import os
import sys
from typing import Any, Optional

# Garante uma QApplication disponÃ­vel (offscreen em ambientes sem display).
def _ensure_qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is not None:
        return app
    # Tenta modo normal; se falhar, usa offscreen.
    for platform in (None, "offscreen"):
        try:
            if platform:
                os.environ.setdefault("QT_QPA_PLATFORM", platform)
            app = QApplication([])
            return app
        except Exception:
            if platform is None:
                os.environ["QT_QPA_PLATFORM"] = "offscreen"
            continue
    # Ãºltima tentativa
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication([])


# Importa Qt apÃ³s garantir app factory disponÃ­vel (lazy no __init__).
from PySide6.QtCore import QObject, QUrl, Qt
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class WallpaperPlayer(QObject):
    """Reproduz vÃ­deos (QMediaPlayer) e GIFs (QMovie) como wallpaper."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._app = _ensure_qapp()
        self._volume = 50
        self._loop = True
        self._current_path: Optional[str] = None
        self._mode: Optional[str] = None  # 'video' | 'gif' | None

        # VÃ­deo
        try:
            from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
            from PySide6.QtMultimediaWidgets import QVideoWidget

            self._media_player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._media_player.setAudioOutput(self._audio_output)
            self._video_widget = QVideoWidget()
            self._media_player.setVideoOutput(self._video_widget)
            self._has_media = True
        except Exception:
            self._media_player = None
            self._audio_output = None
            self._video_widget = None
            self._has_media = False

        # Container para GIF
        self._container = QWidget(parent)
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._gif_label = QLabel(self._container)
        self._gif_label.setScaledContents(True)
        self._container_layout.addWidget(self._gif_label)
        self._movie: Optional[QMovie] = None

        if self._has_media and self._media_player is not None:
            try:
                self._audio_output.setVolume(self._volume / 100.0)
            except Exception:
                pass
            try:
                self._media_player.mediaStatusChanged.connect(self._on_media_status)
            except Exception:
                pass

    # ---------- propriedades ----------

    def video_widget(self) -> Optional[QWidget]:
        return self._video_widget

    def container(self) -> QWidget:
        return self._container

    def current_path(self) -> Optional[str]:
        return self._current_path

    def mode(self) -> Optional[str]:
        return self._mode

    # ---------- controle ----------

    def set_source(self, path: str) -> bool:
        self.stop()
        self._current_path = path
        ext = os.path.splitext(path)[1].lower()
        if ext == ".gif":
            return self._load_gif(path)
        if ext in (".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"):
            return self._load_video(path)
        # imagem: sem reproduÃ§Ã£o
        self._mode = "image"
        return True

    def _load_gif(self, path: str) -> bool:
        try:
            movie = QMovie(path)
            try:
                movie.setLoopCount(-1 if self._loop else 1)
            except Exception:
                pass
            self._gif_label.setMovie(movie)
            movie.start()
            self._movie = movie
            self._mode = "gif"
            return True
        except Exception:
            self._mode = None
            return False

    def _load_video(self, path: str) -> bool:
        if not self._has_media or self._media_player is None:
            return False
        try:
            self._media_player.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
            try:
                self._media_player.setLoops(
                    self._media_player.Loops.Infinite if self._loop else 1
                )
            except Exception:
                pass
            self._mode = "video"
            return True
        except Exception:
            self._mode = None
            return False

    def play(self) -> None:
        if self._mode == "gif" and self._movie is not None:
            try:
                self._movie.start()
            except Exception:
                pass
            return
        if self._mode == "video" and self._media_player is not None:
            try:
                self._media_player.play()
            except Exception:
                pass

    def pause(self) -> None:
        if self._mode == "gif" and self._movie is not None:
            try:
                self._movie.setPaused(True)
            except Exception:
                pass
            return
        if self._mode == "video" and self._media_player is not None:
            try:
                self._media_player.pause()
            except Exception:
                pass

    def stop(self) -> None:
        if self._movie is not None:
            try:
                self._movie.stop()
            except Exception:
                pass
            self._movie = None
            try:
                self._gif_label.clear()
            except Exception:
                pass
        if self._media_player is not None:
            try:
                self._media_player.stop()
            except Exception:
                pass

    def set_volume(self, volume: int) -> None:
        self._volume = max(0, min(100, int(volume)))
        if self._audio_output is not None:
            try:
                self._audio_output.setVolume(self._volume / 100.0)
            except Exception:
                pass

    def volume(self) -> int:
        return self._volume

    def set_loop(self, loop: bool) -> None:
        self._loop = bool(loop)
        if self._movie is not None:
            try:
                self._movie.setLoopCount(-1 if self._loop else 1)
            except Exception:
                pass
        if self._media_player is not None:
            try:
                self._media_player.setLoops(
                    self._media_player.Loops.Infinite if self._loop else 1
                )
            except Exception:
                pass

    def loop(self) -> bool:
        return self._loop

    def is_playing(self) -> bool:
        if self._mode == "gif" and self._movie is not None:
            try:
                return self._movie.state() == QMovie.Running
            except Exception:
                return False
        if self._mode == "video" and self._media_player is not None:
            try:
                from PySide6.QtMultimedia import QMediaPlayer

                return self._media_player.playbackState() == QMediaPlayer.PlayingState
            except Exception:
                return False
        return False

    def _on_media_status(self, status) -> None:
        # loop manual caso setLoops nÃ£o suportado
        if not self._loop:
            return
        try:
            from PySide6.QtMultimedia import QMediaPlayer

            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                self._media_player.setPosition(0)
                self._media_player.play()
        except Exception:
            pass
