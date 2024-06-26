import json
from enum import Enum
from typing import Self
from dataclasses import dataclass
from schema import Schema, And, SchemaError, Optional


class AttributeType(Enum):
    GENERATOR = 0
    EXCLUSIVE = 1
    MIX = 2
    TEXT = 3

    @staticmethod
    def contains(value : str) -> bool:
        try:
            AttributeType[value]
        except ValueError:
            return False
        return True

@dataclass
class Attribute:
    name : str
    type : AttributeType
    values : list[str]
    selection : list[str]

    def getTooltipText(self : Self) -> str:
        assert len(self.selection) != 0

        output = "{}: ".format(self.name)
        if self.type == AttributeType.EXCLUSIVE:
            assert len(self.selection) == 1
            output += self.selection[0]
        elif self.type == AttributeType.TEXT:
            assert len(self.selection) == 1
            output += f"\n{self.selection[0]}"
        else:
            output += ", ".join(self.selection)
        return output

    def hasSelection(self : Self) -> bool:
        return len(self.selection) != 0

    def serialize(self : Self) -> dict:
        return self.selection

    @staticmethod
    def deserialize(data : dict):
        try:
            data = Attribute.validateSchema(data)

            attribute_type = AttributeType[data['type'].upper()]
            if attribute_type != AttributeType.TEXT:
                if len(data['values']) == 0:
                    raise SchemaError("values field is required for non-text attributes.")
                for x in data['selection']:
                    if x not in data['values']:
                        raise ValueError(f"Unknown value {x!r} for attribute {data['name']!r}.")

            if attribute_type != AttributeType.MIX and len(data['selection']) > 1:
                raise ValueError(f"Too many elements in field 'selection' of attribute {data['name']!r}.")
        except SchemaError as e:
            e.add_note('Parsed item was:\n{}'.format(json.dumps(data, indent=4)))
            raise

        return Attribute(data['name'], attribute_type, data['values'], selection = data['selection'])

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
                'name': str,
                'type': And(str, lambda x: AttributeType.contains(x.upper())),
                Optional('values', default=[]): [ str ],
                Optional('selection', default=[]): [ str ],

        })
        return schema.validate(data)
