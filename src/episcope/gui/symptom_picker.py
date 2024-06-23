import dataclasses
from typing import Union, override, Self
from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel, Slot, Signal
from PySide6.QtWidgets import (QAbstractItemView,
                               QCheckBox,
                               QComboBox,
                               QCompleter,
                               QDialog,
                               QDialogButtonBox,
                               QLabel,
                               QLineEdit,
                               QRadioButton,
                               QTreeView,
                               QVBoxLayout,
                               QWidget)

from episcope.localization import I18N
from episcope.core import Symptom, Attribute, AttributeType, SymptomDB

class AttributeWidget(QWidget):
    clicked = Signal()

    def __init__(self, attribute, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert type(attribute) is Attribute

        self._attribute = attribute
        self._layout = QVBoxLayout()
        self._layout.addWidget(QLabel(attribute.name, self))
        self.setLayout(self._layout)
        self._options = []
        self._initOptions(attribute)

    def _addOption(self, widget):
        self._options.append(widget)
        self._layout.addWidget(widget)

    def selection(self):
        output = []
        for option in self._options:
            if option.isChecked():
                output.append(option.text())
        return output

    def name(self):
        return self._attribute.name

    def options(self : Self) -> list[Union[QRadioButton, QCheckBox]]:
        return self._options

    def setEnabled(self, enabled):
        for option in self._options:
            option.setCheckable(enabled)
            option.setEnabled(enabled)
            option.setChecked(False)

    def isSelectionValid(self : Self) -> bool:
        return True

class ExclusivePicker(AttributeWidget):
    @override
    def _initOptions(self, attribute):
        for option in attribute.values:
            w = QRadioButton(option, self)
            w.clicked.connect(lambda: self.clicked.emit())
            w.setChecked(option in attribute.selection)
            self._addOption(w)

    @override
    def isSelectionValid(self : Self) -> bool:
        for option in self.options():
            if option.isChecked():
                return True
        return False

class MixPicker(AttributeWidget):
    @override
    def _initOptions(self, attribute):
        for option in attribute.values:
            w = QCheckBox(option, self)
            w.clicked.connect(lambda: self.clicked.emit())
            w.setChecked(option in attribute.selection)
            self._addOption(w)

class AttributeEditor(QDialog):
    def __init__(self, database : SymptomDB, model : Symptom, add = True):
        super().__init__()
        self._model = model

        if add:
            self.setWindowTitle(I18N("window_add_symptom"))
        else:
            self.setWindowTitle(I18N("window_edit_symptom"))

        self._buttonBox = QDialogButtonBox()
        if add:
            self._buttonBox.addButton(I18N("button_create"), QDialogButtonBox.AcceptRole)
        else:
            self._buttonBox.addButton(I18N("button_save"), QDialogButtonBox.AcceptRole)
        self._buttonBox.addButton(I18N("button_cancel"), QDialogButtonBox.RejectRole)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)
        self._buttonBox.buttons()[0].setEnabled(False)

        self._attribute_widgets : list[AttributeWidget] = []
        for name, item in model.attributes.items():
            widget : Union[ExclusivePicker, MixPicker]
            if item.type == AttributeType.EXCLUSIVE:
                widget = ExclusivePicker(item)
            else:
                widget = MixPicker(item)
            widget.clicked.connect(self._checkFormValid)
            self._attribute_widgets.append(widget)

        self._layout = QVBoxLayout()
        for widget in self._attribute_widgets:
            self._layout.addWidget(widget)
        self._layout.addWidget(self._buttonBox)
        self.setLayout(self._layout)
        self._checkFormValid()

    @Slot()
    def _checkFormValid(self : Self):
        self._buttonBox.buttons()[0].setEnabled(self._canAccept())

    def _canAccept(self : Self) -> bool:
        for widget in self._attribute_widgets:
            if not widget.isSelectionValid():
                return False
        return True

    def symptom(self):
        output = self._model.instantiate()
        for w in self._attribute_widgets:
            assert w.name() in output.attributes
            output.attributes[w.name()].selection = w.selection()
        return output
