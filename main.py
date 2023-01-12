import os

def process_line(line, prefix, table, function):
    """Breaks a line up by spaces and checks if the desired prefix is in the line before invoking the function on the line split"""
    chunks = line.strip().split(' ')

    if prefix in chunks[1] and len(chunks) >= 3:
        function(chunks, table)

def process_class(chunks, table):
    """Correctly adds a class to the table"""
    table[chunks[1].removeprefix('net/minecraft/')] = chunks[2].replace('/', '.')

def process_other(chunks, table):
    """Adds an entry of the second and third item of the string split to the table"""
    table[chunks[1]] = chunks[2]

def process_file(path, table):
    with open(path, 'r+') as file:
        lines = file.readlines()
        counter = 1

        for line in lines:
            line = line.strip()

            if line.startswith('CLASS'):
                process_line(line, 'class', table, process_class)
            if line.startswith('FIELD'):
                process_line(line, 'field', table, process_other)
            if line.startswith('METHOD'):
                process_line(line, 'method', table, process_other)

            counter += 1

# this will remap the file
def remap_file(path, table):
    fin = open(path, 'r+').read()

    with open(path, 'w+') as fout:
        for key in table:
            for trailer in ' ', ';', ')', '[', ',', '.', '(', ';', '>', '<':
                if key + trailer in fin:
                    print(f'Replaced {key} with {table[key]}')
                    fin = fin.replace(key + trailer, table[key] + trailer)

        fout.truncate(0)
        fout.write(fin)

# Either process the file or recurse on the directory
def zipTree(dir, func, table):
    for file in os.scandir(dir):
        if not file.is_file():
            zipTree(file, func, table)
        else:
            print(f'processing {file}')
            func(file.path, table)
            print(f'processed file {file}')

if __name__ == '__main__':
    path_in = input('Input the absolute path for the directory of the mappings: ')
    path_out = input('Input the absolute path for the directory you want to be remapped: ')

    reference_table = {}

    # Find all the mappings
    for file in os.scandir(path_in):
        zipTree(file, process_file, reference_table)

    # Replace all the proxy names with their correct mapping
    for file in os.scandir(path_out):
        zipTree(file, remap_file, reference_table)
