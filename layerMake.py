from qgis import utils
from qgis.core import (Qgis, QgsApplication, 
    QgsProject, QgsWkbTypes, QgsPoint, 
    QgsPointXY, QgsFeature, QgsGeometry, 
    QgsField, QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform, QgsSettings)
from PyQt5.QtCore import QVariant

class layerMake:
	def __init__(self,layer):
		
		self.layer_to_edit = layer
		layer_type = self.layer_to_edit.geometryType()
		self.count = 0

		self.timeSurveyPoint = 0
		self.porcent = 0
		self.pointName = []

		self.latPoint = []
		self.lonPoint = []
		self.altPoint = []
		
		#print(self.layer_to_edit)
		#print(layerEPSG)
		#print(self.layer_to_edit.dataProvider().fields().names())
		#print(self.layer_to_edit.dataProvider().fields().count())

		if self.layer_to_edit.dataProvider().fields().count() > 1:
			utils.iface.messageBar().pushMessage("Warning "," The select layer is not empty",level=Qgis.Warning,duration=5)
		
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

	def add_point(self,date,time,x,y,alt,fix_mode,sat_n):
		pt1 = self.xform.transform(QgsPointXY(x, y))
		fet = QgsFeature()
		fet.setGeometry(QgsGeometry.fromPointXY(pt1))
		fet.setAttributes([self.count, date, time,y,x,alt,fix_mode,sat_n])
		self.layer_to_edit.startEditing()
		self.layer_to_edit.addFeatures([fet])
		self.layer_to_edit.commitChanges()
		
		utils.iface.mapCanvas().refresh()

		self.count += 1
		
	def collect_point(self,x,y,alt,fix_mode):

		if self.timeSurveyPoint > -1:
			self.latPoint.append(y)
			self.lonPoint.append(x)
			self.altPoint.append(alt)

			print(self.latPoint)

			self.porcent = ((self.timeComplete - self.timeSurveyPoint)/self.timeComplete)*100
			self.timeSurveyPoint -= 1
		
		else:
			print('test')
			#print(sum(self.latPoint)/len(self.latPoint))
			#print(sum(self.lonPoint)/len(self.lonPoint))
			#print(sum(self.altPoint)/len(self.altPoint))
			#self.latPoint.clear()
			#self.lonPoint.clear()
			#self.altPoint.clear()

	def print(self):
		print(self.layer_to_edit)
		return True
'''
if self.timeSurveyPoint <= -1:

                self.dlg.progressBar.setValue(0)
                self.dlg.savePointButton.setEnabled(True)
                self.flatSurveyPoint = False

                self.PointToLayer(self.layer_for_point,self.pointName)

            else:
                porcent = ((self.timeComplete - self.timeSurveyPoint)/self.timeComplete)*100

                self.latPoint.append(GPSInformation.latitude)
                self.lonPoint.append(GPSInformation.longitude)
                self.altPoint.append(GPSInformation.elevation)

                self.dlg.progressBar.setValue(porcent)
                self.timeSurveyPoint -= 1

def PointToLayer(self,layer,pointID):

        utils.iface.setActiveLayer(layer)     
        
        layerEPSG = utils.iface.activeLayer().crs().authid()
        crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")                      # WGS 84
        crsDest = QgsCoordinateReferenceSystem(layerEPSG)                       # WGS 84 a WGS de la capa seleccionada
        transformContext = QgsProject.instance().transformContext()             # Crear instancia de tranformacion
        xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)  # Crear formulario transformacion
        
        layer.startEditing()             

        point = xform.transform(QgsPointXY(sum(self.lonPoint)/len(self.lonPoint), sum(self.latPoint)/len(self.latPoint)))      # Obtener corrdenadas reproyectadas a la capa destino del punto
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPointXY(point))
        fet.setAttributes([pointID,sum(self.altPoint)/len(self.altPoint)]) 

        layer.addFeatures([fet])
        utils.iface.mapCanvas().refresh()

        layer.commitChanges()                      # Despues de actualizar los campos detenemos edicion de capa

        self.latPoint.clear()
        self.lonPoint.clear()
        self.altPoint.clear()
'''