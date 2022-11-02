# pyMAML
Python library for Master AutomationML files.

pyMAML implements a bidirectional conversion between the complex AML files and a much intuitive native dictionary stored in a JSON file.



## Installation

1. Install and activate a Python 3.10 environment

2. Setup the Python libraries: `pip install -r requirements.txt`



## Usage

To convert AML files to a simpler dictionary, without the XML overhead, use the following commands:

```bash
# Convert to simplified dictionary and store in a JSON file
python -m pymaml input.aml [output.json]

# Example:
python -m pymaml testfiles/penelope/master.aml
cat testfiles/penelope/master.json

# Convert dictionary back to AML
python -m pymaml testfiles/penelope/master.json testfiles/penelope/exported.aml
```

More examples available at the [examples folder](examples).




## Documentation

- Setup the required python modules: `pip install sphinx sphinx_rtd_theme`
- Update the .rst files: `sphinx-apidoc -o docs pymaml/`
- Generate the HTML from the docs folder: `cd docs; make clean; make html`



## Acknowledgements

This project has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 958303.
