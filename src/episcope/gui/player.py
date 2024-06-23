from PySide6.QtCore import QStandardPaths, Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QDialog,
                               QFileDialog,
                               QLabel,
                               QMainWindow,
                               QSplitter,
                               QStyle,
                               QToolBar,
                               QHBoxLayout,
                               QVBoxLayout,
                               QGroupBox,
                               QWidget,
                               QSizePolicy)
from PySide6.QtMultimedia import QAudioOutput, QMediaFormat, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from typing import Self, Optional

import sys
import json
from episcope.localization import I18N
from episcope.core import Timeline, Symptom, SymptomCategory, SymptomDB, Attribute
from episcope.gui import TimelineWidget, AttributeEditor, SymptomPickerList

AVI = "video/x-msvideo"  # AVI
MP4 = 'video/mp4'
MPEG = 'video/mpeg'
MKV = 'video/x-matroska'
WEBM = 'video/webm'
QUICKTIME = 'video/quicktime'

WANTED_VIDEO_MIME_TYPES = [ MP4, AVI, MPEG, MKV, WEBM, QUICKTIME ]
JSON_MIME_TYPES = [ 'application/json' ]

class ToolbarWidget(QWidget):
    play = Signal()
    pause = Signal()

    def __init__(self : Self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        layout = QHBoxLayout()
        self.setLayout(layout)

        toolbar = QToolBar()
        self._time = QLabel()

        layout.addWidget(toolbar)
        layout.addStretch()
        layout.addWidget(self._time)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart, self.style().standardIcon(QStyle.SP_MediaPlay))
        self._play = toolbar.addAction(icon, I18N("toolbar_play"))
        icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause, self.style().standardIcon(QStyle.SP_MediaPause))
        self._pause = toolbar.addAction(icon, I18N("toolbar_pause"))

        self._play.triggered.connect(lambda: self.play.emit())
        self._pause.triggered.connect(lambda: self.pause.emit())

        self.setPlaying(False)
        self.setTime(0)

    def setPlaying(self : Self, playing : bool) -> None:
        self._play.setEnabled(not playing)
        self._play.setVisible(not playing)
        self._pause.setEnabled(playing)
        self._pause.setVisible(playing)

    def setTime(self : Self, time : int) -> None:
        seconds = time // 1000
        minutes = (seconds // 60) % 60
        hours = seconds // 3600
        seconds = seconds % 60
        self._time.setText("{:02}:{:02}:{:02}".format(hours, minutes, seconds))

class ClickableVideoWidget(QVideoWidget):
    clicked = Signal()

    def __init__(self : Self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.clicked.emit()

class MainWidget(QWidget):
    def __init__(self : Self, symptoms : SymptomDB, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._symptoms = symptoms

        self._timelineWidget = TimelineWidget()
        self._timelineWidget.on_seek.connect(self._player_seek)
        self._timelineWidget.on_symptom_edit.connect(self._onSymptomEdit)

        video = ClickableVideoWidget()
        video.clicked.connect(self._togglePlayPause)
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._player.errorOccurred.connect(self._player_error)
        self._player.playbackStateChanged.connect(self._update_toolbar)
        self._player.setVideoOutput(video)
        self._player.positionChanged.connect(self._player_position_changed)
        self._player.durationChanged.connect(self._timelineWidget.updateMediaDuration)
        self._media_url = None

        vsplit = QSplitter(Qt.Vertical)
        vsplit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vsplit.addWidget(video)


        self._toolbar = ToolbarWidget()
        self._toolbar.play.connect(self._player.play)
        self._toolbar.pause.connect(self._player.pause)

        vsplit.addWidget(self._toolbar)
        vsplit.addWidget(self._timelineWidget)

        vsplit.setStretchFactor(0, 1)
        vsplit.setStretchFactor(1, 1)
        vsplit.setStretchFactor(2, 3)

        hsplit = QHBoxLayout()
        picker_list = SymptomPickerList(self._symptoms)
        picker_list.on_create_symptom.connect(lambda symptom: self._onCreateSymptom(symptom))
        hsplit.addWidget(picker_list)
        hsplit.addWidget(vsplit)
        self.setLayout(hsplit)

    @Slot(QMediaPlayer.PlaybackState)
    def _update_toolbar(self, state):
        self._toolbar.setPlaying(state == QMediaPlayer.PlayingState)

    @Slot(Symptom)
    def _onCreateSymptom(self : Self, symptom_model : Symptom) -> None:
        dialog = AttributeEditor(self._symptoms, symptom_model, add=True)
        if not dialog.exec():
            return None
        self.addSymptomAtCursor(dialog.symptom())

    @Slot()
    def _togglePlayPause(self : Self) -> None:
        if self._player.isPlaying():
            self._player.pause()
        else:
            self._player.play()

    def _player_seek(self, position):
        self._player.setPosition(position)

    def _onSymptomEdit(self : Self, symptom : Symptom) -> None:
        dialog = AttributeEditor(self._symptoms, symptom, add=False)
        if not dialog.exec():
            return None
        symptom.attributes = dialog.symptom().attributes

    def _player_position_changed(self, position):
        self._timelineWidget.updateCursorPosition(position)
        self._toolbar.setTime(position)

    #def _player_duration_changed(self, duration):
    #    self._timelineGroupWidget.setDuration(duration)

    @Slot(QMediaPlayer.Error, str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)

    def _ensure_stopped(self):
        pass
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    def setVideo(self, uri):
        self._media_uri = uri.toString()
        self._ensure_stopped()
        self._player.setSource(uri)
        self._player.play()

    def setTimeline(self : Self, timeline : Timeline) -> None:
        self._timelineWidget.setTimeline(timeline)

    def setSymptomsDB(self : Self, database : SymptomDB) -> None:
        self._symptoms = database

    def addSymptomAtCursor(self : Self, symptom : Symptom):
        symptom.isInstance()
        self._timelineWidget.addSymptomAtTime(self._timelineWidget.cursorTime(), symptom)

    def export(self : Self) -> Timeline:
        return self._timelineWidget.getTimeline()

    def status(self):
        if self._player.playbackState() == QMediaPlayer.StoppedState:
            return {}
        return {
                "media": self._media_uri,
                "time": self._player.position()
        }

class Player(QMainWindow):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        self.initialize_menu_file()
        self.initialize_mime_types()
        self.initialize_file_dialog()

    def initialize_mime_types(self):
        supported_types = set([ QMediaFormat(f).mimeType().name()
            for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode) ])
        self._video_mime_types = list(filter(lambda x : x in supported_types, WANTED_VIDEO_MIME_TYPES))

    def initialize_file_dialog(self):
        self._default_location = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)

    def initialize_menu_file(self):
        file_menu = self.menuBar().addMenu(I18N("menu_files"))

        action_new  = QAction(I18N("menu_files_new"),
                             self,
                             shortcut=QKeySequence.New,
                             triggered=self.action_reset)
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
                               shortcut=QKeySequence(Qt.CTRL | Qt.Key_O),
                              triggered=self.action_import_timeline)
        action_exit = QAction(I18N("menu_files_exit"),
                              self,
                              shortcut=QKeySequence.Quit,
                              triggered=self.action_exit)

        file_menu.addAction(action_new)
        file_menu.addAction(action_export)
        file_menu.addAction(action_import_video)
        file_menu.addAction(action_import_timeline)
        file_menu.addAction(action_exit)

        self._loadSymptoms("symptoms.json")
        self._player = MainWidget(self._symptoms)
        self.setCentralWidget(self._player)

        #self._loadTimeline("/home/nathan/test.json")

    def _loadSymptoms(self : Self, filename : str) -> None:
        with open(filename, "r") as f:
            data = json.loads(f.read())
        self._symptoms = SymptomDB.deserialize(data)

    def _loadTimeline(self : Self, filename : str) -> None:
        with open(filename, "r") as f:
            data = json.loads(f.read())

        timeline = Timeline()
        for item in data:
            symptom = self._symptoms.fromPath(item["symptom"]["path"], item["symptom"]['attributes'])
            assert symptom is not None
            timeline.addSymptom(symptom, item['start'], item['end'])
        self._player.setTimeline(timeline)

    def action_reset(self : Self):
        self._player.setTimeline(Timeline())

    def action_export(self : Self) -> None:
        dialog = QFileDialog(self)
        dialog.setMimeTypeFilters(JSON_MIME_TYPES)
        dialog.selectMimeTypeFilter(JSON_MIME_TYPES[0])
        dialog.setDirectory(self._default_location)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec() != QDialog.Accepted:
            return

        self._default_location = dialog.directory().absolutePath()
        path = dialog.selectedFiles()[0]
        with open(path, "w+") as f:
            f.write(self._player.export().toJSON())

    def action_import_video(self : Self):
        file_dialog = QFileDialog(self)
        file_dialog.setMimeTypeFilters(self._video_mime_types)
        file_dialog.selectMimeTypeFilter(self._video_mime_types[0])
        file_dialog.setDirectory(self._default_location)
        if file_dialog.exec() == QDialog.Accepted:
            self._default_location = file_dialog.directory().absolutePath()
            uri = file_dialog.selectedUrls()[0]
            self._player.setVideo(uri)

    def action_import_timeline(self : Self):
        dialog = QFileDialog(self)
        dialog.setMimeTypeFilters(JSON_MIME_TYPES)
        dialog.selectMimeTypeFilter(JSON_MIME_TYPES[0])
        dialog.setDirectory(self._default_location)
        if dialog.exec() != QDialog.Accepted:
            return
        self._default_location = dialog.directory().absolutePath()
        self._loadTimeline(dialog.selectedFiles()[0])

    def action_exit(self):
        del self._player
        self.setCentralWidget(None)
        self.close()
