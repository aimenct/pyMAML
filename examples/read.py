"""
Launch from the main project folder:
    ~/pyMAML$  python examples/read.py
"""

# correct the path to the root of the library
from sys import path
from os.path import dirname, realpath
root_path = dirname(dirname(realpath(__file__)))
path.insert(0, root_path)

from pymaml.master import MasterAML

# Open Master AML file
aml = MasterAML('testfiles/idesa/master.aml')

# Explore Digital Threads
for dt in aml['Digital Threads']:
    print(f'''Digital Thread name: {dt['Name']}''')
    print(f'''  Modules: {dt['Modules']}''')

    # Find an Operation with a linked File
    for op in dt['Operations']:
        if len(op['InputFile']) > 0:
            # Get first linked InputFile
            inputFile = dt.findByID(op['InputFile'][0])
            print(f'''  Operation: {op['Name']} <---> '''
                  f'''InputFile: {inputFile['Name']}''')
            break

# Export AML as a clean dictionary
amlDict = aml.toDict()

# Export AML to a JSON file
aml.export(aml.filePath.replace('.aml', '.json'))
