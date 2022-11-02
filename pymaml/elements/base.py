import json
from copy import deepcopy
from abc import abstractmethod


class MAMLBaseElement(dict):

    _TEMPLATE_ = {}

    _TEMPLATE_XMLD_ = None

    # List of XML @Attributes to load
    _ATTRIBUTES_XML_ = [
        'Name',
        'ID',
    ]

    # List of Attribute tags to load its Value
    _ATTRIBUTES_TAG_ = []

    def __init__(
        self,
        # Master AML Document
        Document,
        # Current Digital Thread
        DigitalThread=None,
        # XML Dictionary
        inputXMLD: dict = None,
        # Simplified Dictionary
        inputSimpleDict: dict = None,
    ):
        # Link Master AML Document
        self.doc = Document

        # Link current Digital Thread if provided
        if DigitalThread is not None:
            self.dt = DigitalThread

        # Initialize dictionary
        super().__init__()
        self.clear()

        # Load from XML dict if provided
        if inputXMLD is not None:
            self._decode_(inputXMLD)
        else:
            # Load XML dict template
            self.xmld = self._loadXMLDtemplate()

        # Load from the Simplified Dict if provided
        if inputXMLD is None and inputSimpleDict is not None:
            super().update(inputSimpleDict)

        self._registerSelfIDs_()

    def clear(self) -> None:
        ''' Overload to initialize Simplified Dict with default template '''
        super().clear()
        super().update(deepcopy(self._TEMPLATE_))

        # Initialize own ID
        if 'ID' in self and self['ID'] is None:
            self['ID'] = self.doc.generateID()

    @abstractmethod
    def _decode_(self, xmld) -> None:
        ''' Load the simplified representation from an XML dictionary '''
        # Store XMLD input
        self.xmld = xmld

        # Reset Simplified Dictionary
        self.clear()

        # Load XML attributes
        for attr in self._ATTRIBUTES_XML_:
            try:
                self[attr] = self.xmld[f'@{attr}']
            except KeyError:
                continue

        # Load Attribute tags
        try:
            for attr in self.xmld['Attribute']:
                try:
                    if attr['@Name'] in self._ATTRIBUTES_TAG_:
                        if 'Value' not in attr:
                            continue
                        self[attr['@Name']] = attr['Value'][0]
                except (KeyError, IndexError):
                    continue
        except KeyError:
            pass

        # Solve External Interfaces
        if 'ExternalInterface' in self.xmld:
            for ei in self.xmld['ExternalInterface']:
                try:
                    targetID = self.dt._solveEI_(ei['@ID'])
                    if targetID is None:
                        continue
                    if ei['@Name'] in self:
                        self[ei['@Name']].append(targetID)
                except KeyError:
                    continue

    @abstractmethod
    def _encode_(self) -> dict:
        ''' Export the simplified representation to an XML dictionary '''
        # Clear stored XML dict
        del self.xmld

        # Load XML dict template
        self.xmld = self._loadXMLDtemplate()

        # Load XML attributes
        for attr in self._ATTRIBUTES_XML_:
            try:
                self.xmld[f'@{attr}'] = self[attr]
            except KeyError:
                continue

        # Load Attribute tags
        try:
            if 'Attribute' in self.xmld:
                for attr in self.xmld['Attribute']:
                    try:
                        if attr['@Name'] in self._ATTRIBUTES_TAG_:
                            value = self[attr['@Name']]
                            if value is not None:
                                attr['Value'] = [value]
                    except (KeyError, IndexError):
                        continue
        except KeyError:
            pass

        # Create new IDs for common nodes
        for nodeType in ['ExternalInterface', 'InternalElement']:
            if nodeType not in self.xmld:
                continue
            for node in self.xmld[nodeType]:
                try:
                    if node['@ID'] in [None, 'None']:
                        node['@ID'] = self.doc.generateID()
                except KeyError:
                    continue

        return self.xmld

    def _encodeAttribute_(self, name, value) -> bool:
        ''' Set the value of an attribute in the XML Dict '''
        if name is None or value is None:
            return False
        try:
            if 'Attribute' not in self.xmld:
                return False
            for attr in self.xmld['Attribute']:
                try:
                    if attr['@Name'] == name:
                        attr['Value'] = [value]
                        return True
                except (KeyError, IndexError):
                    continue
        except KeyError:
            pass
        return False

    def _loadXMLDtemplate(self) -> dict:
        ''' Load default XML Dict template '''
        try:
            template = __file__.replace('base.py', self._TEMPLATE_XMLD_)
            return json.load(open(template, mode='r'))
        except:
            return {}

    def _fromRAW_(self, filePath: str) -> None:
        ''' Import raw XML dict from a JSON file, useful during development'''
        self._decode_(json.load(open(filePath, mode='r')))

    def _toRAW_(self, filePath: str) -> None:
        ''' Export raw XML dict to a JSON file, useful during development'''
        json.dump(self.xmld, open(filePath, mode='w'), indent=2)

    def _registerSelfIDs_(self):
        ''' Register all the IDs '''
        for id, _ in findkey(self.xmld, '@ID'):
            self.doc.registerID(id)
        for id, _ in findkey(self, 'ID'):
            self.doc.registerID(id)

    def findByID(self, ID: str) -> dict:
        ''' Search for an element by its ID (high level API) '''
        return findUniqueKeys(self.doc, 'ID')[ID]


# Extra methods
def findkey(var, key):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v, var
            if isinstance(v, dict):
                for result in findkey(v, key):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in findkey(d, key):
                        yield result


def findUniqueKeys(var, key) -> dict:
    ''' Creates a dict with all the elements in the dict matching the key '''
    result = {}
    for k, v in findkey(var, key):
        if k in result:
            if result[k] == v:
                # continue
                pass
            raise Exception(f"findUniqueKeys found duplicated keys for: {k}")
        result[k] = v
    return result
