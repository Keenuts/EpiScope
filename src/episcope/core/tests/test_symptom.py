import episcope.core
import pytest
import schema
from episcope.core import Attribute, AttributeType, Symptom, SymptomCategory

@pytest.fixture
def default_text_attribute() -> Attribute:
    return Attribute("notes", AttributeType.TEXT, values = [], selection = [])

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

    assert category.addSymptom(Symptom("a", {}, category = None, is_instance = False))

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

def test_deserialize_instance_with_notes():
    symptom = Symptom.deserialize({
        "notes": Attribute("notes", AttributeType.TEXT, values = [], selection = []),
        "attr": Attribute("attr", AttributeType.MIX, values = ["a", "b"], selection = [])
    }, {
        "name": "test",
        "attributes": {
            "attr": ["a"],
            "notes": [ "some notes" ]
        }
    })

    assert symptom.isInstance()
    assert len(symptom.attributes) == 2
    assert symptom.attributes['attr'].values == ['a', 'b']
    assert symptom.attributes['attr'].selection == ['a']
    assert symptom.attributes['notes'].values == []
    assert symptom.attributes['notes'].selection == ['some notes']

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

def test_deserialize_custom_attribute_default(default_text_attribute):
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    assert symptom.attributes == { "notes": default_text_attribute }
    assert not symptom.isInstance()

def test_deserialize_custom_attribute_empty(default_text_attribute):
    symptom = Symptom.deserialize({}, {
        "name": "test",
        "custom_attributes": [ ]
    })

    assert symptom.attributes == { "notes": default_text_attribute }
    assert not symptom.isInstance()

def test_deserialize_custom_attribute(default_text_attribute):
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

    assert symptom.attributes == { "attr": Attribute("attr", AttributeType.MIX, [ "a", "b" ], selection = []), "notes": default_text_attribute }
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

def test_deserialize_attribute(default_text_attribute):
    attribute = Attribute("attr", AttributeType.MIX, [], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": { "attr" : None }
    })

    assert symptom.attributes == { "attr": attribute, "notes": default_text_attribute}
    assert not symptom.isInstance()

def test_deserialize_attribute_canonical(default_text_attribute):
    attribute = Attribute("attr", AttributeType.MIX, [], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ]
    })

    assert symptom.attributes == { "attr": attribute, "notes": default_text_attribute }
    assert not symptom.isInstance()

def test_deserialize_attribute_merged(default_text_attribute):
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

    assert symptom.attributes == {
            "attr": attribute,
            "custom_attr": Attribute("custom_attr", AttributeType.MIX, [ "a", "b" ], selection = []),
            "notes": default_text_attribute }

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

def test_instance_no_change_model():
    symptom = Symptom.deserialize({}, {
        "name": "test"
    })

    instance = symptom.instantiate()
    instance.name = "something"

    assert symptom.name == "test"
    assert instance.name == "something"

def test_instance_no_change_attribute_model():
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

    instance = symptom.instantiate()
    instance.attributes['attr'].selection = [ 'a' ]

    assert instance.attributes['attr'].selection == [ 'a' ]
    assert symptom.attributes['attr'].selection == []

def test_tooltip_no_attribute():
    symptom = Symptom.deserialize({}, { "name": "test" })
    instance = symptom.instantiate()

    assert instance.getTooltipText() == "test"

def test_tooltip_no_attribute_set():
    attribute = Attribute("attr", AttributeType.MIX, values=["a", "b"], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ],
    })

    instance = symptom.instantiate()

    assert instance.getTooltipText() == "test"

def test_tooltip_mix_attribute_set():
    attribute = Attribute("attr", AttributeType.MIX, values=["a", "b"], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ],
    })

    instance = symptom.instantiate()
    instance.attributes['attr'].selection = [ 'a', 'b' ]

    assert instance.getTooltipText() == "test\n" + \
                                        " - attr: a, b"

def test_tooltip_multiple_attribute_set():
    attribute = Attribute("attr", AttributeType.MIX, values=["a", "b"], selection = [])
    symptom = Symptom.deserialize({ "attr": attribute }, {
        "name": "test",
        "attributes": [ "attr" ],
        "custom_attributes": [
            {
                "name": "custom_attr",
                "type": "exclusive",
                "values": [ "a", "b" ]
            }
        ]
    })

    instance = symptom.instantiate()
    instance.attributes['attr'].selection = [ 'a', 'b' ]
    instance.attributes['custom_attr'].selection = [ 'a' ]

    assert instance.getTooltipText() == "test\n" + \
                                        " - attr: a, b\n" + \
                                        " - custom_attr: a"
