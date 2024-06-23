from PySide6.QtCore import QStandardPaths, Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QDialog,
                               QFileDialog,
                               QLabel,
                               QMainWindow,
                               QSplitter,
                               QFrame,
                               QStyle,
                               QToolBar,
                               QHBoxLayout,
                               QVBoxLayout,
                               QWidget,
                               QTabWidget,
                               QListWidget,
                               QGroupBox,
                               QScrollArea,
                               QPushButton,
                               QSizePolicy,
                               QSpacerItem)
from PySide6.QtMultimedia import QAudioOutput, QMediaFormat, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from typing import Self, Optional

import sys
import json
from episcope.localization import I18N
from episcope.core import Timeline, Symptom, SymptomCategory, SymptomDB, Attribute

class SymptomList(QWidget):
    on_create_symptom = Signal(Symptom)

    def __init__(self, symptoms : list[SymptomCategory], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        vertical_layout = QVBoxLayout()
        for category in symptoms:
            group = QGroupBox(category.name())
            group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            group_layout = QVBoxLayout()
            group.setLayout(group_layout)
            for symptom in category.symptoms():
                button = QPushButton(symptom.name)
                button.clicked.connect(lambda _, symptom=symptom: self.on_create_symptom.emit(symptom))
                group_layout.addWidget(button)
            vertical_layout.addWidget(group)
        vertical_layout.addStretch()

        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        widget = QWidget()
        widget.setLayout(vertical_layout)
        scroll.setWidget(widget)

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)

class SymptomPickerList(QWidget):
    on_create_symptom = Signal(Symptom)

    def __init__(self, symptoms : SymptomDB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout = QVBoxLayout()
        self.setLayout(layout)

        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        for name, sublist in [('tab_objective', symptoms.objective), ("tab_subjective", symptoms.subjective)]:
            tab = SymptomList(sublist)
            tab.on_create_symptom.connect(lambda value: self.on_create_symptom.emit(value))
            tabs.addTab(tab, I18N(name))

        layout.addWidget(tabs)
