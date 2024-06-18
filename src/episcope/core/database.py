from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Self
from schema import Schema, Optional, SchemaError

from episcope.core import SymptomCategory, Symptom, Attribute

@dataclass
class SymptomDB:
    attributes : list[Attribute]
    objective : list[SymptomCategory]
    subjective : list[SymptomCategory]

    def fromPath(self : Self, path : str, attributes : dict[str, list[str]]) -> Symptom:
        parts = path.split("/")
        if len(parts) != 3:
            raise ValueError(f"Invalid symptom path {path!r}. Expected format: 'familiy/category/symptom'.")

        if parts[0] == "objective_symptoms":
            family = self.objective
        elif parts[0] == "subjective_symptoms":
            family = self.subjective
        else:
            raise ValueError(f"Invalid symptom path {path!r}. Unknown family {parts[0]!r}.")

        needle = None
        for category in family:
            if category.name() == parts[1]:
                needle = category
                break
        if needle is None:
            raise ValueError(f"Invalid symptom path {path!r}. Unknown category {parts[1]!r}.")

        output = None
        for symptom in category.symptoms():
            if symptom.name == parts[2]:
                output = symptom.instantiate()
                break;
        if output is None:
            raise ValueError(f"Invalid symptom path {path!r}. Unknown symptom {parts[2]!r}.")

        for name, values in attributes.items():
            if name not in symptom.attributes:
                raise ValueError(f"Invalid attribute {name!r} for symptom {parts[2]!r}.")
            for x in values:
                if x not in symptom.attributes[name].values:
                    raise ValueError(f"Invalid attribute value {x!r} for attribute {name!r}.")
                output.attributes[name].selection.append(x)
        return output

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

        subjective = [ SymptomCategory.deserialize("subjective_symptoms", attributes, x) for x in data['subjective_symptoms'] ]
        objective = [ SymptomCategory.deserialize("objective_symptoms", attributes, x) for x in data['objective_symptoms'] ]
        return SymptomDB(attributes, objective, subjective)

    @staticmethod
    def validateSchema(data : dict):
        schema = Schema({
            "attributes": list[dict],
            "objective_symptoms": list[dict],
            "subjective_symptoms": list[dict]
        })
        return schema.validate(data)

