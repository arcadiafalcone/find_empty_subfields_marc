from pymarc import *
import re
from datetime import datetime

## Script by Arcadia Falcone, arcadia.falcone at gmail, updated 12/19/2014
## Checks for errors causing Solr ingest to fail: empty subfields and empty 
## delimiters. Outputs detailed error log.


def openFilesIO():
    """Select input file, and create updated MARC file and error log text file
    for output, with file names based on the input file selected."""
    import os
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()
    fileselect = tkFileDialog.askopenfilename()
    filepath = os.path.dirname(fileselect)
    filename = os.path.basename(fileselect)
    basename = os.path.splitext(filename)[0]
    infile = os.path.abspath(fileselect)
    outfile_base = filepath + '/' + basename
    errorfile = outfile_base + '_error.txt'
    logfile = outfile_base + '_log.txt'
    return infile, errorfile, logfile


### Variables ###

bib_formats = {'a': 'print', 'c': 'music', 'd': 'music', 'e': 'maps', 
'f': 'maps', 'g': 'visual', 'i': 'audio', 'j': 'audio', 'k': 'visual',
'm': 'digital', 'o': 'kit', 'p': 'archives', 'r': 'object', 't': 'print'}

# Regex
space_re = re.compile(r'\s*$')
valid_code_re = re.compile(r'[a-z0-9]')
alpha_num_re = re.compile(r'.*?[A-Za-z0-9]+')
repeated_sub_code_re = re.compile(r'\$([a-z0-9])\s*\$\1')
terminal_empty_sub_re = re.compile(r'\$[a-z0-9]$')


### Process ###

# Record start time
start_time = datetime.now()

# Select MARC file for processing and create output files
print 'Select the MARC file for error validation.'
marc_file, error_file, log_file = openFilesIO()
outfile = open(error_file, 'w')
log = open(log_file, 'w')

print 'Processing %s...' % marc_file

# Write headers to output file
headers = ['bib_id', 'marc_field', 'field_value', 'error_type', 'format', 
'language', 'batch', 'errors_per_bib']
outfile.write('\t'.join(headers) + '\n')

process_count = 0
error_count = 0
record_count = 0

reader = MARCReader(file(marc_file))
for record in reader:
    process_count += 1
# Reset values for each record
    output_flag = False
    record_output = []
# Set current record ID and get all fields
    record_id = record['001'].value()
    all_fields = record.get_fields()
    for field in all_fields:
# Skip control fields (don't have subfields)
        if field.is_control_field():
            continue
        if field.subfields:
# Reset values for each field
            i = 0
            old_errors = []
# Iterate through subfields and analyze for errors
            for subfield in field.subfields:
                old_error_count = error_count
                i += 1
                if i % 2 != 0:
                    if re.match(space_re, subfield):
                        error = 'empty delimiter'
                        error_count += 1
                    elif not re.match(valid_code_re, subfield):
                        error = 'invalid subfield code'
                        error_count += 1
                else:
                    if re.match(space_re, subfield):
                        error = 'empty subfield'
                        error_count += 1
# Add new error to field errors if not duplicate
                if error_count > old_error_count and error not in old_errors:
                    old_errors.append(error)
# Get additional metadata from the record
                    bib_format = bib_formats[record.leader[6]]
                    language = record['008'].value()[35:38]
# Identify candidates for batch processing
                    if re.search(repeated_sub_code_re, str(field)):
                        batch = 'batch - repeated subfield code'
                    elif re.search(terminal_empty_sub_re, str(field)):
                        batch = 'batch - terminal empty subfield'
                    else:
                        batch = ''
# Set output values
                    record_output.append([record_id, field.tag, str(field), 
                                          error, bib_format, language, batch])
                    output_flag = True
        else:
            print '%s: no subfields in %s' % (record_id, str(field))
    if output_flag == True:
        record_count += 1
# Note whether same record has one error, or multiple errors
        if len(record_output) > 1:
            error_num = 'multiple'
        else:
            error_num = 'single'
# Write record error data to output file
        for output in record_output:
            output.append(error_num)
            outfile.write('\t'.join(output) + '\n')

# Write summary of results to log file
stop_time = datetime.now()
log.write('Process started: %s' % start_time + '\n')
log.write('Process completed: %s' % stop_time + '\n\n')
log.write('%d records processed.' % process_count + '\n')
log.write('%d errors identified.' % error_count + '\n')
log.write('%d records with errors.' % record_count + '\n')

# Write summary of results to console

print 'Records processed: %d' % process_count
print 'Errors identified: %d' % error_count
print 'Records with errors: %d' % record_count

# Close files
outfile.close()
log.close()
