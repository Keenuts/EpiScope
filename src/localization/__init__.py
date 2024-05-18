import json
import os

modulepath = os.path.dirname(os.path.realpath(__file__))
language = 'french'
with open('{}/{}.json'.format(modulepath, language), 'r') as f:
    translations = json.loads(f.read())

def I18N(key):
    if key in translations:
        return translations[key]
    return "label_" + key.replace(" ", "_")
