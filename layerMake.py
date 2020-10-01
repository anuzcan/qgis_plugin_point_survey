from qgis import utils
from qgis.core import (Qgis, 
    QgsProject, QgsWkbTypes, 
    QgsPointXY, QgsFeature, QgsGeometry, 
    QgsField, QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform)
from PyQt5.QtCore import QVariant

class layerMake:
	def __init__(self,layer, point_ID = 'survey', timeSurveyPoint=0, filt = 'SINGLE'):
		
		self.layer_to_edit = layer
		layer_type = self.layer_to_edit.geometryType()
		self.count = 0

		self.timeSurveyPoint = timeSurveyPoint
		self.timeComplete = timeSurveyPoint
		self.SurveyPointEnabled = True
		self.filterPoint = self.setfilter(filt)
		self.porcent = 0
		self.pointName = point_ID

		self.latPoint = []
		self.lonPoint = []
		self.altPoint = []
		
		#print(self.layer_to_edit)
		#print(layerEPSG)
		#print(self.layer_to_edit.dataProvider().fields().names())
		#print(self.layer_to_edit.dataProvider().fields().count())

		if self.layer_to_edit.dataProvider().fields().count() > 1:
			utils.iface.messageBar().pushMessage("Warning "," The select layer is not empty",level=Qgis.Warning,duration=5)
		
		if self.layer_to_edit.dataProvider().fields().count() <= 9:

			if layer_type == QgsWkbTypes.PointGeometry:
				layerEPSG = self.layer_to_edit.crs().authid()
				crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")                      # WGS 84
				crsDest = QgsCoordinateReferenceSystem(layerEPSG)                       # WGS 84 a WGS de la capa seleccionada
				transformContext = QgsProject.instance().transformContext()             # Crear instancia de tranformacion
				self.xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)  # Crear formulario transformacion
				
				utils.iface.setActiveLayer(self.layer_to_edit)
				self.layer_to_edit.startEditing()

				if self.layer_to_edit.dataProvider().fieldNameIndex("id") == 0 and self.layer_to_edit.dataProvider().fields().count() == 1:
					self.layer_to_edit.dataProvider().addAttributes([
						QgsField(name = "PointName", type = QVariant.String, typeName = "text", len = 20),
						QgsField(name = "DATE", type = QVariant.String, typeName = "text", len = 12),
						QgsField(name = "TIME", type = QVariant.String, typeName = "text", len = 10), 
	                    QgsField(name = "LAT", type = QVariant.Double, typeName = "double", len = 23, prec = 15),
	                    QgsField(name = "LON", type = QVariant.Double, typeName = "double", len = 23, prec = 15),
	                    QgsField(name = "ALT", type = QVariant.Double, typeName = "double", len = 7, prec = 3),
	                    QgsField(name = "FIX_MODE", type = QVariant.String, typeName = "int", len = 6),
	                    QgsField(name = "SAT_N", type = QVariant.Int, typeName = "int", len = 2)])

				elif self.layer_to_edit.dataProvider().fields().count() == 0:
					self.layer_to_edit.dataProvider().addAttributes([
						QgsField(name = "id", type = QVariant.Int, typeName = "int", len = 10),
						QgsField(name = "PointName", type = QVariant.String, typeName = "text", len = 20),
						QgsField(name = "DATE", type = QVariant.String, typeName = "text", len = 12),
						QgsField(name = "TIME", type = QVariant.String, typeName = "text", len = 10), 
	                    QgsField(name = "LAT", type = QVariant.Double, typeName = "double", len = 23, prec = 15),
	                    QgsField(name = "LON", type = QVariant.Double, typeName = "double", len = 23, prec = 15),
	                    QgsField(name = "ALT", type = QVariant.Double, typeName = "double", len = 7, prec = 3),
	                    QgsField(name = "FIX_MODE", type = QVariant.String, typeName = "text", len = 6),
	                    QgsField(name = "SAT_N", type = QVariant.Int, typeName = "int", len = 2)])    

				self.layer_to_edit.updateFields()
				self.layer_to_edit.commitChanges()
				self.error = False 

		else:
			self.error = True

	def add_point(self,date,time,x,y,alt,fix_mode,sat_n,name = 'survey'):
		
		if fix_mode in self.filterPoint:
			pt1 = self.xform.transform(QgsPointXY(x, y))
			fet = QgsFeature()
			fet.setGeometry(QgsGeometry.fromPointXY(pt1))

			fet.setAttributes([self.count,name,date,time,y,x,alt,fix_mode,sat_n])
		
			self.layer_to_edit.startEditing()
			self.layer_to_edit.addFeatures([fet])
			self.layer_to_edit.commitChanges()
		
			utils.iface.mapCanvas().refresh()

			self.count += 1
		
	def collect_point(self,date,time,x,y,alt,fix_mode,sat_n):

		if self.timeSurveyPoint > 0:
			if fix_mode in self.filterPoint:
				self.latPoint.append(y)
				self.lonPoint.append(x)
				self.altPoint.append(alt)

				self.timeSurveyPoint -= 1
				self.porcent = ((self.timeComplete - self.timeSurveyPoint)/self.timeComplete)*100

		elif self.timeSurveyPoint <= 0:
			self.add_point(date,
				time,
				sum(self.lonPoint)/len(self.lonPoint),
				sum(self.latPoint)/len(self.latPoint),
				sum(self.altPoint)/len(self.altPoint),
				fix_mode,
				sat_n,
				self.pointName)

			self.porcent = 0
			self.SurveyPointEnabled = False
		

	def setfilter(self,Filter):

		if Filter == 'FIX':
			return [4]

		elif Filter == 'FLOAT':
			return [5,4]

		elif Filter == 'SINGLE':
			return [-1,1,5,4]
