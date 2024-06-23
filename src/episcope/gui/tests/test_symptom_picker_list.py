import pytest
from PySide6.QtCore import Qt, Signal
from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QWidget, QPushButton, QTabWidget, QToolButton, QStackedWidget

from episcope.core import SymptomDB, Symptom
from episcope.gui import SymptomPickerList
from episcope.localization import setLanguage
from episcope.gui.tests import defaultSymptomDB

def create_symptom_list(qtbot) -> SymptomPickerList:
    db = defaultSymptomDB()
    widget = SymptomPickerList(db)
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    return widget

def findButtonByName(widget : QWidget, name : str) -> QPushButton:
    for child in widget.findChildren(QPushButton):
        if child.text() == name:
            return child
    return None

def test_create(qtbot):
    widget = create_symptom_list(qtbot)

    assert widget.isVisible()

def test_tab_name_french(qtbot):
    setLanguage("french")
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)
    assert tabs is not None

    assert tabs.tabBar().tabText(tabs.currentIndex()) == "Objectif"
    assert tabs.tabBar().tabText(tabs.currentIndex() + 1) == "Subjectif"

def test_tab_name_english(qtbot):
    setLanguage("english")
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)
    assert tabs is not None

    assert tabs.tabBar().tabText(tabs.currentIndex()) == "Objective"
    assert tabs.tabBar().tabText(tabs.currentIndex() + 1) == "Subjective"

def test_tab_button_visible(qtbot):
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)
    assert tabs is not None

    tab = tabs.currentWidget()
    btn = findButtonByName(tab, "Abdominal aura")

    assert btn is not None
    assert btn.isVisible()

def test_tab_button_not_visible(qtbot):
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)
    assert tabs is not None

    tab = tabs.currentWidget()
    btn = findButtonByName(tab, "Urination")
    assert btn is None

def test_tab_click_tab(qtbot):
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)
    assert tabs is not None
    tabs.setCurrentIndex(1)

    tab = tabs.currentWidget()
    btn = findButtonByName(tab, "Urination")

    assert btn is not None
    assert btn.isVisible()

@pytest.mark.filterwarnings('ignore::RuntimeWarning') # Pytest internal binding issue.
def test_click_symptom_a(qtbot):
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)

    tab = tabs.currentWidget()
    btn = findButtonByName(tab, "Abdominal aura")
    with qtbot.waitSignal(widget.on_create_symptom) as blocker:
        btn.click()

    assert type(blocker.args[0]) is Symptom
    assert blocker.args[0].name == "Abdominal aura"

@pytest.mark.filterwarnings('ignore::RuntimeWarning') # Pytest internal binding issue.
def test_click_symptom_a(qtbot):
    widget = create_symptom_list(qtbot)
    tabs = widget.findChild(QTabWidget)
    tabs.setCurrentIndex(1)

    tab = tabs.currentWidget()
    btn = findButtonByName(tab, "Urination")
    with qtbot.waitSignal(widget.on_create_symptom) as blocker:
        btn.click()

    assert type(blocker.args[0]) is Symptom
    assert blocker.args[0].name == "Urination"
