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