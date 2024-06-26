import episcope.core
import pytest
import schema
from episcope.core import Attribute, AttributeType

def test_deserialize():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "exclusive",
        "values": [ "a", "b" ]
    })

    assert attribute.name == "abc"
    assert attribute.type == AttributeType.EXCLUSIVE
    assert attribute.values == [ "a", "b" ]
    assert attribute.selection == [ ]

def test_deserialize_selection():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "exclusive",
        "values": [ "a", "b" ],
        "selection": [ "a" ]
    })

    assert attribute.name == "abc"
    assert attribute.type == AttributeType.EXCLUSIVE
    assert attribute.values == [ "a", "b" ]
    assert attribute.selection == [ "a" ]

def test_deserialize_bad_selection():
    with pytest.raises(ValueError) as e:
        attribute = Attribute.deserialize({
            "name": "abc",
            "type": "exclusive",
            "values": [ "a", "b" ],
            "selection": [ "c" ]
        })
    assert str(e.value) == "Unknown value 'c' for attribute 'abc'."

def test_missing_name():
    with pytest.raises(schema.SchemaMissingKeyError):
        Attribute.deserialize({
            "type": "exclusive",
            "values": [ "a", "b" ]
        })

def test_missing_type():
    with pytest.raises(schema.SchemaMissingKeyError):
        Attribute.deserialize({
            "name": "abc",
            "values": [ "a", "b" ]
        })

def test_bad_type():
    with pytest.raises(schema.SchemaError):
        Attribute.deserialize({
            "name": "abc",
            "type": "invalid_type",
            "values": [ "a", "b" ]
        })

def test_missing_values():
    with pytest.raises(schema.SchemaError) as e:
        Attribute.deserialize({
            "name": "abc",
            "type": "mix",
        })
    assert str(e.value) == "values field is required for non-text attributes."

def test_missing_values_for_text_type():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "text",
    })

    assert attribute.type == AttributeType.TEXT

def test_bad_value_types():
    with pytest.raises(schema.SchemaError):
        Attribute.deserialize({
            "name": "abc",
            "type": "mix",
            "values": 123
        })

def test_tooltip_exclusive():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "exclusive",
        "values": [ "a", "b" ],
        "selection": [ "a" ]
    })

    assert attribute.getTooltipText() == "abc: a"

def test_exclusive_bad_selection_multiple():
    with pytest.raises(ValueError) as e:
        attribute = Attribute.deserialize({
            "name": "abc",
            "type": "exclusive",
            "values": [ "a", "b" ],
            "selection": [ "a", "b" ]
        })
    assert str(e.value) == "Too many elements in field 'selection' of attribute 'abc'."

def test_text_bad_selection_multiple():
    with pytest.raises(ValueError) as e:
        attribute = Attribute.deserialize({
            "name": "abc",
            "type": "text",
            "selection": [ "a", "b" ]
        })
    assert str(e.value) == "Too many elements in field 'selection' of attribute 'abc'."

def test_tooltip_exclusive_bad_selection_multiple():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "exclusive",
        "values": [ "a", "b" ]
    })

    attribute.selection = [ "a", "b" ]
    with pytest.raises(AssertionError):
        attribute.getTooltipText()

def test_tooltip_text_bad_selection_multiple():
    attribute = Attribute.deserialize({
        "name": "notes",
        "type": "text",
    })
    attribute.selection = [ "some text", "some other text" ]

    with pytest.raises(AssertionError):
        attribute.getTooltipText()


def test_tooltip_exclusive_bad_selection_empty():
    with pytest.raises(AssertionError):
        attribute = Attribute.deserialize({
            "name": "def",
            "type": "exclusive",
            "values": [ "a", "b" ],
            "selection": []
        })
        attribute.getTooltipText()

def test_tooltip_mix_single():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "mix",
        "values": [ "a", "b", "c" ],
        "selection": [ "b" ]
    })

    assert attribute.getTooltipText() == "abc: b"

def test_tooltip_mix_multiple():
    attribute = Attribute.deserialize({
        "name": "abc",
        "type": "mix",
        "values": [ "a", "b", "c" ],
        "selection": [ "b", "a" ]
    })

    assert attribute.getTooltipText() == "abc: b, a"

def test_tooltip_text():
    attribute = Attribute.deserialize({
        "name": "notes",
        "type": "text",
        "selection": [ "some text"]
    })

    assert attribute.getTooltipText() == "notes: \n" + \
                                         "some text"

def test_tooltip_text_bad_selection_empty():
    with pytest.raises(AssertionError):
        attribute = Attribute.deserialize({
            "name": "notes",
            "type": "text",
            "selection": []
        })
        attribute.getTooltipText()

def test_tooltip_text_multiline():
    attribute = Attribute.deserialize({
        "name": "notes",
        "type": "text",
        "selection": [ "some text\n" + \
                       "some other line" ]
    })

    assert attribute.getTooltipText() == "notes: \n" + \
                                         "some text\n" + \
                                         "some other line"

def test_tooltip_text_escaping():
    attribute = Attribute.deserialize({
        "name": "notes",
        "type": "text",
        "selection": [ "some text \"with\" characters" ]
    })

    assert attribute.getTooltipText() == "notes: \n" + \
                                         "some text \"with\" characters"
