import math 
from qgis.core import (QgsCoordinateReferenceSystem,
	QgsCoordinateTransform,
	QgsProject,
	QgsPointXY)

class direction:
	def __init__(self, lat, lon, rotation=0, clockwise=False):

		self.lat = lat
		self.lon = lon

		crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")          
		crsDest = QgsCoordinateReferenceSystem("EPSG:3857")                       # WGS 84 a WGS de la capa seleccionada
		transformContext = QgsProject.instance().transformContext()             # Crear instancia de tranformacion
		self.xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)  # Crear formulario transformacion
		self.pt1 = self.xform.transform(QgsPointXY(lon, lat))

		self.rotation = rotation
		self.clockwise = clockwise

	def distance(self, lat, lon):
		self.pt2 = self.xform.transform(QgsPointXY(lon, lat))
		distance = math.sqrt((self.pt2[0] - self.pt1[0])**2 + (self.pt2[1] - self.pt1[1])**2)
		return distance

	def angle_to(self):
		if abs(self.rotation) > 360:
			self.rotation %= 360

		Dx = self.pt2[0] - self.pt1[0]
		Dy = self.pt2[1] - self.pt1[1]
		angle = math.degrees(math.atan2(Dy, Dx))

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