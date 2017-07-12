"""Module for conversion from ArcGIS tables to CSV.
"""
from __future__ import print_function, unicode_literals, absolute_import, division

import csv
import re
import base64
import datetime
from sys import version_info
import arcpy


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
        with arcpy.da.SearchCursor(
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

def _prepare_for_csv(item):
    """Converts a data item to a format that can be written to CSV.
    """
    if isinstance(item, bytearray):
        return base64.b64encode(item).decode(encoding='utf-8')
    elif isinstance(item, datetime.datetime):
        return item.date()
    else:
        return item

def dump_fc(fc_path, out_file, omit_oid=True, skip_re=re.compile("Shape_Length", re.IGNORECASE)):
    """Dumps a feature class to a CSV file.
    Geometry data is written to the CSV file as base64-encoded
    Well-Known Binary (WKB).

    Parameters
    ----------

    fc_path:
        str. Path to a feature class.
    out_file:
        str. Path to CSV file.
    omit_oid
        Boolean, optional. If True (default), the OID field will be omitted from the CSV output.
    skip_re
        re, optional. A regular expression defining fields that will be omitted from the output.
        By default it will ignore the "Shape_Length" field. Any field with a name that matches
        via re.match() will be omitted from the output. Set to None to never omit any fields
        (other than OID fields, which are handled separately by omit_oid).
    """
    if not arcpy.Exists(fc_path):
        # Exit with "{x} does not exist message."
        msg = arcpy.AddIDMessage("ERROR", 110, fc_path)
        raise FileNotFoundError(msg)

    # Create a list of the fields for cursor
    fc_desc = arcpy.Describe(fc_path)
    field_list = []
    has_geometry = False
    for field in fc_desc.fields:
        if (skip_re and skip_re.match(field.name)) or (omit_oid and field.type == "OID"):
            continue
        elif field.type == "Geometry":
            has_geometry = True
        else:
            field_list.append(field.name)
    if has_geometry:
        field_list.append("SHAPE@WKB")

    try:
        file_obj = None
        if out_file:
            file_obj = open(out_file, 'w', newline='')

        if file_obj:
            csv_writer = csv.writer(file_obj)

        csv_writer.writerow(field_list)
        with arcpy.da.SearchCursor(fc_path, field_list) as cursor:
            row = None
            for row in cursor:
                csv_writer.writerow(map(_prepare_for_csv, row))
            del row

    finally:
        if file_obj:
            file_obj.flush()
            file_obj.close()
