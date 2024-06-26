from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Self, Union
from schema import Schema, Optional, SchemaError, Or

import json
import traceback
import copy

from episcope.core import Attribute, AttributeType

@dataclass
class Symptom:
    name : str
    attributes : dict[str, Attribute]
    category : SymptomCategory
    is_instance : bool

    def __init__(self : Self, name : str, attributes : dict[str, Attribute], category : SymptomCategory, is_instance : bool) -> None:
        self.name = name
        self.attributes = attributes
        self.category = category
        self.is_instance = is_instance

        if 'notes' not in self.attributes:
            self.attributes['notes'] = Attribute('notes', AttributeType.TEXT, [], [])

    def instantiate(self : Self) -> Self:
        output = copy.deepcopy(self)
        output.is_instance = True
        return output

    def instantiateFromJSON(self : Self, attributes : dict[str, list[str]]) -> Self:
        output = self.instantiate()

        for name, values in attributes.items():
            if name not in self.attributes:
                raise ValueError(f"Invalid attribute {name!r} for symptom {parts[2]!r}.")

            output.attributes[name].selection = values
            if self.attributes[name].type == AttributeType.TEXT:
                continue

            for x in values:
                if x not in self.attributes[name].values:
                    raise ValueError(f"Invalid attribute value {x!r} for attribute {name!r}.")
        return output

    def isInstance(self : Self) -> bool:
        return self.is_instance

    def getTooltipText(self : Self) -> str:
        assert self.isInstance()
        output = self.name
        for _, attribute in self.attributes.items():
            if len(attribute.selection) == 0:
                continue;
            if attribute.type == AttributeType.TEXT:
                output += "\n{}".format(attribute.getTooltipText())
            else:
                output += "\n - {}".format(attribute.getTooltipText())
        return output

    def serialize(self : Self) -> dict:
        # For now, this is the only valid usage. If this changes, implement support for it.
        assert self.isInstance()

        path = f"{self.category.family()}/{self.category.name()}/{self.name}"

        attributes = dict()
        for name, value in self.attributes.items():
            if value.hasSelection():
                attributes[name] = value.serialize()
        return {
                'path': path,
                'attributes': attributes
        }

    @staticmethod
    def _checkAttribute(name : str, selection : list[str], global_attributes : dict[Attribute]) -> None:
        if name not in global_attributes:
            raise ValueError(f"Unknown global attribute {name!r}.")

        attribute = global_attributes[name]
        if attribute.type == AttributeType.TEXT:
            return

        if selection is None:
            return

        for item in selection:
            if item not in attribute.values:
                raise ValueError(f"Unknown value {item!r} for attribute {name!r}.")

    @staticmethod
    def deserialize(global_attributes : dict[Attribute], data : dict):
        try:
            data = Symptom.validateSchema(data)
            custom_attributes = [ Attribute.deserialize(x) for x in data['custom_attributes'] ]

            attributes = dict()
            is_instance = False

            if type(data['attributes']) is list:
                attributes_to_parse = dict()
                for item in data['attributes']:
                    attributes_to_parse[item] = None
            else:
                attributes_to_parse = data['attributes']

            for name, values in attributes_to_parse.items():
                Symptom._checkAttribute(name, values, global_attributes)

                attributes[name] = global_attributes[name]
                if values is not None:
                    attributes[name].selection = values
                    is_instance = True

            for item in custom_attributes:
                if item.name in attributes or item.name in global_attributes:
                    raise ValueError(f"Duplicate name for custom attribute {item.name!r}.")
                attributes[item.name] = item
                if len(item.selection) != 0:
                    is_instance = True
        except SchemaError:
            e = ValueError("Unable to deserialize Symptom.")
            e.add_note(f"Parsed item was:\n{json.dumps(data, indent=4)}")
            raise e
        except ValueError as e:
            e.add_note(f"Parsed item was:\n{json.dumps(data, indent=4)}")
            raise
        return Symptom(data['name'], attributes, category = None, is_instance = is_instance)

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
                'name': str,
                Optional('custom_attributes', default=[]): [ dict ],
                Optional('attributes', default=dict()): Or(dict[str, Union[None, list[str]]], list[str]),
        })
        return schema.validate(data)

class SymptomCategory:
    def __init__(self : Self, symptom_family : str, name : str):
        if '/' in symptom_family:
            raise ValueError(f"Illegal character '/' in family name {symptom_family!r}.")
        self._symptom_family = symptom_family

        if '/' in name:
            raise ValueError(f"Illegal character '/' in category name {name!r}.")
        self._name : str = name
        self._children : list[Symptom] = []

    def name(self : Self) -> str:
        return self._name

    def family(self : Self) -> str:
        return self._symptom_family

    def symptoms(self : Self) -> list[Symptom]:
        return self._children

    def addSymptom(self : Self, symptom : Symptom) -> bool:
        if len([ x for x in self._children if x.name == symptom.name ]):
            return False

        symptom.category = self
        self._children.append(symptom)
        return True

    @staticmethod
    def deserialize(symptom_family : str, attributes : list[Attribute], data : dict):
        try:
            data = SymptomCategory.validateSchema(data)
        except SchemaError as e:
            e.add_note('Parsed item was:\n{}'.format(json.dumps(data, indent=4)))
            raise

        output = SymptomCategory(symptom_family, data['name'])
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
