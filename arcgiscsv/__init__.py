"""Module for conversion from ArcGIS tables to CSV.
"""

import csv
import arcpy
import arcpy.da as da


def writeToCsv(table_view, output_file, field_names='*', where_clause=None, sql_clause=None):
    """Converts a table or table view into a CSV file.
    Returns the number of rows that were read.
    """
    row_count = 0
    with open(output_file, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file, 'excel')
        with da.SearchCursor(table_view, field_names, where_clause=where_clause, sql_clause=sql_clause) as cursor:
            # Write the headers
            csv_writer.writerow(cursor.fields)
            for row in cursor:
                csv_writer.writerow(row)
                row_count += 1
    return row_count
