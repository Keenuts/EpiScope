<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="./docs/source/images/Logo_final.png" alt="Logo" width="1000" height="220">
  <h1 align="center">EpiScope</h1>
</div>


**EpiScope** is a python-based GUI featuring ergonomic tools for annotating epileptic seizure videos. 

These tools enable practitioners to note directly on their patients' epileptic seizure videos the various symptoms that appear, thanks to a pre-configured symptom semiology. This interface generates a .txt text file listing all the symptoms occurring during the seizure in chronological order, as well as a timeline illustrating the patient's epileptic seizure. The timeline follows a temporal axis (identical to that of the seizure video) and indicates the moment of onset and end of each symptom. Practitioners must also be able to modify the .txt file and the frieze in the event of an oversight or readjustment.

<br />
<div align="center">
  <img src="./docs/source/images/interface_utilisee2.png" alt="interface" width="500" height="268">
</div>

**Documentation :** 
-----------------
  You can find the official Episcope documentation here : https://episcope.readthedocs.io/en/latest/

**Running :**
----------------

One time:

```bash
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

To run the app:

```bash
. venv/bin/activate
python src/app.py
```

**Development**
---------------

This section assumes the environment is already setup.
To run all tests:

```bash
pytest
```

To run the static type analysis:

```bash
mypy
```
