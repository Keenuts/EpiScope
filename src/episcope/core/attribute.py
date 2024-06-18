import json
from enum import Enum
from typing import Self
from dataclasses import dataclass
from schema import Schema, And, SchemaError


class AttributeType(Enum):
    GENERATOR = 0
    EXCLUSIVE = 1
    MIX = 2

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

    @staticmethod
    def deserialize(data : dict):
        try:
            data = Attribute.validateSchema(data)
        except SchemaError as e:
            e.add_note('Parsed item was:\n{}'.format(json.dumps(data, indent=4)))
            raise
        return Attribute(data['name'], AttributeType[data['type'].upper()], data['values'])

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
                'name': str,
                'type': And(str, lambda x: AttributeType.contains(x.upper())),
                'values': [ str ]
        })
        return schema.validate(data)
