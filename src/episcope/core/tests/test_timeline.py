import episcope.core
import pytest
import schema
from episcope.core import Attribute, AttributeType, Symptom, SymptomCategory, Timeline, ReportInfo

@pytest.fixture()
def category() -> SymptomCategory:
    return SymptomCategory("objective", "category")

@pytest.fixture()
def sample_report_info() -> ReportInfo:
    return ReportInfo("AB12", "John Smith", "2024-06-01", "Some notes\non a new line")

@pytest.fixture()
def a(category) -> Symptom:
    output = Symptom("a", attributes = {}, category = None, is_instance = False).instantiate()
    category.addSymptom(output)
    return output

@pytest.fixture()
def b(category) -> Symptom:
    output = Symptom("b", attributes = {}, category = None, is_instance = False).instantiate()
    category.addSymptom(output)
    return output

@pytest.fixture()
def c(category) -> Symptom:
    output = Symptom("c", attributes = {}, category = None, is_instance = False).instantiate()
    category.addSymptom(output)
    return output

def test_default():
    timeline = Timeline()

def test_default(sample_report_info):
    timeline = Timeline()

    assert timeline.getSymptoms() == []
    assert timeline.getDuration() == 0
    assert timeline.toJSON() == "[]"
    assert timeline.getNextSymptom(0) is None
    assert timeline.getPreviousSymptom(0) is None
    assert timeline.toReport(sample_report_info) == \
"""Patient number: AB12
Doctor name: John Smith
Date: 2024-06-01

Observations:
  Some notes
  on a new line

Chronology:
"""

def test_add_symptom(a, b):
    timeline = Timeline()
    a = Symptom("a", attributes = {}, category = None, is_instance = False).instantiate()
    b = Symptom("b", attributes = {}, category = None, is_instance = False).instantiate()

    id_a = timeline.addSymptom(a, 0, 10)
    id_b = timeline.addSymptom(b, 1, 10)

    assert timeline.getDuration() == 10
    assert len(timeline.getSymptoms()) == 2
    assert timeline.getSymptoms()[0].identifier == id_a
    assert timeline.getSymptoms()[1].identifier == id_b
    assert timeline.getSymptoms()[0].symptom == a
    assert timeline.getSymptoms()[1].symptom == b

def test_edit_symptom_change_start(a, b, c):
    timeline = Timeline()
    id_a = timeline.addSymptom(a, 0, 10)
    id_b = timeline.addSymptom(b, 1, 10)
    id_c = timeline.addSymptom(c, 2, 10)

    assert timeline.getSymptoms()[0].identifier == id_a
    assert timeline.getSymptoms()[1].identifier == id_b
    assert timeline.getSymptoms()[2].identifier == id_c

    timeline.updateSymptom(id_a, start = 3)

    assert timeline.getSymptoms()[0].identifier == id_b
    assert timeline.getSymptoms()[1].identifier == id_c
    assert timeline.getSymptoms()[2].identifier == id_a
    assert timeline.getSymptoms()[2].start == 3
    assert timeline.getSymptoms()[2].duration == 7

def test_edit_symptom_change_end(a, b, c):
    timeline = Timeline()
    id_a = timeline.addSymptom(a, 0, 10)
    id_b = timeline.addSymptom(b, 1, 10)
    id_c = timeline.addSymptom(c, 2, 10)

    assert timeline.getSymptoms()[0].identifier == id_a
    assert timeline.getSymptoms()[1].identifier == id_b
    assert timeline.getSymptoms()[2].identifier == id_c

    timeline.updateSymptom(id_a, end = 3)

    assert timeline.getSymptoms()[0].identifier == id_a
    assert timeline.getSymptoms()[1].identifier == id_b
    assert timeline.getSymptoms()[2].identifier == id_c
    assert timeline.getSymptoms()[0].start == 0
    assert timeline.getSymptoms()[0].duration == 3

def test_edit_symptom_change_start_and_end(a, b, c):
    timeline = Timeline()
    id_a = timeline.addSymptom(a, 0, 10)
    id_b = timeline.addSymptom(b, 1, 10)
    id_c = timeline.addSymptom(c, 2, 10)

    assert timeline.getSymptoms()[0].identifier == id_a
    assert timeline.getSymptoms()[1].identifier == id_b
    assert timeline.getSymptoms()[2].identifier == id_c

    timeline.updateSymptom(id_a, start = 12, end = 15)

    assert timeline.getSymptoms()[0].identifier == id_b
    assert timeline.getSymptoms()[1].identifier == id_c
    assert timeline.getSymptoms()[2].identifier == id_a
    assert timeline.getSymptoms()[2].start == 12
    assert timeline.getSymptoms()[2].duration == 3

def test_edit_symptom_change_symptom(a, b):
    timeline = Timeline()
    id_a = timeline.addSymptom(a, 0, 10)

    assert len(timeline.getSymptoms()) == 1
    assert timeline.getSymptoms()[0].symptom.name == "a"

    timeline.updateSymptom(id_a, symptom = b)

    assert len(timeline.getSymptoms()) == 1
    assert timeline.getSymptoms()[0].symptom.name == "b"

def test_edit_symptom_change_unknown_id(a, b, c):
    timeline = Timeline()
    a = Symptom("a", attributes = {}, category = None, is_instance = False).instantiate()
    b = Symptom("b", attributes = {}, category = None, is_instance = False).instantiate()
    id_a = timeline.addSymptom(a, 0, 10)

    assert id_a != 234234 # Should never happen, but if it does, change this test (it is valid).
    with pytest.raises(KeyError) as e:
        timeline.updateSymptom(234234, symptom = b)

    assert str(e.value) == "'Invalid identifier 234234.'"

def test_get_item(a, b, c):
    timeline = Timeline()
    id_a = timeline.addSymptom(a, 0, 10)
    id_b = timeline.addSymptom(b, 1, 10)
    id_c = timeline.addSymptom(c, 2, 10)

    assert timeline.getItem(id_a).symptom == a
    assert timeline.getItem(id_b).symptom == b
    assert timeline.getItem(id_c).symptom == c

def test_get_next_prev(a, b, c):
    timeline = Timeline()

    id_a = timeline.addSymptom(a, 0, 10)
    id_b = timeline.addSymptom(b, 1, 10)
    id_c = timeline.addSymptom(c, 2, 10)

    assert timeline.getNextSymptom(id_a) == timeline.getItem(id_b)
    assert timeline.getNextSymptom(id_b) == timeline.getItem(id_c)
    assert timeline.getNextSymptom(id_c) == None
    assert timeline.getPreviousSymptom(id_a) == None
    assert timeline.getPreviousSymptom(id_b) == timeline.getItem(id_a)
    assert timeline.getPreviousSymptom(id_c) == timeline.getItem(id_b)

def test_toJSON(a, b, c):
    timeline = Timeline()
    timeline.addSymptom(c, 2, 10)
    timeline.addSymptom(a, 0, 10)
    timeline.addSymptom(b, 1, 10)

    output = timeline.toJSON()

    assert output == \
"""[
    {
        "symptom": {
            "path": "objective/category/a",
            "attributes": {}
        },
        "start": 0,
        "end": 10
    },
    {
        "symptom": {
            "path": "objective/category/b",
            "attributes": {}
        },
        "start": 1,
        "end": 10
    },
    {
        "symptom": {
            "path": "objective/category/c",
            "attributes": {}
        },
        "start": 2,
        "end": 10
    }
]"""

def test_toReport(a, b, c, sample_report_info):
    timeline = Timeline()
    timeline.addSymptom(c, 2, 10)
    timeline.addSymptom(a, 0, 10)
    timeline.addSymptom(b, 1, 10)

    output = timeline.toReport(sample_report_info)

    assert output == \
"""Patient number: AB12
Doctor name: John Smith
Date: 2024-06-01

Observations:
  Some notes
  on a new line

Chronology:
   0 - start 00:00, duration 00:00, (end 00:00):
	a
   1 - start 00:00, duration 00:00, (end 00:00):
	b
   2 - start 00:00, duration 00:00, (end 00:00):
	c
"""
