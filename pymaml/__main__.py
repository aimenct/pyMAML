from sys import path, argv
from os.path import dirname, realpath

# correct the path to the root of the library
root_path = dirname(dirname(realpath(__file__)))
path.insert(0, root_path)


if __name__ == "__main__":
    def printHelp():
        print("Usage: python -m pymaml input.(aml|json) [output.(aml|json)]")
        quit()

    if len(argv) < 2:
        printHelp()

    conversions = {
        # Master AML to simplified dictionary
        'aml': 'json',

        # Simpified dictionary to Master AML
        'json': 'aml',
    }

    inputF = argv[1]
    inputExt = inputF.split('.')[-1]
    if inputExt not in conversions:
        printHelp()

    try:
        outputF = argv[2]
        if outputF.split('.')[-1] not in conversions:
            printHelp()
    except IndexError:
        outputExt = conversions[inputExt]
        outputF = inputF.replace(f'.{inputExt}', f'.{outputExt}')

    print(f"Converting {inputF} to {outputF}")
    from pymaml.master import MasterAML
    MasterAML(inputF).export(outputF)
