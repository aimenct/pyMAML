import json
from uuid import uuid4
from hashlib import sha256
from pymaml.master import MasterAML


class ConversionTest():

    def __init__(self, filePath) -> None:
        # Read AML
        self.aml = MasterAML(filePath)

    def validate(self) -> bool:
        originalDict = self.aml.toDict()

        # Import from simplified dictionary and save to AML
        imported = MasterAML(originalDict)
        exportedPath = f'/tmp/{uuid4()}.aml'
        imported.export(exportedPath)

        # Read exported AML as a simplified dictionary
        self.reimported = MasterAML(exportedPath)
        reimportedDict = self.reimported.toDict()

        # Check equalness
        if self.hash(reimportedDict) == self.hash(originalDict):
            print(f'Conversion worked successfuly! --> {self.aml.filePath}')
            return True
        else:
            print(f'Conversion failed! --> {self.aml.filePath}')
            return False

    def hash(self, x: dict) -> str:
        h = sha256()
        h.update(bytes(json.dumps(x), 'utf-8'))
        return h.hexdigest()
