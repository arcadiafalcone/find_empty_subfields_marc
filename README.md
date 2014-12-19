Validation Tool for MARC Records: Identifying Empty Subfields and Delimiters

Functionality
-------------
Identifies the following errors:
* subfield code without an alphanumeric value, such as $a in $a$bValue or $a:$bValue
* subfield code that is not a lower case letter or number
* subfield delimiter symbol without a code
Notes error types amenable to batch updates:
* a repeated subfield code, such as $a$aValue
* a terminal empty subfield, such as $b in $aValue$b
Supplements error logging with metadata from the record that may be used for filtering or routing for manual review:
* record identifier
* field tag where error was found
* the content of the field
* the type of error
* the format of the resource (from Leader06/07)
* the language of the resource (from 008)
* batch processing classification

Input
-----
* A file in MARC format, selected through a GUI dialog box

Output
------
* inputfilename_error.txt: Error log with supplementary metadata
* inputfilename_log.txt: Processing statistics

Dependencies
------------
pymarc

Credit
------
Script by Arcadia Falcone, arcadiafalcone at gmail  
Updated 2014-12-19
