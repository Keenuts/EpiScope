import pytest
from episcope.core import SymptomDB, Attribute, AttributeType

SAMPLE_DB = {
    "attributes" : [
        {
            "name" : "topography",
            "type" : "mix",
            "values" : [
                "Body",
                "Eyelids"
            ]
        },
        {
            "name" : "lateralized",
            "type" : "exclusive",
            "values" : [
                "left",
                "right"
            ]
        }
    ],
    "subjective_symptoms" : [
        {
            "name": "category1",
            "children" : [
                  {
                     "name" : "Symptom1",
                     "custom_attributes" : [
                        {
                            "name" : "direction",
                            "type" : "exclusive",
                            "values" : [
                               "Cephalic to epigastric",
                               "Epigastric to cephalic"
                            ]
                        }
                     ],
                     "attributes" : [ "topography" ]
                  },
                  {
                     "name" : "Symptom2"
                  }
            ]
        },
        {
            "name": "category2",
            "children" : [
                  {
                     "name" : "Symptom3"
                  }
            ]
        }
    ],
    "objective_symptoms" : [
        {
            "name": "category3",
            "children" : [
                  {
                     "name" : "Symptom4"
                  }
            ]
        },
        {
            "name": "category4",
            "children" : [
                  {
                     "name" : "Symptom5"
                  }
            ]
        }
    ]
}

def test_deserialize():
    db = SymptomDB.deserialize(SAMPLE_DB)

    assert len(db.attributes) == 2
    assert len(db.objective) == 2
    assert len(db.subjective) == 2

    assert db.attributes['topography'].name == "topography"
    assert db.attributes['topography'].type == AttributeType.MIX
    assert db.attributes['topography'].values == [ "Body", "Eyelids" ]

    assert db.attributes['lateralized'].name == "lateralized"
    assert db.attributes['lateralized'].type == AttributeType.EXCLUSIVE
    assert db.attributes['lateralized'].values == [ "left", "right" ]

    assert db.subjective[0].name() == "category1"
    assert db.subjective[0].symptoms()[0].name == "Symptom1"
    assert db.subjective[0].symptoms()[0].attributes['topography'] == db.attributes['topography']
    assert db.subjective[0].symptoms()[0].attributes['direction'] == Attribute(
            name="direction", type=AttributeType.EXCLUSIVE, values=["Cephalic to epigastric", "Epigastric to cephalic"], selection=[])

    assert db.subjective[0].symptoms()[1].name == "Symptom2"
    assert db.subjective[1].name() == "category2"
    assert db.subjective[1].symptoms()[0].name == "Symptom3"
    assert db.objective[0].name() == "category3"
    assert db.objective[0].symptoms()[0].name == "Symptom4"
    assert db.objective[1].name() == "category4"
    assert db.objective[1].symptoms()[0].name == "Symptom5"

def test_frompath():
    db = SymptomDB.deserialize(SAMPLE_DB)

    instance = db.fromPath("subjective_symptoms/category1/Symptom1", { "topography": ["Body"] })

    assert instance.isInstance()
    assert instance.name == "Symptom1"
    assert instance.attributes['topography'].selection == [ "Body" ]
    assert instance.attributes['direction'].selection == []

def test_frompath_bad_path():
    db = SymptomDB.deserialize(SAMPLE_DB)
    with pytest.raises(ValueError) as e:
        instance = db.fromPath("randomcategory1/Symptom1", { "topography": ["Body"] })
    assert str(e.value) == "Invalid symptom path 'randomcategory1/Symptom1'. Expected format: 'familiy/category/symptom'."

def test_frompath_bad_family():
    db = SymptomDB.deserialize(SAMPLE_DB)
    with pytest.raises(ValueError) as e:
        instance = db.fromPath("y/x/Symptom1", { "topography": ["Body"] })
    assert str(e.value) == "Invalid symptom path 'y/x/Symptom1'. Unknown family 'y'."

def test_frompath_bad_category():
    db = SymptomDB.deserialize(SAMPLE_DB)
    with pytest.raises(ValueError) as e:
        instance = db.fromPath("subjective_symptoms/x/Symptom1", { "topography": ["Body"] })
    assert str(e.value) == "Invalid symptom path 'subjective_symptoms/x/Symptom1'. Unknown category 'x'."

def test_frompath_bad_symptom():
    db = SymptomDB.deserialize(SAMPLE_DB)
    with pytest.raises(ValueError) as e:
        instance = db.fromPath("subjective_symptoms/category1/SymptomX", { "topography": ["Body"] })
    assert str(e.value) == "Invalid symptom path 'subjective_symptoms/category1/SymptomX'. Unknown symptom 'SymptomX'."

def test_frompath_bad_attribute():
    db = SymptomDB.deserialize(SAMPLE_DB)
    with pytest.raises(ValueError) as e:
        instance = db.fromPath("subjective_symptoms/category1/Symptom1", { "lateralized": ["Body"] })
    assert str(e.value) == "Invalid attribute 'lateralized' for symptom 'Symptom1'."
