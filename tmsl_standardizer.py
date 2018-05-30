#!/usr/bin/env python

"""tmsl_standardizer.py: Standardizes column display formats for a few datatypes to save tiresome drudgery in visual studio"""

__author__      = "Gage Renzi"
__copyright__   = "Copyright 2009, Planet Earth"
__license__ = "GPLv3"
__version__ = "0.0.2"

import json
import click

g={}
# see this for tmsl reference for model definition
# https://docs.microsoft.com/en-us/sql/analysis-services/tabular-models-scripting-language-objects/tables-object-tmsl?view=sql-analysis-services-2017

def standardize_date_format(col):    
    if col['dataType']=='dateTime':
        col['formatString']= 'Short Date'
        col['annotations']=[
              {
                "name": "Format",
                "value": "<Format Format=\"DateTimeShortDatePattern\" />"
              }
            ]

# From: https://docs.microsoft.com/en-us/sql/analysis-services/multidimensional-models/mdx/mdx-cell-properties-format-string-contents?view=sql-analysis-services-2017
# Numeric Values
# A user-defined format expression for numbers can have anywhere from one to four sections separated by semicolons. If the format argument contains one of the named numeric formats, only one section is allowed.

# Usage	Result
# One section	The format expression applies to all values.
# Two sections	The first section applies to positive values and zeros, the second to negative values.
# Three sections	The first section applies to positive values, the second to negative values, and the third to zeros.
# Four sections	The first section applies to positive values, the second to negative values, the third to zeros, and the fourth to null values.
def standardize_whole_number_commas(col):
    if col['dataType']=='int64':
        col['formatString']= '#,0;(-#,0)'

def standardize_percentiles(col):
    if col['dataType']=='double' and '%' in col['name']:
        col['formatString']= '0.0%;(-0.0%);0.0%'    
 

################################################################################
## main
@click.command()
@click.argument('infile', type=click.File('r'))
@click.argument('outfile',type=click.File('w'))
def main(infile, outfile):
    #read in the model - json doesn't like doing it directly. meh.
    contents = infile.read()
    model = json.loads(contents)

    #iterate through tables and pass the columns off for each function to take a crack at
    for tab in model['model']['tables']:
        for col in tab['columns']:
            standardize_date_format(col)
            standardize_whole_number_commas(col)
            standardize_percentiles(col)
    
    #save output pretty printed, 2 spaces is what visual studio does
    outfile.write(json.dumps(model, indent=2, sort_keys=False))

if __name__ == '__main__':
    main()
    