from .base import MAMLBaseElement
from .file import MAMLFile
from .sw import MAMLSoftware


class MAMLOperation(MAMLBaseElement):

    _TEMPLATE_ = {
        'Name': None,
        'ID': None,

        'Module': None,
        'Success': None,

        # Operations SystemUnitClassLib
        'Type': None,
        'Stage': None,
        'Step': None,
        'Operation': None,

        'InputFile': [],  # List of IDs

        'OutputFile': [],  # List of IDs

        'SoftwareUsed': [],  # List of IDs

        'UserInfo': {
            'Username': None,
            'UserID': None,
            'Timestamp': None,
        },

        'Comments': None,
    }

    _TEMPLATE_XMLD_ = 'operation.json'

    _ATTRIBUTES_TAG_ = [
        'Module',
        'Success',
        'Stage',
        'Step',
        'Operation',
        'Comments',
    ]

    _OPS_LIB_KEY_ = '@RefBaseSystemUnitPath'
    _OPS_LIB_PREFIX_ = 'Operations/'

    def newInputFile(self) -> MAMLFile:
        return self._newIOFile_('InputFile')

    def newOutputFile(self) -> MAMLFile:
        return self._newIOFile_('OutputFile')

    def _newIOFile_(self, direction: str) -> MAMLFile:
        f = MAMLFile(Document=self.doc, DigitalThread=self.dt)
        self[direction].append(f['ID'])
        self.dt['Files'].append(f)
        return f

    def newSoftwareUsed(self) -> MAMLSoftware:
        sw = MAMLSoftware(Document=self.doc, DigitalThread=self.dt)
        self['SoftwareUsed'].append(sw['ID'])
        self.dt['Softwares'].append(sw)
        return sw

    def getOperationType(self) -> str:
        '''
        Returns the Operation type according to the SystemUnitClassLib

        Returns None if invalid or not defined
        '''
        try:
            if self._OPS_LIB_KEY_ not in self.xmld:
                return None
            ot = self.xmld[self._OPS_LIB_KEY_]
            if self._OPS_LIB_PREFIX_ not in ot:
                return None
            if ot[:len(self._OPS_LIB_PREFIX_)] == self._OPS_LIB_PREFIX_:
                return ot[len(self._OPS_LIB_PREFIX_):]
        except:
            pass
        return None

    def getOperationTypesAvailable(self) -> dict:
        ''' Returns the Operations SystemUnitClassLib '''
        return self.doc.OperationsLib

    def setOperationType(self, name, overwriteAttributes=True) -> bool:
        '''
        Attempt to set the Operation type from the SystemUnitClassLib

        Returns True if succeeded

        If overwriteAttributes, these attributes are loaded from the lib:
            Stage, Step, Operation
        '''
        if name is None or name not in self.getOperationTypesAvailable():
            return False

        try:
            self.xmld[self._OPS_LIB_KEY_] = self._OPS_LIB_PREFIX_ + name
            self['Type'] = name
        except:
            return False

        if overwriteAttributes:
            attrs = self.getOperationTypesAvailable()[name]
            try:
                for attr in ['Stage', 'Step', 'Operation']:
                    self._encodeAttribute_(attr, attrs[attr])
                    self[attr] = attrs[attr]
            except:
                return False

        return True

    def _decode_(self, xmld) -> None:
        ''' Load the simplified representation from an XML dictionary '''
        super()._decode_(xmld)

        # Load Operation Type according to the SystemUnitClassLib
        self['Type'] = self.getOperationType()

        # Load User Info
        for ie in self.xmld['InternalElement']:
            try:
                if ie['@Name'] != 'UserInfo':
                    continue
                for attr in ie['Attribute']:
                    if 'Value' not in attr:
                        continue

                    # Fix wrong keys
                    key = attr['@Name']
                    if key == 'User Name':
                        key = 'Username'
                    elif key == 'Timestmp':
                        key = 'Timestamp'

                    self['UserInfo'][key] = attr['Value'][0]
                break
            except (KeyError, IndexError):
                continue

    def _encode_(self) -> dict:
        ''' Export the simplified representation to an XML dictionary '''
        super()._encode_()

        # Load Operation Type according to the SystemUnitClassLib
        if 'Type' in self:
            self.setOperationType(self['Type'], overwriteAttributes=False)

        # Load User Info
        for ie in self.xmld['InternalElement']:
            try:
                if ie['@Name'] != 'UserInfo':
                    continue
                if ie['@ID'] is None:
                    ie['@ID'] = self.doc.generateID()
                for attr in ie['Attribute']:
                    attr['Value'] = [self['UserInfo'][attr['@Name']]]
                break
            except (KeyError, IndexError):
                continue

        return self.xmld
