import pytest
from PySide6.QtCore import Qt, Signal
from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QWidget, QPushButton, QTabWidget, QToolButton, QStackedWidget, QDialogButtonBox

from episcope.core import SymptomDB, Symptom
from episcope.gui import AttributeEditor, MixPicker, ExclusivePicker
from episcope.localization import setLanguage
from episcope.gui.tests import defaultSymptomDB

# Sets some global variables (language) and resets a known singleton to
# help isolate tests.
@pytest.fixture(autouse=True)
def fixGlobalState():
    setLanguage("english")
    AttributeEditor._default_selection = {}

def checkNonNull(value):
    assert value is not None
    return value

def create(qtbot, db : SymptomDB, model : Symptom) -> AttributeEditor:
    widget = AttributeEditor(db, model)
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    return widget

def test_localization_add_english(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    w = create(qtbot, db, symptom)

    assert w.windowTitle() == "Add a new symptom"

def test_localization_add_french(qtbot):
    setLanguage("french")

    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    w = create(qtbot, db, symptom)

    assert w.windowTitle() == "Ajouter un nouveau symptome"

def test_localization_edit_english(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    instance = symptom.instantiate()
    w = create(qtbot, db, instance)

    assert w.windowTitle() == "Edit symptom"

def test_localization_edit_french(qtbot):
    setLanguage("french")

    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    instance = symptom.instantiate()
    w = create(qtbot, db, instance)

    assert w.windowTitle() == "Edition du symptome"

def findButton(widget : QWidget, text : str) -> QPushButton:
    for child in widget.findChildren(QPushButton):
        if child.text() == text:
            return child
    return None

def test_localization_add_buttons_french(qtbot):
    setLanguage("french")
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    w = create(qtbot, db, symptom)

    assert findButton(w, "Créer") is not None
    assert findButton(w, "Annuler") is not None

def test_localization_add_buttons_english(qtbot):
    setLanguage("english")
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    w = create(qtbot, db, symptom)

    assert findButton(w, "Create") is not None
    assert findButton(w, "Cancel") is not None

def test_localization_edit_buttons_french(qtbot):
    setLanguage("french")
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    instance = symptom.instantiate()
    w = create(qtbot, db, instance)

    assert findButton(w, "Enregister") is not None
    assert findButton(w, "Annuler") is not None

def test_localization_edit_buttons_english(qtbot):
    setLanguage("english")
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    instance = symptom.instantiate()
    w = create(qtbot, db, instance)

    assert findButton(w, "Save") is not None
    assert findButton(w, "Cancel") is not None

def test_no_attribute_no_widget(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Deafness")
    w = create(qtbot, db, symptom)

    children = w.findChildren(QWidget, options=Qt.FindDirectChildrenOnly)

    assert len(children) == 1
    assert type(children[0]) is QDialogButtonBox

def test_mix_attribute_checkbox_widget(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Cognitive/Heautoscopy")
    w = create(qtbot, db, symptom)

    children = w.findChildren(MixPicker, options=Qt.FindDirectChildrenOnly)
    assert len(children) == 1
    assert children[0].name() == "topography"
    assert len(children[0].options()) == 2
    assert children[0].options()[0].text() == "head"
    assert children[0].options()[1].text() == "body"

def test_mix_attribute_checkbox_widget_selection(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Cognitive/Heautoscopy")
    instance = symptom.instantiate()
    instance.attributes['topography'].selection = ['head']

    w = create(qtbot, db, instance)

    children = w.findChildren(MixPicker, options=Qt.FindDirectChildrenOnly)
    assert len(children) == 1
    assert children[0].name() == "topography"
    assert len(children[0].options()) == 2
    assert children[0].options()[0].text() == "head"
    assert children[0].options()[0].isChecked() is True
    assert children[0].options()[1].text() == "body"
    assert children[0].options()[1].isChecked() is False

def test_exclusive_attribute_radio_widget(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    w = create(qtbot, db, symptom)

    children = w.findChildren(ExclusivePicker, options=Qt.FindDirectChildrenOnly)
    assert len(children) == 1
    assert children[0].name() == "direction"
    assert len(children[0].options()) == 2
    assert children[0].options()[0].text() == "cephalic"
    assert children[0].options()[1].text() == "epigastric"

def test_exclusive_attribute_radio_widget_selection(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")
    instance = symptom.instantiate()
    instance.attributes['direction'].selection = ['epigastric']
    w = create(qtbot, db, instance)

    children = w.findChildren(ExclusivePicker, options=Qt.FindDirectChildrenOnly)
    assert len(children) == 1
    assert children[0].name() == "direction"
    assert len(children[0].options()) == 2
    assert children[0].options()[0].text() == "cephalic"
    assert children[0].options()[0].isChecked() == False
    assert children[0].options()[1].text() == "epigastric"
    assert children[0].options()[1].isChecked() == True

def test_exclusive_attribute_radio_widget_default_selection(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")

    w = create(qtbot, db, symptom)
    picker = w.findChild(ExclusivePicker, options=Qt.FindDirectChildrenOnly)
    picker.options()[1].click()
    qtbot.mouseClick(checkNonNull(findButton(w, "Create")), Qt.MouseButton.LeftButton)

    assert symptom.attributes['direction'].selection == []

    w = create(qtbot, db, symptom)
    picker = w.findChild(ExclusivePicker, options=Qt.FindDirectChildrenOnly)

    assert not picker.options()[0].isChecked()
    assert picker.options()[1].isChecked()

def test_exclusive_attribute_radio_widget_default_selection_on_reject(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")

    w = create(qtbot, db, symptom)
    picker = w.findChild(ExclusivePicker, options=Qt.FindDirectChildrenOnly)
    picker.options()[1].click()
    qtbot.mouseClick(checkNonNull(findButton(w, "Cancel")), Qt.MouseButton.LeftButton)

    assert symptom.attributes['direction'].selection == []

    w = create(qtbot, db, symptom)
    picker = w.findChild(ExclusivePicker, options=Qt.FindDirectChildrenOnly)

    assert not picker.options()[0].isChecked()
    assert not picker.options()[1].isChecked()

def test_exclusive_attribute_symptom_creation(qtbot):
    db = defaultSymptomDB()
    symptom = db.fromPath("objective_symptoms/Sensory/Abdominal aura")

    w1 = create(qtbot, db, symptom)
    picker = w1.findChild(ExclusivePicker, options=Qt.FindDirectChildrenOnly)

    picker.options()[0].click()
    picker.options()[1].click()
    qtbot.mouseClick(checkNonNull(findButton(w1, "Create")), Qt.MouseButton.LeftButton)

    result = w1.symptom()
    assert result.isInstance()
    assert result.name == "Abdominal aura"
    assert result.attributes['direction'].selection == [ "epigastric" ]

    w2 = create(qtbot, db, symptom)
    picker = w2.findChild(ExclusivePicker, options=Qt.FindDirectChildrenOnly)

    picker.options()[1].click()
    picker.options()[0].click()
    qtbot.mouseClick(checkNonNull(findButton(w2, "Create")), Qt.MouseButton.LeftButton)

    result = w2.symptom()
    assert result.isInstance()
    assert result.name == "Abdominal aura"
    assert result.attributes['direction'].selection == [ "cephalic" ]
