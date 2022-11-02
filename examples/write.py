"""
Launch from the main project folder:
    ~/pyMAML$  python examples/write.py
"""

# correct the path to the root of the library
from sys import path
from os.path import dirname, realpath
root_path = dirname(dirname(realpath(__file__)))
path.insert(0, root_path)

from pymaml.master import MasterAML

# Create a new Master AML
aml = MasterAML(replicableIDs=True)

# Create a Digital Thread
dt = aml.newDigitalThread()
dt['Name'] = 'Analog thread'
dt['Modules'].append('Nailing')

# Add Operation
op = dt.newOperation()
op['Name'] = 'Assembly'
op['Module'] = 'Nailing'
op['Success'] = True
op['Comments'] = '''
Multiple
line
comment
'''

# Add Files to an Operation
file1 = op.newOutputFile()
file1['Name'] = 'scope.hdf5'
file2 = op.newOutputFile()
file2['Name'] = 'perfilometer.hdf5'

# Add more details to a File
subfile = file2.newSubFile()
subfile['Connection']['IP'] = '0.0.0.0'

# Add Softwares to an Operation
sw = op.newSoftwareUsed()
sw['Name'] = 'Capturer'

# Add a ConfigFile to a Software
config = sw.newConfigFile()
config['Name'] = 'settings.yml'

# Explore Operations library
print(f'''Operations library (version: {aml.OperationsLib.version}):''')
for name, value in aml.OperationsLib.items():
    print(f'''  {name}''')
    for key, val in value.items():
        print(f'''    {key}: {val}''')

# Set operation type from one in the library
op.setOperationType('Build')

# Export to a file
aml.export('new.aml')
aml.export('new.json')
