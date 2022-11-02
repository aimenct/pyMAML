from ..base import MAMLBaseElement


class MAMLOperationsLib(dict):
    ''' Class to read the Operations SystemUnitClassLib '''

    class _operation_(MAMLBaseElement):
        ''' Temporal class to parse the Operations '''

        # List of XML @Attributes to load
        _ATTRIBUTES_XML_ = [
            'Name',
            'ID',
        ]

        # List of Attribute tags to load its Value
        _ATTRIBUTES_TAG_ = [
            'Stage',
            'Step',
            'Operation',
        ]

    def __init__(
        self,
        # Master AML Document
        Document,
    ):
        # Link Master AML Document
        self.doc = Document

        # Initialize list
        super().__init__()
        super().clear()

        self.version = None

        # Find Operations library
        try:
            for lib in self.doc.xmld['CAEXFile'][0]['SystemUnitClassLib']:
                if '@Name' in lib and lib['@Name'] == 'Operations':
                    library = lib
                    break
            else:
                # print('WARNING: No Operations library found!')
                return
        except:
            return

        # Load version
        try:
            self.version = library['Version'][0]
        except:
            self.version = None

        # Load operations
        for op in library['SystemUnitClass']:
            try:
                operation = self._operation_(
                    Document=self.doc,
                    inputXMLD=op,
                )
                name = operation.pop('Name')
                self[name] = operation
            except:
                continue
