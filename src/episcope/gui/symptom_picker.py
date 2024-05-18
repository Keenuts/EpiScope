from typing import Union
from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel
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
from episcope.core import Symptom, Criteria, CriteriaType

class TreeComboBox(QComboBox):
    def __init__(self, *args):
        super().__init__(*args)
        self.setView(QTreeView())
        self.setRootModelIndex(QModelIndex())
        self.view().viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonPress and object is self.view().viewport():
            index = self.view().indexAt(event.pos())
            self.__skip_next_hide = not self.view().visualRect(index).contains(event.pos())
        return False

class SymptomTree(QAbstractItemModel):
    def __init__(self, symptoms : Symptom, parent=None):
        super().__init__(parent)
        self._root = symptoms

    def columnCount(self, parent):
        return 1

    def rowCount(self, parent):
        if not parent.isValid():
            return self._root.childCount()
        return parent.internalPointer().childCount()

    def hasChildren(self, parent):
        if not parent.isValid():
            return self._root.childCount() != 0
        return parent.internalPointer().childCount() != 0

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        #if index.internalPointer().childCount() != 0:
        #    return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root.name()
        return None

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.name()
        if role == Qt.UserRole:
            return item
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent = self._root
        else:
            parent = parent.internalPointer()

        child = parent.child(row)
        if child:
            return self.createIndex(row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        parent = node.parent()
        if parent == self._root:
            return QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

class MyCompleter(QCompleter):
    def splitPath(self, path):
        return path.split('/')

    def pathFromIndex(self, index):
        result = []
        while index.isValid():
            result = [self.model().data(index, Qt.DisplayRole)] + result
            index = index.parent()
        return '/'.join(result)

class CriteriaWidget(QWidget):
    def __init__(self, criteria, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert type(criteria) is Criteria

        self._criteria = criteria
        self._layout = QVBoxLayout()
        self._layout.addWidget(QLabel(criteria.name, self))
        self.setLayout(self._layout)
        self._options = []
        self._initOptions(criteria)

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
        return self._criteria.name

    def setEnabled(self, enabled):
        for option in self._options:
            option.setCheckable(enabled)
            option.setEnabled(enabled)
            option.setChecked(False)

class ExclusivePicker(CriteriaWidget):
    def _initOptions(self, criteria):
        for option in criteria.values:
            self._addOption(QRadioButton(option, self))

class MixPicker(CriteriaWidget):
    def _initOptions(self, criteria):
        for option in criteria.values:
            self._addOption(QCheckBox(option, self))

class SymptomPickerDialog(QDialog):
    def __init__(self, symptoms : Symptom, criterias : list[Criteria]):
        super().__init__()

        self.setWindowTitle(I18N("window_add_symptom"))

        self._buttonBox = QDialogButtonBox()
        self._buttonBox.addButton(I18N("button_create"), QDialogButtonBox.AcceptRole)
        self._buttonBox.addButton(I18N("button_cancel"), QDialogButtonBox.RejectRole)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)
        self._buttonBox.buttons()[0].setEnabled(False)

        self._model = SymptomTree(symptoms)
        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.setAutoScroll(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tree.clicked.connect(self._activated)

        self._criterias = []
        widget : Union[ExclusivePicker, MixPicker]
        for item in criterias:
            if item.type == CriteriaType.EXCLUSIVE:
                widget = ExclusivePicker(item)
            else:
                widget = MixPicker(item)
            self._criterias.append(widget)

        self._searchBox = QLineEdit()
        self._completer = MyCompleter(self._searchBox)
        self._completer.setModel(self._model)
        self._completer.setCompletionColumn(0)
        self._completer.setCompletionRole(Qt.DisplayRole)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.InlineCompletion)
        self._searchBox.setCompleter(self._completer)
        self._searchBox.textChanged.connect(self._activatedCompletion)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tree)
        self._layout.addWidget(self._searchBox)
        self._layout.addWidget(self._buttonBox)

        for criteria in self._criterias:
            self._layout.addWidget(criteria)
            criteria.setEnabled(False)
        self.setLayout(self._layout)

    def selection(self):
        index = self._tree.currentIndex()
        if not index.isValid():
            return None
        output = {
                'symptom': index.data(Qt.UserRole),
                'criterias': {
                }
        }
        for criteria in self._criterias:
            output['criterias'][criteria.name()] = criteria.selection()
        return output

    def _activated(self, index):
        if not index.isValid():
            return
        symptom = index.data(Qt.UserRole)
        if symptom.childCount() != 0:
            return

        path = symptom.path()
        self._completer.setCompletionPrefix(path)
        self._searchBox.setText(path)

    def _activatedCompletion(self, text):
        index = self._completer.currentIndex()
        if not index.isValid():
            return
        index = index.model().mapToSource(index)
        self._tree.setCurrentIndex(index)
        self._tree.setExpanded(index, True)
        self._tree.scrollTo(index)

        symptom = index.data(Qt.UserRole)
        if text.lower() != symptom.path().lower() or symptom.childCount() != 0:
            for criteria in self._criterias:
                criteria.setEnabled(False)
            return

        self._buttonBox.buttons()[0].setEnabled(True)
        for criteria in self._criterias:
            criteria.setEnabled(criteria.name() in symptom.criterias())

