from .base import MAMLBaseElement, findUniqueKeys
from .file import MAMLFile
from .sw import MAMLSoftware
from .operation import MAMLOperation


class MAMLDigitalThread(MAMLBaseElement):

    _TEMPLATE_ = {
        'Name': None,
        'ID': None,

        'Modules': [
            'Requirements',
        ],

        'Operations': [],
        'Files': [],
        'Softwares': [],
    }

    _TEMPLATE_XMLD_ = 'dt.json'

    def newFile(self) -> MAMLFile:
        f = MAMLFile(Document=self.doc, DigitalThread=self)
        self['Files'].append(f)
        return f

    def newOperation(self) -> MAMLOperation:
        op = MAMLOperation(Document=self.doc, DigitalThread=self)
        self['Operations'].append(op)
        return op

    def newSoftware(self) -> MAMLSoftware:
        sw = MAMLSoftware(Document=self.doc, DigitalThread=self)
        self['Softwares'].append(sw)
        return sw

    def _decode_(self, xmld) -> None:
        ''' Load the simplified representation from an XML dictionary '''
        super()._decode_(xmld)

        # Load Modules
        if 'Attribute' in self.xmld:
            for attr in self.xmld['Attribute']:
                try:
                    if attr['@Name'] != 'Modules':
                        continue
                    for subattr in attr['Attribute']:
                        module = subattr['Value'][0]
                        if module not in self['Modules']:
                            self['Modules'].append(module)
                except (KeyError, IndexError):
                    continue

        # Load Internal Elements: Operations, Files and Softwares
        for file in self._xmldFiles_:
            self['Files'].append(MAMLFile(
                Document=self.doc, DigitalThread=self, inputXMLD=file))
        for sw in self._xmldSoftwares_:
            self['Softwares'].append(MAMLSoftware(
                Document=self.doc, DigitalThread=self, inputXMLD=sw))
        for op in self._xmldOperations_:
            self['Operations'].append(MAMLOperation(
                Document=self.doc, DigitalThread=self, inputXMLD=op))

    @property
    def _xmldFiles_(self) -> list:
        ''' Direct accesss to the XML dict Files list '''
        return self._xmld_ie_wrapper_('Files')

    @property
    def _xmldOperations_(self) -> list:
        ''' Direct accesss to the XML dict Operations list '''
        return self._xmld_ie_wrapper_('Operations')

    @property
    def _xmldSoftwares_(self) -> list:
        ''' Direct accesss to the XML dict Softwares list '''
        return self._xmld_ie_wrapper_('Softwares')

    def _xmld_ie_wrapper_(self, name) -> list:
        for ie in self.xmld['InternalElement']:
            if 'InternalElement' not in ie:
                continue
            if ie['@Name'] == name:
                return ie['InternalElement']
        return []

    def _encode_(self) -> dict:
        ''' Export the simplified representation to an XML dictionary '''
        super()._encode_()

        # Save direct accesses first
        for ie in self.xmld['InternalElement']:
            if ie['@Name'] == 'Files':
                files = ie['InternalElement']
            elif ie['@Name'] == 'Softwares':
                sws = ie['InternalElement']
            elif ie['@Name'] == 'Operations':
                ops = ie['InternalElement']
        for attr in self.xmld['Attribute']:
            if attr['@Name'] == 'Modules':
                mods = attr['Attribute']
                break

        # Load modules
        for module in self['Modules']:
            # Check if module is already present
            for mod in mods:
                if module == mod['Value'][0]:
                    break
            else:
                mod = {}
                mod.update(mods[0])
                mod['Value'] = [module]
                mod['@Name'] = f'Module{len(mods)+1}'
                mods.append(mod)

        # Load Internal Elements: Operations, Files and Softwares
        for f in self['Files']:
            files.append(MAMLFile(
                Document=self.doc,
                DigitalThread=self,
                inputSimpleDict=f)._encode_())
        for sw in self['Softwares']:
            sws.append(MAMLSoftware(
                Document=self.doc,
                DigitalThread=self,
                inputSimpleDict=sw)._encode_())
        for op in self['Operations']:
            ops.append(MAMLOperation(
                Document=self.doc,
                DigitalThread=self,
                inputSimpleDict=op)._encode_())

        # Create links
        lineage = findUniqueKeys(self.xmld, '@ID')
        for op in self['Operations']:
            sourceID = op['ID']
            source = lineage[sourceID]
            for interface in ['InputFile', 'OutputFile', 'SoftwareUsed']:
                for targetID in op[interface]:
                    target = lineage[targetID]
                    self._newLink_(source, target, interface)
        for sw in self['Softwares']:
            sourceID = sw['ID']
            source = lineage[sourceID]
            for targetID in sw['ConfigFile']:
                target = lineage[targetID]
                self._newLink_(source, target, 'ConfigFile')

        return self.xmld

    def _lineageEI_(self) -> dict:
        ''' Returns a dict of External Interface ID and its parent ID '''
        eis = {}
        supportedInterfaces = [
            'DigitalThreadInterfaces/FileExchangeConnector',
            'DigitalThreadInterfaces/SoftwareInterfaceConnector',
        ]
        for x in (
            self._xmldFiles_ + self._xmldSoftwares_ + self._xmldOperations_
        ):
            try:
                for ei in x['ExternalInterface']:
                    try:
                        if ei['@RefBaseClassPath'] in supportedInterfaces:
                            eis[ei['@ID']] = x['@ID']
                    except KeyError:
                        continue
            except KeyError:
                continue
        return eis

    def _solveEI_(self, sourceEIID) -> str:
        ''' Find the opposite element ID linked with an External Interface '''

        if 'InternalLink' not in self.xmld:
            return None

        lineage = self._lineageEI_()

        for link in self.xmld['InternalLink']:
            A = link['@RefPartnerSideA']
            B = link['@RefPartnerSideB']
            if sourceEIID == A:
                targetEIID = B
            elif sourceEIID == B:
                targetEIID = A
            else:
                continue

            if targetEIID in lineage:
                return lineage[targetEIID]

        return None

    def _newLink_(
        self,
        source: dict,
        target: dict,
        interface: str,
    ) -> None:
        ''' Link source and target by adding External Interfaces '''

        def getTargetName(sourceName: str) -> str:
            return {
                'InputFile': 'InputOf',
                'OutputFile': 'OutputOf',
                'SoftwareUsed': 'Operation',
                'ConfigFile': 'ConfigOf',
            }[sourceName]

        def getRefBaseClassPath(name):
            if name in [
                # From Operation
                'InputFile', 'OutputFile',
                # From File
                'InputOf', 'OutputOf',
                # From Software
                'ConfigFile',
            ]:
                return 'DigitalThreadInterfaces/FileExchangeConnector'
            elif name in [
                # From Operation
                'SoftwareUsed',
                # From Software
                'Operation'
            ]:
                return 'DigitalThreadInterfaces/SoftwareInterfaceConnector'
            else:
                raise NotImplementedError(
                    f'Unknown External Interface name: {name}')

        # Create new interfaces at both ends
        sourceEI = {
            "@RefBaseClassPath": getRefBaseClassPath(interface),
            "@ID": self.doc.generateID(),
            "@Name": interface,
        }
        source['ExternalInterface'].append(sourceEI)
        targetEI = {
            "@RefBaseClassPath": getRefBaseClassPath(interface),
            "@ID": self.doc.generateID(),
            "@Name": getTargetName(interface),
        }
        target['ExternalInterface'].append(targetEI)

        # Create link
        n = len(self.xmld['InternalLink'])
        self.xmld['InternalLink'].append({
            '@RefPartnerSideA': sourceEI['@ID'],
            '@RefPartnerSideB': targetEI['@ID'],
            '@Name': f'InternalLink{n + 1}'
        })
