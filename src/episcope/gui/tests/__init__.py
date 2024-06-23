from episcope.core import SymptomDB

def defaultSymptomDB():
    return SymptomDB.deserialize({
        "attributes": [
            {
                "name": "topography",
                "type": "mix",
                "values": [
                    "head",
                    "body"
                ]
            }
        ],
        "objective_symptoms": [
            {
                "name": "Sensory",
                "children": [
                    {
                        "name": "Abdominal aura",
                        "custom_attributes": [
                            {
                                "name": "direction",
                                "type": "exclusive",
                                "values": [
                                    "cephalic",
                                    "epigastric"
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Deafness",
                    },
                ]
            },
            {
                "name": "Cognitive",
                "children": [
                    {
                        "name": "Heautoscopy",
                        "attributes": { "topography" : None }
                    },
                    {
                        "name": "Forced thinking"
                    }
                ]
            }
        ],
        "subjective_symptoms": [
            {
                "name": "Autonomic",
                "children": [
                    {
                        "name": "Urination"
                    }
                ]
            }
        ]
    })

