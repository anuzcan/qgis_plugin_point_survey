self.dlg.comboBox.clear()                                   # Vaciamos combobox al iniciar plugin prevenir llenar con lineas duplicadas
layers = QgsProject.instance().mapLayers().values()         # Leemos las capas cargadas en el proyecto y las almacenamos en un iterador
layers_names = [ layer.name() for layer in layers ]         # Pasamos el iterador a una lista 
self.dlg.comboBox.addItems(layers_names)                    # Agregamos la lista al combobox



pt1 = self.xform.transform(QgsPointXY(GPSInformation.longitude, GPSInformation.latitude))      # Obtener corrdenadas reproyectadas a la capa destino del punto
print("Transformed point:", pt1)
pt2 = xform.transform(pt1, QgsCoordinateTransform.ReverseTransform)    # Proceso inverso de reproyeccion
print("Transformed back:", pt2)

print (self.layer_to_edit.id())                            # Print capa ID