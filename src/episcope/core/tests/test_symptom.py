import episcope.core
import pytest
import schema
from episcope.core import Attribute, AttributeType, Symptom, SymptomCategory

def test_category_name():
    category = SymptomCategory("objective", "category")
    assert category.name() == "category"

def test_category_name_invalid():
    with pytest.raises(ValueError) as e:
        category = SymptomCategory("objective", "category/blabla")
    assert str(e.value) == "Illegal character '/' in category name 'category/blabla'."

def test_category_family_invalid():
    with pytest.raises(ValueError) as e:
        category = SymptomCategory("objective/blibli", "category/blabla")
    assert str(e.value) == "Illegal character '/' in family name 'objective/blibli'."

def test_category_insert():
    category = SymptomCategory("objective", "category")

    assert category.addSymptom(Symptom("a", [], category = None, is_instance = False))

def test_category_insert_set_category():
    category = SymptomCategory("objective", "category")
    symptom = Symptom("a", attributes = {}, category = None, is_instance = False)

    category.addSymptom(symptom)

    assert symptom.category == category

def test_category_insert_twice():
    category = SymptomCategory("objective", "category")
    symptom = Symptom("a", attributes = {}, category = None, is_instance = False)

    category.addSymptom(symptom)

    assert not category.addSymptom(symptom)

def test_deserialize():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    assert symptom.name == "test"
    assert not symptom.isInstance()

def test_instance_default():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    assert not symptom.isInstance()

def test_instance_after_instantiate():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    instance = symptom.instantiate()

    assert not symptom.isInstance()
    assert instance.isInstance()

def test_deserialize_attribute_model_global():
    symptom = Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, values = ["a", "b"], selection = []) }, {
        "name": "test",
        "attributes": [ "attr" ]
    })

    assert not symptom.isInstance()
    assert symptom.attributes['attr'].values == ['a', 'b']
    assert symptom.attributes['attr'].selection == []

def test_deserialize_instance_global():
    symptom = Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, values = ["a", "b"], selection = []) }, {
        "name": "test",
        "attributes": {
            "attr": ["a"]
        }
    })

    assert symptom.isInstance()
    assert symptom.attributes['attr'].values == ['a', 'b']
    assert symptom.attributes['attr'].selection == ['a']

def test_deserialize_instance_global_unknown_value():
    with pytest.raises(ValueError) as e:
        symptom = Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, values = ["a", "b"], selection = []) }, {
            "name": "test",
            "attributes": {
                "attr": ["unknown"]
            }
        })
    assert str(e.value) == "Unknown value 'unknown' for attribute 'attr'."

def test_deserialize_instance_custom():
    symptom = Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, values = ["a", "b"], selection = []) }, {
        "name": "test",
        "custom_attributes": [
            {
                "name": "custom",
                "type": "mix",
                "values": [ "a", "b" ],
                "selection": [ "a" ]
            }
        ]
    })

    assert symptom.isInstance()
    assert symptom.attributes['custom'].values == ['a', 'b']
    assert symptom.attributes['custom'].selection == ['a']

def test_deserialize_bad_attribute():
    with pytest.raises(ValueError) as e:
        symptom = Symptom.deserialize({}, {
            "name": "test",
            "attributes": 1
        })
    assert str(e.value) == "Unable to deserialize Symptom."
    assert e.value.__notes__[0] == \
"""Parsed item was:
{
    "name": "test",
    "attributes": 1
}"""

def test_deserialize_custom_attribute_default():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    assert symptom.attributes == {}
    assert not symptom.isInstance()

def test_deserialize_custom_attribute_empty():
    symptom = Symptom.deserialize({}, {
        "name": "test",
        "custom_attributes": [ ]
    })

    assert symptom.attributes == {}
    assert not symptom.isInstance()

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

    assert symptom.attributes == { "attr": Attribute("attr", AttributeType.MIX, [ "a", "b" ], selection = []) }
    assert not symptom.isInstance()

def test_deserialize_custom_attribute_invalid_duplicated_name():
    with pytest.raises(ValueError) as e:
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
    assert str(e.value) == "Duplicate name for custom attribute 'attr'."

def test_deserialize_custom_attribute_invalid_duplicated_name_from_global():
    with pytest.raises(ValueError) as e:
        Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, [], selection = []) }, {
            "name": "test",
            "custom_attributes": [
                {
                    "name": "attr",
                    "type": "mix",
                    "values": [ "a", "b" ]
                }
            ]
        })
    assert str(e.value) == "Duplicate name for custom attribute 'attr'."

def test_deserialize_custom_unknown_attribute():
    with pytest.raises(ValueError) as e:
        Symptom.deserialize({ "attr": Attribute("attr", AttributeType.MIX, [], selection = []) }, {
            "name": "test",
            "attributes": { "abc" : None }
        })

    assert str(e.value) == "Unknown global attribute 'abc'."

def test_deserialize_attribute():
    attribute = Attribute("attr", AttributeType.MIX, [], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": { "attr" : None }
    })

    assert symptom.attributes == { "attr": attribute }
    assert not symptom.isInstance()

def test_deserialize_attribute_canonical():
    attribute = Attribute("attr", AttributeType.MIX, [], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ]
    })

    assert symptom.attributes == { "attr": attribute }
    assert not symptom.isInstance()

def test_deserialize_attribute_merged():
    attribute = Attribute("attr", AttributeType.MIX, [], selection = [])
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

    assert symptom.attributes == { "attr": attribute, "custom_attr": Attribute("custom_attr", AttributeType.MIX, [ "a", "b" ], selection = []) }

def test_serialize():
    category = SymptomCategory("objective", "category")
    symptom = Symptom("a", attributes = {}, category = None, is_instance = False)
    category.addSymptom(symptom)

    instance = symptom.instantiate()

    assert instance.serialize() == {
            "path": "objective/category/a",
            "attributes": {}
    }

def test_serialize_global_attribute():
    attribute = Attribute("attr", AttributeType.MIX, values=["a", "b"], selection = [])
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
    category = SymptomCategory("subjective", "some_category")
    category.addSymptom(symptom)

    instance = symptom.instantiate()
    instance.attributes['attr'].selection = [ 'a' ]

    assert instance.serialize() == {
            "path": "subjective/some_category/test",
            "attributes": {
                "attr": [ "a" ]
            }
    }

def test_serialize_attributes():
    attribute = Attribute("attr", AttributeType.MIX, values=["a", "b"], selection = [])
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
    category = SymptomCategory("subjective", "some_category")
    category.addSymptom(symptom)

    instance = symptom.instantiate()
    instance.attributes['attr'].selection = [ 'a' ]
    instance.attributes['custom_attr'].selection = [ 'b' ]

    assert instance.serialize() == {
            "path": "subjective/some_category/test",
            "attributes": {
                "attr": [ "a" ],
                "custom_attr": [ "b" ]
            }
    }
