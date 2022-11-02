import json
from copy import deepcopy
from .base import MAMLBaseElement, findkey
from .dt import MAMLDigitalThread
from .libs.operations import MAMLOperationsLib


class MAMLDocument(MAMLBaseElement):
    '''
    Backend to handle Master AML documents (low level API)
    '''

    _TEMPLATE_ = {
        'FileName': None,
        'Digital Threads': []
    }

    _TEMPLATE_XMLD_ = 'doc.json'

    _ATTRIBUTES_XML_ = []
    _ATTRIBUTES_TAG_ = []

    def __init__(self, *args, **kargs):
        ''' Overload init to load libraries '''
        super().__init__(*args, **kargs)

        # Load the Operations library
        self.OperationsLib = MAMLOperationsLib(Document=self)

    def _decode_(self, xmld) -> None:
        ''' Load the simplified representation from an XML dictionary '''
        # Store XMLD input
        self.xmld = xmld

        # Reset Simplified Dictionary
        self.clear()

        self._fixXMLDNullIDs_()

        # Load FileName
        try:
            self['FileName'] = self.xmld['CAEXFile'][0]['@FileName']
        except (KeyError, IndexError):
            pass

        # Save direct accesses first
        self.ih = self.xmld['CAEXFile'][0]['InstanceHierarchy'][0]

        # Load Digital Threads
        if 'InternalElement' in self.ih:
            for ie in self.ih['InternalElement']:
                if '@RefBaseSystemUnitPath' in ie and \
                   ie['@RefBaseSystemUnitPath'] == "Structures/DigitalThread":
                    self['Digital Threads'].append(
                        MAMLDigitalThread(Document=self, inputXMLD=ie))

        self._registerSelfIDs_()

    def _encode_(self) -> dict:
        ''' Export the simplified representation to an XML dictionary '''
        super()._encode_()

        # Load FileName
        try:
            self.xmld['CAEXFile'][0]['@FileName'] = self['FileName']
        except (KeyError, IndexError):
            pass

        # Save direct accesses first
        ih = self.xmld['CAEXFile'][0]['InstanceHierarchy'][0]

        for dt in self['Digital Threads']:
            ih['InternalElement'].append(
                MAMLDigitalThread(
                    Document=self, inputSimpleDict=dt)._encode_())

        self._fixXMLDNullIDs_()

        return self.xmld

    def _fixXMLDNullIDs_(self) -> None:
        ''' Make sure IDs in the XMLD are not null '''
        for id, parent in findkey(self.xmld, '@ID'):
            if id is None or str(id).lower() == 'none':
                parent['@ID'] = self.doc.generateID()

    def _exportTemplate_(self, filePath) -> None:
        ''' Save the current AML without any Digital Thread '''
        t = deepcopy(self.xmld)
        t['CAEXFile'][0]['InstanceHierarchy'][0]['InternalElement'].clear()
        # Sort JSON to ease comparison
        json.dump(t, open(filePath, mode='w'), indent=2, sort_keys=True)
