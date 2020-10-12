import math 
from qgis.core import (QgsCoordinateReferenceSystem,
	QgsCoordinateTransform,
	QgsProject,
	QgsPointXY,
	QgsPoint,
	QgsGeometry,
	QgsWkbTypes)

from qgis.gui import QgsRubberBand
from PyQt5.QtGui import QColor

class direction:
	def __init__(self, rotation=0, clockwise=False):

		crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")          
		crsDest = QgsCoordinateReferenceSystem("EPSG:3857")                       # WGS 84 a WGS de la capa seleccionada
		transformContext = QgsProject.instance().transformContext()             # Crear instancia de tranformacion
		self.xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)  # Crear formulario transformacion
		
		self.rotation = rotation
		self.clockwise = clockwise

	def new_point(self, lon, lat):
		self.pt1 = self.xform.transform(QgsPointXY(lon, lat))

	def distance(self, lon, lat):
		pt2 = self.xform.transform(QgsPointXY(lon, lat))
		distance = math.sqrt((pt2[0] - self.pt1[0])**2 + (pt2[1] - self.pt1[1])**2)
		return distance

	def angle_to(self, lon, lat):
		pt2 = self.xform.transform(QgsPointXY(lon, lat))

		if abs(self.rotation) > 360:
			self.rotation %= 360

		Dx = pt2[0] - self.pt1[0]
		Dy = pt2[1] - self.pt1[1]
		angle = math.degrees(math.atan2(Dx, Dy))

		if self.clockwise:
			angle -= self.rotation
			return angle if angle > 0 else angle + 360
		else:
			angle = (360 - angle if angle > 0 else -1 * angle) - self.rotation
			return angle if angle > 0 else angle + 360


def point_pos(origin, amplitude, angle, rotation=0, clockwise=False):
	if abs(rotation) > 360:
		rotation %= 360
	if clockwise:
		rotation *= -1
	if clockwise:
		angle -= rotation
		angle = angle if angle > 0 else angle + 360
	else:
		angle = (360 - angle if angle > 0 else -1 * angle) - rotation
		angle = angle if angle > 0 else angle + 360

	theta_rad = math.radians(angle)
	return int(origin[0] + amplitude * math.sin(theta_rad)), int(origin[1] + amplitude * math.cos(theta_rad))


# https://stackoverrun.com/es/q/10271498

class guide:
	def __init__(self,mapCanvas):
		print(mapCanvas.mapSettings().destinationCrs().authid())
		self.r_polyline = QgsRubberBand(mapCanvas, False)
		self.r_polyline.setWidth(2)
		self.r_polyline.setColor(QColor(0, 100, 255))
	
	def paint(self):
		points = [QgsPoint(-85, 10), QgsPoint(-84, 10.5), QgsPoint(-84, 10.4)]
		self.r_polyline.setToGeometry(QgsGeometry.fromPolyline(points), None)
    
	def erase(self):
		self.r_polyline.reset(QgsWkbTypes.LineGeometry)