"""
Spatial Angle Join

Spatially join line features within a radius that have the most similar 
polar angle. 

"""

import arcpy
import numpy as np

arcpy.env.workspace = arcpy.GetParameterAsText(0)
#target = arcpy.GetParameterAsText(1)
#join = arcpy.GetParameterAsText(2)
#output = arcpy.GetParameterAsText(3)

target = "US_SM_COPY"
join = "ROAD_Brighton"
out_features = "SM_Roads_Radius"


operation = "JOIN_ONE_TO_MANY"
match = "WITHIN_A_DISTANCE"
search_radius = 60

join_copy = r"in_memory/join"
target_copy = r"in_memory/target"
output = r"in_memory/output"

arcpy.CopyFeatures_management(join, join_copy)
arcpy.CopyFeatures_management(target, target_copy)

arcpy.AddField_management(join_copy, "joinAngle", "FLOAT")
arcpy.AddField_management(join_copy, "delta", "FLOAT")
arcpy.AddField_management(target_copy, "targetAngle", "FLOAT")


def get_angle(line):
    p1 = line.firstPoint
    p2 = line.lastPoint
    angle = np.arctan2( p1.Y-p2.Y, p1.X-p2.X )
    angle = angle if (angle > 0) else (angle + (2*np.pi))
    angle = np.degrees(angle)
    angle = np.floor(angle)
    angle = angle % 180 
    return angle

    
with arcpy.da.UpdateCursor(join_copy, ["SHAPE@", "joinAngle"]) as cur:
    for row in cur:
        angle = get_angle(row[0])
        row[1] = angle
        cur.updateRow(row)   

        
with arcpy.da.UpdateCursor(target_copy, ["SHAPE@", "targetAngle"]) as cur:
    for row in cur:
        angle = get_angle(row[0])
        row[1] = angle
        cur.updateRow(row)

        
arcpy.SpatialJoin_analysis(target_copy, 
        join_copy, 
        output, 
        join_operation=operation, 
        match_option=match,
        search_radius=search_radius)

        
with arcpy.da.UpdateCursor(output, ["joinAngle", "targetAngle", "delta"]) as cur:
    for row in cur:
        jAngle = row[0]
        tAngle = row[1]
        if jAngle is not None:
            row[2] = np.abs(tAngle-jAngle)
        else:
            row[2] = 0
        cur.updateRow(row)


sql = (None, "ORDER BY delta ASC")
save = set()
trash = set()
with arcpy.da.SearchCursor(output, ["OID@", "Key_ID", "delta"], sql_clause = sql) as cur:
    for row in cur:
        fid = row[0]
        key = row[1]
        if key in save:
            trash.add(fid)
        else:
            save.add(key)


with arcpy.da.UpdateCursor(output, ["OID@"]) as cur:
    for row in cur:
        if row[0] in trash:
            cur.deleteRow()


arcpy.CopyFeatures_management(output, out_features)



