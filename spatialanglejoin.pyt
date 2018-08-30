import arcpy
import saj
reload(saj)
from saj import Join


class Toolbox(object):
	def __init__(self):
		self.label = "Toolbox"
		self.alias = "saj"
		# List of tool classes associated with this toolbox
		self.tools = [Join]