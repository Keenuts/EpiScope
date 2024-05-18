from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow
from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
                               QMainWindow, QSlider, QStyle, QToolBar,
                               QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QWidget)
from PySide6.QtMultimedia import (QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget

import sys
from localization import I18N

AVI = "video/x-msvideo"  # AVI
MP4 = 'video/mp4'
WANTED_VIDEO_MIME_TYPES = [ MP4, AVI ]

class VideoWidget(QWidget):
    def __init__(self, steps=5, *args, **kwargs):
        super(VideoWidget, self).__init__(*args, **kwargs)

        video = QVideoWidget()
        audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(audio_output)
        self._player.errorOccurred.connect(self._player_error)
        self._player.playbackStateChanged.connect(self._update_toolbar)
        self._player.setVideoOutput(video)
        self._player.positionChanged.connect(self._player_position_changed)
        self._player.durationChanged.connect(self._player_duration_changed)

        toolbar = QToolBar()
        timeline = QFrame(self)

        vsplit = QSplitter(Qt.Vertical)
        vsplit.addWidget(video)
        vsplit.addWidget(toolbar)
        vsplit.addWidget(timeline)
        vsplit.setStretchFactor(0, 1)
        vsplit.setStretchFactor(1, 1)
        vsplit.setStretchFactor(2, 5)

        vbox = QVBoxLayout(self)
        vbox.addWidget(vsplit)
        self.setLayout(vbox)

        style = self.style()
        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart,
                                          style.standardIcon(QStyle.SP_MediaPlay))
        self._play_action = toolbar.addAction(icon, "toolbar_play")
        self._play_action.triggered.connect(self._player.play)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause,
                               style.standardIcon(QStyle.SP_MediaPause))
        self._pause_action = toolbar.addAction(icon, I18N("toolbar_pause"))
        self._pause_action.triggered.connect(self._player.pause)

        self._time_slider = QSlider()
        self._time_slider.setOrientation(Qt.Horizontal)
        self._time_slider.setMinimum(0)
        self._time_slider.setMaximum(0)
        self._time_slider.setValue(0)
        self._time_slider.setToolTip(I18N("toolbar_seek_tooltip"))
        self._time_slider.valueChanged.connect(self._player.setPosition)
        toolbar.addWidget(self._time_slider)

        self._update_toolbar(QMediaPlayer.StoppedState)

    @Slot("QMediaPlayer::PlaybackState")
    def _update_toolbar(self, state):
        is_playing = state == QMediaPlayer.PlayingState
        self._play_action.setEnabled(not is_playing)
        self._play_action.setVisible(not is_playing)
        self._pause_action.setEnabled(is_playing)
        self._pause_action.setVisible(is_playing)

    def _player_position_changed(self, position):
        self._time_slider.setValue(position)

    def _player_duration_changed(self, duration):
        self._time_slider.setMaximum(duration)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)

    def _ensure_stopped(self):
        pass
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    def setVideo(self, url):
        self._ensure_stopped()
        self._player.setSource(url)
        self._player.play()
        self._time_slider.setValue(0)

class Player(QMainWindow):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        self.initialize_menu_file()
        self.initialize_mime_types()
        self.initialize_file_dialog()

    def initialize_mime_types(self):
        supported_types = set([ QMediaFormat(f).mimeType().name()
            for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode) ])
        self._mime_types = list(filter(lambda x : x in supported_types,
                                  WANTED_VIDEO_MIME_TYPES))

    def initialize_file_dialog(self):
        self._default_location = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)

    def initialize_menu_file(self):
        file_menu = self.menuBar().addMenu(I18N("menu_files"))
        action_new  = QAction(I18N("menu_files_new"),
                             self,
                             shortcut=QKeySequence.New,
                             triggered=self.action_reset)
        action_load = QAction(I18N("menu_files_load"),
                              self,
                              shortcut=QKeySequence.Open,
                              triggered=self.action_load)
        action_save = QAction(I18N("menu_files_save"),
                              self,
                              shortcut=QKeySequence.Save,
                              triggered=self.action_save)
        action_export = QAction(I18N("menu_files_export"),
                                self,
                                shortcut=QKeySequence(Qt.CTRL | Qt.Key_E),
                                triggered=self.action_export)
        action_import_video = QAction(I18N("menu_files_import_video"),
                               self,
                               shortcut=QKeySequence(Qt.CTRL | Qt.Key_I),
                               triggered=self.action_import_video)
        action_import_timeline = QAction(I18N("menu_files_import_timeline"),
                              self,
                              triggered=self.action_import_timeline)
        action_exit = QAction(I18N("menu_files_exit"),
                              self,
                              shortcut=QKeySequence.Quit,
                              triggered=self.action_exit)

        file_menu.addAction(action_new)
        file_menu.addAction(action_load)
        file_menu.addAction(action_save)
        file_menu.addAction(action_export)
        file_menu.addAction(action_import_video)
        file_menu.addAction(action_import_timeline)
        file_menu.addAction(action_exit)

        self.player = VideoWidget()
        self.setCentralWidget(self.player)

    def action_reset(self):
        pass

    def action_load(self):
        pass

    def action_save(self):
        pass

    def action_export(self):
        pass

    def action_import_video(self):
        file_dialog = QFileDialog(self)
        file_dialog.setMimeTypeFilters(self._mime_types)
        file_dialog.selectMimeTypeFilter(self._mime_types[0])
        file_dialog.setDirectory(self._default_location)
        if file_dialog.exec() == QDialog.Accepted:
            self._default_location = file_dialog.directory().absolutePath()
            url = file_dialog.selectedUrls()[0]
            self.player.setVideo(url)

    def action_import_timeline(self):
        pass

    def action_exit(self):
        del self.player
        self.setCentralWidget(None)
        self.close()
