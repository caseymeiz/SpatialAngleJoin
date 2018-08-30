'''
Demo Spatial Angle Join

This script must be run from the demo folder or else the 
toolbox, input, and output locations must be adjusted for
where demo.py is being run.

cd SpatialAnglJoin/demo

python -i demo.py

'''

import arcpy

arcpy.ImportToolbox(r"..\spatialanglejoin.pyt")

target = r"workspace.gdb\Sewer"
join = r"workspace.gdb\Roads"
workspace = r"workspace.gdb"
output = r"demo" # just the name of the output features
search_radius = 75
overwriteOutput = True

arcpy.Join_saj(target, join, workspace, output, search_radius, overwriteOutput)