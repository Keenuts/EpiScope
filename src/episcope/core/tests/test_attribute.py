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
    with pytest.raises(schema.SchemaError):
        Attribute.deserialize({
            "name": "abc",
            "type": "mix",
        })

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
