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

    # Initialize an array to return to the caller.
    rows = []

    # Get the file.
    with open( file_name, 'r', encoding='utf8') as file:

        # Pass the file contents to the reader function.
        reader = csv.reader( file )

        # Iterate over the rows in the file.
        for row in reader:

            # Append each row with modified items to the array.
            rows.append( row )

    # Return the array.
    return rows

def write_csv( file_name, content ):
    '''
    Helper function to write tasks to CSV
    '''

    # Write to CSV file.
    with open( file_name, 'w', encoding='utf8') as file:

        writer = csv.writer( file )
        writer.writerows( content )

        # writer = csv.writer(file, delimiter=",")
        # for row in content:
        #    columns = [c.strip() for c in row.strip(', ').split(',')]
        #    writer.writerow(columns)
