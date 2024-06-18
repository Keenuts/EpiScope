import episcope.core
import pytest
import schema
from episcope.core import Attribute, AttributeType, Symptom, SymptomCategory

def test_category_name():
    category = SymptomCategory("category")
    assert category.name() == "category"

def test_category_insert():
    category = SymptomCategory("category")

    assert category.addSymptom(Symptom("a", [], None))

def test_category_insert_set_category():
    category = SymptomCategory("category")
    symptom = Symptom("a", [], None)

    category.addSymptom(symptom)

    assert symptom.category == category

def test_category_insert_twice():
    category = SymptomCategory("category")
    symptom = Symptom("a", [], None)

    category.addSymptom(symptom)

    assert not category.addSymptom(symptom)

def test_deserialize():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    assert symptom.name == "test"

def test_deserialize_bad_attribute():
    with pytest.raises(schema.SchemaError):
        symptom = Symptom.deserialize({}, {
            "name": "test",
            "attributes": [ 1 ]
        })

def test_deserialize_custom_attribute_default():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    assert symptom.attributes == []

def test_deserialize_custom_attribute_empty():
    symptom = Symptom.deserialize({}, {
        "name": "test",
        "custom_attributes": [ ]
    })

    assert symptom.attributes == []

def test_deserialize_custom_attribute():
    symptom = Symptom.deserialize({}, {
        "name": "test",
        "custom_attributes": [
            {
                "name": "attr",
                "type": "mix",
                "values": [ "a", "b" ]
            }
        ]
    })

    assert symptom.attributes == [ Attribute("attr", AttributeType.MIX, [ "a", "b" ]) ]

def test_deserialize_custom_attribute_invalid_duplicated_name():
    with pytest.raises(ValueError):
        Symptom.deserialize({}, {
            "name": "test",
            "custom_attributes": [
                {
                    "name": "attr",
                    "type": "mix",
                    "values": [ "a", "b" ]
                },
                {
                    "name": "attr",
                    "type": "mix",
                    "values": [ "a", "b" ]
                }
            ]
        })

def test_deserialize_custom_attribute_invalid_duplicated_name_from_global():
    with pytest.raises(ValueError):
        Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, []) }, {
            "name": "test",
            "custom_attributes": [
                {
                    "name": "attr",
                    "type": "mix",
                    "values": [ "a", "b" ]
                }
            ]
        })

def test_deserialize_custom_unknown_attribute():
    with pytest.raises(KeyError):
        Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, []) }, {
            "name": "test",
            "attributes": [ "abc" ]
        })

def test_deserialize_attribute():
    attribute = Attribute("attr", AttributeType.MIX, [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ]
    })

    assert symptom.attributes == [ attribute ]

def test_deserialize_attribute_merged():
    attribute = Attribute("attr", AttributeType.MIX, [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ],
        "custom_attributes": [
            {
                "name": "custom_attr",
                "type": "mix",
                "values": [ "a", "b" ]
            }
        ]
    })

    assert symptom.attributes == [ attribute, Attribute("custom_attr", AttributeType.MIX, [ "a", "b" ]) ]
