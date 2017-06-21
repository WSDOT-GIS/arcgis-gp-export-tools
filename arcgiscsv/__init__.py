"""Module for conversion from ArcGIS tables to CSV.
"""
from __future__ import print_function, unicode_literals, absolute_import, division

import csv
import re
from sys import version_info
import arcpy
import arcpy.da as da


def get_fields_from_table(table, omit_fields_re=None):
    """Gets the fields from a table
    table - The name or path of the table.
    omit_fields_re - If not set to None, any field with a name matching this
                     expression will be omitted from the output list.
    returns - An array of field names.
    """
    if isinstance(omit_fields_re, str):
        omit_fields_re = re.compile(omit_fields_re, re.IGNORECASE)
    desc = arcpy.Describe(table)
    fields = desc.fieldInfo
    output = []
    for field in fields:
        if omit_fields_re is None or not omit_fields_re.matches(field.name):
            output.append(field.name)
    return output

def _open_csv_file(filename):
    """Opens a file for writing to CSV, choosing the correct method for the
    current version of Python
    """
    if version_info.major < 3:
        out_file = open(filename, 'wb')
    else:
        out_file = open(filename, 'w', newline='')
    return out_file

def write_to_csv(table_view, output_file, field_names='*', where_clause=None, sql_clause=None):
    """Converts a table or table view into a CSV file.
    Returns the number of rows that were read.
    """
    row_count = 0
    with _open_csv_file(output_file) as csv_file:
        csv_writer = csv.writer(csv_file, 'excel')
        with da.SearchCursor(
            table_view,
            field_names,
            where_clause=where_clause,
            sql_clause=sql_clause
        ) as cursor:
            # Write the headers
            csv_writer.writerow(cursor.fields)
            for row in cursor:
                csv_writer.writerow(row)
                row_count += 1
    return row_count
