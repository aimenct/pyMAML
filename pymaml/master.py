import json
import xmltodict

from random import Random
from uuid import UUID, uuid4

from .elements.doc import MAMLDocument, MAMLDigitalThread


class MasterAML(MAMLDocument):
    '''
    Class to handle Master AML files (high level API)
    '''

    def __init__(self, input=None, replicableIDs=False) -> None:
        '''
        Initialize a Master AML from a dictionary, a JSON file path
        or an actual AML file path

        Set replicableIDs to True to always generate the same set of IDs,
        useful to compare files during development

        :param input: path to the AML/JSON file or dict with the simplified AML
        :type input: str or dict
        '''

        # Use replicable IDs during development
        self.replicableIDs = replicableIDs
        if self.replicableIDs:
            self.random = Random()
            self.random.seed(0)

        # List of IDs used to avoid duplicates
        self.IDs = []

        self.doc = self
        self.filePath = None

        if type(input) is str:
            self.filePath = input
            if '.aml' in input:
                self.fromAML(input)
            elif '.json' in input:
                self.fromJSON(input)

        elif isinstance(input, dict):
            self.fromDict(input)

        else:
            MAMLDocument.__init__(self, Document=self)

    def newDigitalThread(self) -> MAMLDigitalThread:
        ''' Add and return an empty Digital Thread to the current MasterAML '''
        dt = MAMLDigitalThread(Document=self)
        self['Digital Threads'].append(dt)
        return dt

    def export(self, filePath: str) -> None:
        ''' Save to an AML or JSON according to the file extension '''
        if '.aml' in filePath.lower():
            self.toAML(filePath)
        elif '.json' in filePath.lower():
            self.toJSON(filePath)
        else:
            raise NotImplementedError(f'Unsupported export format: {filePath}')

    def fromAML(self, filePath: str) -> None:
        ''' Load AML file '''
        xml = open(filePath, mode='r').read()
        xmld = xmltodict.parse(xml, force_list=True)
        MAMLDocument.__init__(self, Document=self, inputXMLD=xmld)

    def toAML(self, filePath: str) -> None:
        ''' Export current Master AML to an AML file '''
        xmld = self._encode_()
        xml = xmltodict.unparse(xmld, pretty=True)
        open(filePath, mode='w').write(xml)

    def fromDict(self, d: dict) -> None:
        ''' Load AML from a simplified dictionary '''
        MAMLDocument.__init__(self, Document=self, inputSimpleDict=d)

    def toDict(self) -> dict:
        ''' Export current Master AML as a simplified dictionary '''
        return dict(self)

    def fromJSON(self, filePath: str) -> None:
        ''' Load AML from a simplified dictionary stored in a JSON file '''
        self.fromDict(json.load(open(filePath, mode='r')))

    def toJSON(self, filePath: str) -> None:
        ''' Export current Master AML as a simplified dict to a JSON file '''
        json.dump(self.toDict(), open(filePath, mode='w'), indent=2)

    def registerID(self, ID: str) -> None:
        ''' Save IDs to avoid duplicates '''
        if str(ID) not in self.IDs:
            self.IDs.append(str(ID))

    def generateID(self) -> str:
        ''' Returns a new unique ID '''
        while True:
            if self.replicableIDs:
                id = str(UUID(int=self.random.getrandbits(16), version=4))
            else:
                id = str(uuid4())
            if id in self.IDs:
                continue
            self.registerID(id)
            return id
