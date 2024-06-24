import dataclasses
from typing import Union, override, Self, Optional
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
                               QWidget,
                               QSizePolicy)

from episcope.localization import I18N
from episcope.core import Symptom, Attribute, AttributeType, SymptomDB

class AttributeWidget(QWidget):
    clicked = Signal()

    def __init__(self : Self, attribute : Attribute, default_values : set[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert type(attribute) is Attribute

        self._attribute = attribute
        self._options : list[Union[QRadioButton, QCheckBox]] = []

        self._layout = QVBoxLayout()
        self._layout.addWidget(QLabel(attribute.name, self))
        self.setLayout(self._layout)
        self._initOptions(attribute, default_values)

    def _initOptions(self : Self, attribute : Attribute) -> None:
        pass

    def _addOption(self, widget : Union[QRadioButton, QCheckBox]):
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

    def isSelectionValid(self : Self) -> bool:
        return True

class ExclusivePicker(AttributeWidget):
    @override
    def _initOptions(self : Self, attribute : Attribute, default_values : set[str]) -> None:
        can_use_defaults = len(attribute.selection) == 0
        for option in attribute.values:
            w = QRadioButton(option, self)
            w.clicked.connect(lambda: self.clicked.emit())
            if can_use_defaults:
                w.setChecked(option in default_values)
            else:
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
    def _initOptions(self : Self, attribute : Attribute, default_values : set[str]) -> None:
        can_use_defaults = len(attribute.selection) == 0
        for option in attribute.values:
            w = QCheckBox(option, self)
            w.clicked.connect(lambda: self.clicked.emit())
            if can_use_defaults:
                w.setChecked(option in default_values)
            else:
                w.setChecked(option in attribute.selection)
            self._addOption(w)

class AttributeEditor(QDialog):
    _default_selection : dict[str, set[str]] = {}

    def __init__(self, database : SymptomDB, symptom : Symptom, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._symptom = symptom

        if symptom.isInstance():
            self.setWindowTitle(I18N("window_edit_symptom"))
        else:
            self.setWindowTitle(I18N("window_add_symptom"))

        self._buttonBox = QDialogButtonBox()
        if symptom.isInstance():
            self._buttonBox.addButton(I18N("button_save"), QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            self._buttonBox.addButton(I18N("button_create"), QDialogButtonBox.ButtonRole.AcceptRole)
        self._buttonBox.addButton(I18N("button_cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        self._buttonBox.accepted.connect(self._accept)
        self._buttonBox.rejected.connect(self.reject)
        self._buttonBox.buttons()[0].setEnabled(False)

        self._attribute_widgets : list[Union[ExclusivePicker, MixPicker]] = []
        for name, item in symptom.attributes.items():
            widget : Union[ExclusivePicker, MixPicker]
            if item.type == AttributeType.EXCLUSIVE:
                widget = ExclusivePicker(item, AttributeEditor._defaultSelection(name))
            else:
                widget = MixPicker(item, AttributeEditor._defaultSelection(name))
            widget.clicked.connect(self._checkFormValid)
            self._attribute_widgets.append(widget)

        self._layout = QVBoxLayout()
        for widget in self._attribute_widgets:
            self._layout.addWidget(widget)
        self._layout.addWidget(self._buttonBox)
        self.setLayout(self._layout)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.adjustSize()

        self._checkFormValid()

    @staticmethod
    def _defaultSelection(name : str) -> set[str]:
        if name in AttributeEditor._default_selection:
            return AttributeEditor._default_selection[name]
        return set()

    @staticmethod
    def _setDefaultSelection(name : str, values : set[str]) -> None:
        AttributeEditor._default_selection[name] = values

    @Slot()
    def _checkFormValid(self : Self):
        self._buttonBox.buttons()[0].setEnabled(self._canAccept())

    def _canAccept(self : Self) -> bool:
        for widget in self._attribute_widgets:
            if not widget.isSelectionValid():
                return False
        return True

    def _accept(self : Self):
        for w in self._attribute_widgets:
            AttributeEditor._setDefaultSelection(w.name(), w.selection())
        self.accept()

    def symptom(self):
        if self._symptom.isInstance():
            output = self._symptom
        else:
            output = self._symptom.instantiate()

        for w in self._attribute_widgets:
            assert w.name() in output.attributes
            output.attributes[w.name()].selection = w.selection()
        return output
