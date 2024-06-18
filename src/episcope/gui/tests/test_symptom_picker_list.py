import pytest
from PySide6.QtCore import Qt, Signal
from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QWidget, QPushButton, QTabWidget, QToolButton, QStackedWidget

from episcope.core import SymptomDB, Symptom
from episcope.gui import SymptomPicker
from episcope.localization import setLanguage

def defaultSymptomDB():
    return SymptomDB.deserialize({
        "attributes": [
            {
                "name": "topography",
                "type": "mix",
                "values": [
                    "head",
                    "body"
                ]
            }
        ],
        "objective_symptoms": [
            {
                "name": "Sensory",
                "children": [
                    {
                        "name": "Abdominal aura",
                        "custom_attributes": [
                            {
                                "name": "direction",
                                "type": "exclusive",
                                "values": [
                                    "cephalic",
                                    "epigastric"
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Deafness",
                    },
                ]
            },
            {
                "name": "Cognitive",
                "children": [
                    {
                        "name": "Heautoscopy",
                        "attributes": { "topography" : None }
                    },
                    {
                        "name": "Forced thinking"
                    }
                ]
            }
        ],
        "subjective_symptoms": [
            {
                "name": "Autonomic",
                "children": [
                    {
                        "name": "Urination"
                    }
                ]
            }
        ]
    })

def create_symptom_list(qtbot) -> SymptomPicker:
    db = defaultSymptomDB()
    widget = SymptomPicker(db)
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
