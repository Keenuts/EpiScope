import json
import os

modulepath = os.path.dirname(os.path.realpath(__file__))
DEFAULT_LANGUAGE = 'french'
translations = {}

def I18N(key):
    if key in translations:
        return translations[key]
    return "label_" + key.replace(" ", "_")

def setLanguage(name : str) -> None:
    global translations
    with open('{}/{}.json'.format(modulepath, name), 'r') as f:
        translations = json.loads(f.read())

setLanguage(DEFAULT_LANGUAGE)
