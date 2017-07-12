"""
Prints message IDs
"""

from __future__ import unicode_literals, print_function
import csv
from sys import stdout
import arcpy


def main():
    """Creates a CSV file of messages for use with AddIDMessage.
    """
    with open("ArcGisIdMessages.csv", 'w', newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(("ID", "Message"))
        for id_range in (range(1, 100000), range(999997, 999999)):
            for msg_id in id_range:
                try:
                    msg = arcpy.GetIDMessage(msg_id)
                    if msg:
                        csv_writer.writerow((msg_id, msg))
                except Exception as ex:
                    stdout.write("%s\n" % ex)
                    raise


if __name__ == '__main__':
    main()
