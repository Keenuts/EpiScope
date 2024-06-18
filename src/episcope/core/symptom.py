from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Self
from schema import Schema, Optional, SchemaError

import json

from episcope.core import Attribute, AttributeType

@dataclass
class Symptom:
    name : str
    attributes : list[Attribute]
    category : SymptomCategory

    @staticmethod
    def deserialize(global_attributes : dict[Attribute], data : dict):
        try:
            data = Symptom.validateSchema(data)
            custom_attributes = [ Attribute.deserialize(x) for x in data['custom_attributes'] ]
            custom_attribute_names = set([ x.name for x in custom_attributes])
            global_attribute_names = set([ x for x in global_attributes])
            if len(custom_attribute_names) != len(custom_attributes) or \
                    len(global_attribute_names.intersection(custom_attribute_names)) != 0:
                raise ValueError("Duplicate name for custom attributes.")

            attributes = [ global_attributes[x] for x in data['attributes'] ]
        except (SchemaError, ValueError) as e:
            e.add_note('Parsed item was:\n{}'.format(json.dumps(data, indent=4)))
            raise
        return Symptom(data['name'], attributes + custom_attributes, None)

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
                'name': str,
                Optional('custom_attributes', default=[]): [ dict ],
                Optional('attributes', default=[]): [ str ],
        })
        return schema.validate(data)

class SymptomCategory:
    def __init__(self : Self, name : str):
        self._name = name
        self._children = []

    def name(self : Self) -> str:
        return self._name

    def addSymptom(self : Self, symptom : Symptom) -> bool:
        if len([ x for x in self._children if x.name == symptom.name ]):
            return False

        symptom.category = self
        self._children.append(symptom)
        return True

    @staticmethod
    def deserialize(attributes : list[Attribute], data : dict):
        try:
            data = SymptomCategory.validateSchema(data)
        except SchemaError as e:
            e.add_note('Parsed item was:\n{}'.format(json.dumps(data, indent=4)))
            raise

        output = SymptomCategory(data['name'])
        for child in data['children']:
            output.addSymptom(Symptom.deserialize(attributes, child))
        return output

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
                'name': str,
                'children': [ dict ]
        })
        return schema.validate(data)
