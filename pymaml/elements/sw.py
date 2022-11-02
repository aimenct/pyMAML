from .file import MAMLFile
from .base import MAMLBaseElement


class MAMLSoftware(MAMLBaseElement):

    _TEMPLATE_ = {
        'Name': None,
        'ID': None,

        'Software Name': None,
        'Version': None,
        'Description': None,
        'Input type(s)': None,
        'Output type(s)': None,

        'ConfigFile': [],  # List of IDs
    }

    _TEMPLATE_XMLD_ = 'sw.json'

    _ATTRIBUTES_TAG_ = [
        'Software Name',
        'Version',
        'Description',
        'Input type(s)',
        'Output type(s)',
    ]

    def newConfigFile(self) -> MAMLFile:
        f = MAMLFile(Document=self.doc, DigitalThread=self.dt)
        self['ConfigFile'].append(f['ID'])
        self.dt['Files'].append(f)
        return f
