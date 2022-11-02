from copy import deepcopy

from .base import MAMLBaseElement


class MAMLFile(MAMLBaseElement):

    _TEMPLATE_ = {
        'Name': None,
        'ID': None,

        # Subfiles
        'Files': [
            {
                'File': {
                    'Name': None,
                    'MIMEType': None,
                    'UUID': None,
                },
                'Connection': {
                    'IP': None,
                    'Port': None,
                    'URL': None,
                },
                'Security': {
                    'Checksum': None,
                },
            }
        ],
    }

    _TEMPLATE_XMLD_ = 'file.json'

    def _decode_(self, xmld) -> None:
        ''' Load the simplified representation from an XML dictionary '''
        super()._decode_(xmld)

        # Load subfiles
        self['Files'] = []
        for subfile in self.xmld['InternalElement']:
            try:
                file = deepcopy(MAMLFile._TEMPLATE_['Files'][0])
                for attr in subfile['ExternalInterface'][0]['Attribute']:
                    for subattr in attr['Attribute']:
                        try:
                            if 'Value' not in subattr:
                                continue
                            file[attr['@Name']][subattr['@Name']] = \
                                subattr['Value'][0]
                        except (KeyError, IndexError):
                            continue
                self['Files'].append(file)

            except KeyError:
                print(f'''Failed to import MAMLFile subfile ({self['ID']})''')

    def _encode_(self) -> dict:
        ''' Export the simplified representation to an XML dictionary '''
        super()._encode_()

        # Load subfiles
        template = deepcopy(self.xmld['InternalElement'][0])
        self.xmld['InternalElement'] = []
        for subfile in self['Files']:
            try:
                file = deepcopy(template)
                for attr in file['ExternalInterface'][0]['Attribute']:
                    for subattr in attr['Attribute']:
                        try:
                            value = subfile[attr['@Name']][subattr['@Name']]
                            if value is not None:
                                subattr['Value'] = [value]
                        except KeyError:
                            continue
                self.xmld['InternalElement'].append(file)
            except (KeyError, IndexError):
                print(f'''Failed to export MAMLFile subfile ({self['ID']})''')

        # Generate nested External Interfaces IDs
        for ie in self.xmld['InternalElement']:
            for ei in ie['ExternalInterface']:
                ei['@ID'] = self.doc.generateID()

        return self.xmld

    def newSubFile(self) -> dict:
        ''' Add a new empty SubFile and append it to the current File '''
        template = deepcopy(self._TEMPLATE_['Files'][0])
        # Check if last SubFile is empty
        if self['Files'][-1] != template:
            self['Files'].append(template)
        return self['Files'][-1]
