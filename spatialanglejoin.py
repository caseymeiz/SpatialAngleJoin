import arcpy
import numpy as np


target = "US_SM_COPY"
join = "ROAD_Brighton"
output = "SM_Roads_Radius"
operation = "JOIN_ONE_TO_MANY"
match = "WITHIN_A_DISTANCE"
search_radius = 60

join_copy = join+"_Copy"

arcpy.env.workspace = arcpy.GetParameterAsText(0)

arcpy.CopyFeatures_management(join, join_copy)

arcpy.AddField_management(join_copy, "angle", "FLOAT")


def get_angle(line):
    p1 = line.firstPoint
    p2 = line.lastPoint
    angle = np.arctan2( p1.Y-p2.Y, p1.X-p2.X )
    return np.cos(2*angle)


with arcpy.da.UpdateCursor(join_copy, ["SHAPE@", "angle"]) as cur:
    for row in cur:
        angle = get_angle(row[0])
        row[1] = angle
        cur.updateRow(row)


arcpy.SpatialJoin_analysis(target, 
        join_copy, 
        output, 
        join_operation=operation, 
        match_option=match,
        search_radius=search_radius)


join_fields = ["SHAPE@", "Key_ID"]
output_fields = ["JOIN_FID", "angle"]

remove_sections = set()

with arcpy.da.SearchCursor(target, join_fields) as cur:
    for row in cur:
        where = "Key_ID=" + str(row[1])
        delta = None
        fid = None
        target_angle = get_angle(row[0])
        with arcpy.da.SearchCursor(output, output_fields, where_clause=where) as ucur:
            for urow in ucur:
                join_angle = urow[1]
                if join_angle is not None:
                    join_delta = np.abs(target_angle - join_angle)
                    
                    if fid is not None:
                        if join_delta < delta:
                            delta = join_delta
                            remove_sections.add(fid)
                            fid = urow[0]
                        else:
                            remove_sections.add(urow[0])
                    else:
                        delta = join_delta
                        fid = urow[0]

with arcpy.da.UpdateCursor(output,["JOIN_FID"]) as cur:
    for row in cur:
        if row[0] in remove_sections:
            cur.deleteRow()
