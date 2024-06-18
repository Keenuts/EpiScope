from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Self
from schema import Schema, Optional, SchemaError

from episcope.core import SymptomCategory, Attribute

@dataclass
class SymptomDB:
    attributes : list[Attribute]
    objective : list[SymptomCategory]
    subjective : list[SymptomCategory]

    @staticmethod
    def deserialize(data : dict):
        try:
            data = SymptomDB.validateSchema(data)
        except SchemaError as e:
            e.add_note('Parsed item was:\n{}'.format(json.dumps(data, indent=4)))
            raise

        tmp = [ Attribute.deserialize(x) for x in data['attributes'] ]
        attributes = {}
        for x in tmp:
            attributes[x.name] = x

        subjective = [ SymptomCategory.deserialize(attributes, x) for x in data['subjective_symptoms'] ]
        objective = [ SymptomCategory.deserialize(attributes, x) for x in data['objective_symptoms'] ]
        return SymptomDB(attributes, objective, subjective)

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
            "attributes": list[dict],
            "objective_symptoms": list[dict],
            "subjective_symptoms": list[dict]
        })
        return schema.validate(data)

