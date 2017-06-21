"""Export tools Python Toolbox for ArcGIS
"""

import os
import re
import zipfile
import arcpy
from arcgiscsv import write_to_csv

# pylint: disable=invalid-name,unused-argument

class Toolbox(object):
    "Defines toolbox level properties"
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Export Tools"
        self.alias = "export"

        # List of tool classes associated with this toolbox
        self.tools = [ExportToCsv, AddFilesToZip]


class ExportToCsv(object):
    """Defines the "Export to CSV" tool
    """
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Export to CSV"
        self.description = "Exports a table to CSV"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

        table_param = arcpy.Parameter(
            displayName="Input Table",
            name="in_table",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input")

        out_csv_param = arcpy.Parameter(
            displayName="Output CSV File",
            name="out_csv_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        where_clause_param = arcpy.Parameter(
            displayName="Where Clause",
            name="where_clause",
            datatype="GPSQLExpression",
            parameterType="Optional",
            direction="Input"
        )

        fields_param = arcpy.Parameter(
            displayName="Fields",
            name="fields",
            datatype="GPFieldInfo",
            parameterType="Optional",
            direction="Input"
        )

        # This will make the SQL parameter editor in the dialog populate
        # with fields from the input table parameter.
        where_clause_param.parameterDependencies = [table_param.name]
        fields_param.parameterDependencies = [table_param.name]

        params = [table_param, out_csv_param, where_clause_param, fields_param]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        table_param = parameters[0]
        out_csv_param = parameters[1]
        # Provide a default file path based on input table name if user has not
        # provided one.
        if table_param.value and not out_csv_param.altered:
            out_csv_param.value = os.path.join(
                arcpy.env.scratchFolder, "%s.csv" % table_param.value)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        table = parameters[0].valueAsText
        csvFile = parameters[1].valueAsText
        whereClause = parameters[2].valueAsText
        fields = parameters[3].valueAsText
        # Fields will be listed in this format. We only care about the first
        # part (the actual field name)
        # SiteId '' VISIBLE NONE;SiteLocation '' VISIBLE NONE

        # Convert the GPFieldInfo list into an array of field names
        # Split field names into array at ';', then strip everything but
        # field name from each string in array.
        if fields is not None:
            r = re.compile(r"^\S+")
            fields = map(lambda s: r.match(s).group(0), fields.split(';'))

        row_count = write_to_csv(
            table, csvFile, where_clause=whereClause, field_names=fields)
        if row_count < 1:
            arcpy.AddIDMessage("WARNING", 117)
            arcpy.AddWarning("%d rows written to %s" %
                             (row_count, os.path.split(csvFile)[1]))
        else:
            arcpy.AddMessage("%d rows written to %s" %
                             (row_count, os.path.split(csvFile)[1]))
        return


class AddFilesToZip(object):
    """Defines toolbox that adds files to a zip archive file.
    """
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add files to ZIP"
        self.description = "Adds files to a ZIP archive"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

        in_files_param = arcpy.Parameter(
            displayName="Input Files",
            name="in_files",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        out_zip_param = arcpy.Parameter(
            displayName="Output ZIP File",
            name="out_zip",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        params = [in_files_param, out_zip_param]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        in_files = parameters[0].valueAsText.split(";")
        zip_path = parameters[1].valueAsText

        arcpy.SetProgressor("step", "Adding files to %s" %
                            zip_path, 1, len(in_files), 1)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for in_file in in_files:
                arcpy.AddMessage("Adding %s to %s..." % (in_file, zip_path))
                z.write(in_file, os.path.split(in_file)[1])
                arcpy.SetProgressorPosition()
        arcpy.ResetProgressor()
        return
