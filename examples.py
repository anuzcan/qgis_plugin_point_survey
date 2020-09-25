self.dlg.comboBox.clear()                                   # Vaciamos combobox al iniciar plugin prevenir llenar con lineas duplicadas
layers = QgsProject.instance().mapLayers().values()         # Leemos las capas cargadas en el proyecto y las almacenamos en un iterador
layers_names = [ layer.name() for layer in layers ]         # Pasamos el iterador a una lista 
self.dlg.comboBox.addItems(layers_names)                    # Agregamos la lista al combobox



pt1 = self.xform.transform(QgsPointXY(GPSInformation.longitude, GPSInformation.latitude))      # Obtener corrdenadas reproyectadas a la capa destino del punto
print("Transformed point:", pt1)
pt2 = xform.transform(pt1, QgsCoordinateTransform.ReverseTransform)    # Proceso inverso de reproyeccion
print("Transformed back:", pt2)

print (self.layer_to_edit.id())                            # Print capa ID


layerEPSG = utils.iface.activeLayer().crs().authid()   # Obtenemos EPSG de la capa Activa
print(layerEPSG[layerEPSG.find(":") + 1 : ])               # Imprimimos EPSG


self.layer_for_point = QgsProject().instance().mapLayersByName(self.dlg.mMapLayer_for_point.currentText())[0]
        layer_type = self.layer_for_point.geometryType()

        if layer_type == QgsWkbTypes.PointGeometry:
            print('Point Layer')
        elif layer_type == QgsWkbTypes.LineGeometry:
            print('Line Layer')
        elif layer_type == QgsWkbTypes.PolygonGeometry:
            print('Polygon Layer')

        print(self.layer_for_point.id()) 



#################################################################################
# connect to signal renderComplete which is emitted when canvas rendering is done
self.iface.mapCanvas().renderComplete.connect(self.renderTest)
	# Funcion llamada cuando el mapa se renderiza
	def renderTest(self, painter):
        # use painter for drawing to map canvas
        print("TestPlugin: renderTest called!")

# disconnect form signal of the canvas
self.iface.mapCanvas().renderComplete.disconnect(self.renderTest)
#################################################################################
https://qgis.github.io/pyqgis/3.2/core/Gps/QgsGpsInformation.html
# Listado de Informacion disponible del GPS
        #GPSInformation.latitude
        #GPSInformation.longitude
        #GPSInformation.elevation
        #GPSInformation.utcDateTime
        #GPSInformation.quality
        #GPSInformation.fixMode
    
        #GPSInformation.hdop     # horizontal dilution of precision
        #GPSInformation.vdop     # vertical dilution of precision
        #GPSInformation.pdop     # position (3D) dilution of precision
        #GPSInformation.quality  # Calidad
        
        #GPSInformation.hacc          
        #GPSInformation.vacc

        #GPSInformation.direction
        
        #GPSInformation.fixType
        #GPSInformation.satInfoComplete
        #GPSInformation.satPrn
        #GPSInformation.satellitesInView
        #GPSInformation.speed
        #GPSInformation.status

######################################################################
    #On Construction
    def filters(self):
        
        self.dlgtools = tools_Dialog(self.dlg)
        self.dlgtools.pushButton.clicked.connect(self.closeFilter)
        self.dlgtools.show()

    def closeFilter(self):

        hdop = self.dlgtools.hdopSpinBox.value()
        vdop = self.dlgtools.vdopSpinBox.value()
        pdop = self.dlgtools.pdopSpinBox.value()
        self.dlgtools.close()
        del self.dlgtools

    def rotation(self):

        if self.flatRotationMap == False:
            self.flatRotationMap = True
            rot = utils.iface.mapCanvas().rotation()
            utils.iface.mapCanvas().setRotation(rot + 10)
        else:
            self.flatRotationMap = False

######################################################################
    
    def distance(p0,p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def angle_to(p1, p2, rotation=0, clockwise=False):
        if abs(rotation) > 360:
            rotation %= 360
        p2 = list(p2)
        p2[0] = p2[0] - p1[0]
        p2[1] = p2[1] - p1[1]

        angle = math.degrees(math.atan2(p2[0], p2[1]))
        if clockwise:
            angle -= rotation
            return angle if angle > 0 else angle + 360
        else:
            angle = (360 - angle if angle > 0 else -1 * angle) - rotation
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

#p1 = [10,15]
#p2 = [90,100]

#print(distance(p1,p2))
#print(angle_to(p1,p2,clockwise=True))
#print(point_pos(p1, distance(p1,p2), angle_to(p1,p2,clockwise=True), clockwise=True)) 