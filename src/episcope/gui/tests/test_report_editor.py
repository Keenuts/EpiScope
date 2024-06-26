import pytest
from PySide6.QtCore import Qt, QDate
from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QDateEdit

from episcope.core import ReportInfo
from episcope.gui import ReportEditor
from episcope.localization import setLanguage

# Sets some global variables (language) and resets a known singleton to
# help isolate tests.
@pytest.fixture(autouse=True)
def fixGlobalState():
    setLanguage("english")

def checkNonNull(value):
    assert value is not None
    return value

def create_dialog(qtbot) -> ReportEditor:
    widget = ReportEditor()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    return widget

def findButton(widget : QWidget, text : str) -> QPushButton:
    for child in widget.findChildren(QPushButton):
        print(child.text())
        if child.text() == text:
            return child
    return None

@pytest.fixture
def dialog(qtbot) -> ReportEditor:
    return create_dialog(qtbot)

def test_localization_title_english(dialog):
    assert dialog.windowTitle() == "Report edition"

def test_localization_title_english(qtbot):
    setLanguage("french")
    dialog = create_dialog(qtbot)
    assert dialog.windowTitle() == "Édition de rapport"

def test_localization_buttons_english(dialog):
    assert findButton(dialog, "OK") is not None
    assert findButton(dialog, "Cancel") is not None

def test_localization_buttons_french(qtbot):
    setLanguage("french")
    dialog = create_dialog(qtbot)

    assert findButton(dialog, "OK") is not None
    assert findButton(dialog, "Annuler") is not None

def test_localization_labels(dialog):
    labels = dialog.findChildren(QLabel)
    assert labels[0].text() == "Patient number"
    assert labels[1].text() == "Doctor"
    assert labels[2].text() == "Date"

def test_localization_labels_french(qtbot):
    setLanguage("french")
    dialog = create_dialog(qtbot)

    labels = dialog.findChildren(QLabel)
    assert labels[0].text() == "Numéro de patient"
    assert labels[1].text() == "Docteur"
    assert labels[2].text() == "Date"

def test_localization_labels(qtbot, dialog):
    lines = dialog.findChildren(QLineEdit)
    date = dialog.findChild(QDateEdit)
    notes = dialog.findChild(QTextEdit)

    lines[0].setText("first")
    lines[1].setText("second")
    notes.setPlainText("notes")
    date.setDate(QDate(2024, 6, 1))
    qtbot.mouseClick(checkNonNull(findButton(dialog, "OK")), Qt.MouseButton.LeftButton)

    assert dialog.data() == ReportInfo("first", "second", "2024-06-01", "notes")

