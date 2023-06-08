'''
Helper functions to read and write items from CSV.
'''

# Import dependencies.
import csv

# Define functions.
def read_csv( file_name ):
    '''
    Helper function to read items from CSV
    '''
    tasks = []
    with open( file_name, 'r', encoding='utf8') as file:
        reader = csv.reader(file)
        for row in reader:
            tasks.append(row)
    return tasks

def write_csv( file_name, content ):
    '''
    Helper function to write tasks to CSV
    '''
    with open( file_name, 'w', newline='', encoding='utf8') as file:

        writer = csv.writer( file )
        writer.writerows( content )

        # writer = csv.writer(file, delimiter=",")
        # for row in content:
        #    columns = [c.strip() for c in row.strip(', ').split(',')]
        #    writer.writerow(columns)
