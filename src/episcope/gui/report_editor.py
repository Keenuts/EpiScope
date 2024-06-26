import dataclasses
from typing import Union, override, Self, Optional
from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel, Slot, Signal, QDate
from PySide6.QtWidgets import (QDialog,
                               QDialogButtonBox,
                               QLabel,
                               QLineEdit,
                               QDateEdit,
                               QVBoxLayout,
                               QWidget,
                               QSizePolicy,
                               QTextEdit)

from episcope.localization import I18N
from episcope.core import Symptom, Attribute, AttributeType, SymptomDB, ReportInfo

class ReportEditor(QDialog):
    #_default_selection : dict[str, set[str]] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(I18N("window_edit_report"))

        self._buttonBox = QDialogButtonBox()
        self._buttonBox.addButton(I18N("button_ok"), QDialogButtonBox.ButtonRole.AcceptRole)
        self._buttonBox.addButton(I18N("button_cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)

        self._patient = QLineEdit()
        self._date = QDateEdit(QDate.currentDate())
        self._date.setDisplayFormat("dd MMM yyyy")
        self._date.setCalendarPopup(True)
        self._doctor = QLineEdit()
        self._notes = QTextEdit()


        self._layout = QVBoxLayout()
        self._layout.addWidget(QLabel(I18N("label_patient_number")))
        self._layout.addWidget(self._patient)
        self._layout.addWidget(QLabel(I18N("label_doctor_name")))
        self._layout.addWidget(self._doctor)
        self._layout.addWidget(QLabel(I18N("label_report_date")))
        self._layout.addWidget(self._date)
        self._layout.addWidget(QLabel(I18N("label_report_notes")))
        self._layout.addWidget(self._notes)
        self._layout.addWidget(self._buttonBox)
        self.setLayout(self._layout)

        #self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #self.adjustSize()

        #self._checkFormValid()

    #@staticmethod
    #def _defaultSelection(name : str) -> set[str]:
    #    return set()

    #@staticmethod
    #def _setDefaultSelection(name : str, values : set[str]) -> None:
    #    pass

    def data(self : Self) -> ReportInfo:
        date = self._date.date()
        date_str = "{:4}-{:02}-{:02}".format(date.year(), date.month(), date.day())
        return ReportInfo(self._patient.text(), self._doctor.text(), date_str, self._notes.toPlainText())
