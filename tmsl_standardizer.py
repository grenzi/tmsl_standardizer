#!/usr/bin/env python

"""tmsl_standardizer.py: Standardizes column display formats for a few datatypes to save tiresome drudgery in visual studio"""

__author__      = "Gage Renzi"
__copyright__   = "Copyright 2009, Planet Earth"
__license__ = "GPLv3"
__version__ = "0.0.1"

import json
import click
import logging

logger = logging.getLogger('tmsl_standardizer')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()]) #or, or add logging.FileHandler("example1.log")

# place column or measure names in respective arrays to exclude them
exclude_columns = []
exclude_measures = []

g={}
# see this for tmsl reference for model definition
# https://docs.microsoft.com/en-us/sql/analysis-services/tabular-models-scripting-language-objects/tables-object-tmsl?view=sql-analysis-services-2017

# See this for formatString info:
# https://docs.microsoft.com/en-us/sql/analysis-services/multidimensional-models/mdx/mdx-cell-properties-format-string-contents?view=sql-analysis-services-2017

def standardize_column_date_format(col):    
    if col['dataType']=='dateTime':
        logger.info('Date Standardizing Column {0}'.format(col['name']))
        col['formatString']= 'Short Date'
        col['annotations']=[
              {
                "name": "Format",
                "value": "<Format Format=\"DateTimeShortDatePattern\" />"
              }
            ]

def standardize_measure_date_format(m):    
    if 'date' in m['name'].lower():
        logger.info('Date Standardizing Measure {0}'.format(col['name']))
        m['formatString']= 'Short Date'
        m['annotations']=[
              {
                "name": "Format",
                "value": "<Format Format=\"DateTimeShortDatePattern\" />"
              }
            ]

def standardize_column_whole_number_commas(col):
    if col['dataType']=='int64':
        logger.info('Whole Number Standardizing Column {0}'.format(col['name'])
        col['formatString']= '#,0;(-#,0)'

def standardize_column_percentiles(col):
    if col['dataType']=='double' and '%' in col['name']:
        logger.info('Percentile Standardizing Column {0}'.format(col['name']))
        col['formatString']= '0.0%;(-0.0%);0.0%'    

def standardize_measure_percentiles(m):
    if '%' in m['name']:
        logger.info('Percentile Standardizing Measure {0}'.format(col['name']))
        m['formatString']= '0.0%;(-0.0%);0.0%'    
 

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
        for [col in tab['columns'] if col not in exclude_columns]:
            standardize_column_date_format(col)
            standardize_column_whole_number_commas(col)
            standardize_column_percentiles(col)
        if 'measures' in tab.keys():
            for [measure in tab['measures'] if measure not in exclude_measures]:
                standardize_measure_date_format(measure)
                standardize_measure_percentiles(measure)
    
    #save output pretty printed, 2 spaces is what visual studio does
    outfile.write(json.dumps(model, indent=2))

if __name__ == '__main__':
    main()
    