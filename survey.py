from PyQt5.QtWidgets import QAction, QMessageBox, QWidget, QPushButton
from PyQt5.QtCore import QTimer, QVariant, Qt
from PyQt5.QtGui import QIcon

from qgis import utils
from qgis.core import (Qgis, QgsApplication, 
    QgsProject, QgsWkbTypes, QgsPoint, 
    QgsPointXY, QgsFeature, QgsGeometry, 
    QgsField, QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform, QgsSettings)


from .survey_dialog import survey_Dialog, tools_Dialog
import os.path

class ATNPlugin:
    def __init__(self, iface):
        self.iface = iface


    def initGui(self):                                              # Rutina al cargar complemento al Qgis
        
        plg_dir = os.path.dirname(__file__)                         # Obtener ruta absoluta de plugis, necesaria para acceder recursos
        icon_path = os.path.join(plg_dir, "icon.png")               # Leemos icon

        self.action = QAction(QIcon(icon_path), "Quick Survey Plugin", self.iface.mainWindow())
        self.action.setObjectName("RunAction")
        self.action.setWhatsThis("Configuration for RTK plugin")
        self.action.setStatusTip("Plugis RTK Survey")
        self.action.triggered.connect(self.run)                     # Configuramos accion a clip icon y menu 

        # Agregamos barra de herramientas e Icon en interfas de Qgis
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Survey Tools", self.action)

        
        self.dlg = survey_Dialog()                                  # Cargamos dialogo de archivo .ui
        
        # Creamos acciones para los botones y comandos
        self.dlg.buttonSetFilterPoints.clicked.connect(self.filters)
        self.dlg.buttonRotationSet.clicked.connect(self.rotation)
        self.dlg.buttonGpsActive.clicked.connect(self.star_Read)
        self.dlg.buttonGPSPause.clicked.connect(self.pause_Read)
        self.dlg.buttonGpsDesactive.clicked.connect(self.end_Read)
        self.dlg.buttonSelectLayer.clicked.connect(self.selectLayer)
        self.dlg.buttonClose_plugin.clicked.connect(self.close_plugin)
        self.dlg.zoomInbutton.clicked.connect(self.zoomInMapCanvas)
        self.dlg.zoomOutbutton.clicked.connect(self.zoomOutMapCanvas)
        self.dlg.savePointButton.clicked.connect(self.savePoint)
        
        # Deshabilitar botones 
        self.dlg.buttonSetFilterPoints.setEnabled(False)
        self.dlg.buttonSelectLayer.setEnabled(False)
        #self.dlg.buttonSelectLayer.setEnabled(True)
        self.dlg.buttonGpsActive.setEnabled(False)          
        self.dlg.buttonGpsDesactive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(False)
        
        # Flat de control
        self.flatGPS    = False
        self.flatPAUSE  = True
        self.flatSelectedLayer = False
        self.flatRotationMap = False


        select_fixMode = ["FIX","FLOAT","SINGLE"]
        self.dlg.comboBox_Fix.addItems(select_fixMode)

        # Configurar temporizador
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_Device)                 # Enlazamos temporizador con funcion objetivo
        
    def read_setting(self):
        s = QgsSettings()
        self.plugin_name = s.value("quick_survey_plugin/plugin_name")


    def store_setting(self):
        s = QgsSettings()
        s.setValue("quick_survey_plugin/plugin_name", "Quick Survey Plugin")


    def unload(self):                                               # Rutina ejecutada al deshabilitar plugin en complementos
        # remove the plugin menu item and icon
        self.iface.removePluginMenu("&Survey Tools", self.action)
        self.iface.removeToolBarIcon(self.action)

        del self.action

    def run(self):                                                  # Rutina ejecuta al llamar plugin

        self.read_setting()
        self.flatGPS = self.testSignal()

        if self.flatGPS == True:                                  # Verificamos que este GPS conectado
            self.dlg.buttonSelectLayer.setEnabled(True)
            self.timer.start(1000)

        self.dlg.show()                                         # Cargamos Plugin

    def zoomInMapCanvas(self):
        utils.iface.mapCanvas().zoomByFactor(0.9)

    def zoomOutMapCanvas(self):
        utils.iface.mapCanvas().zoomByFactor(1.1)

    def testSignal(self):                                           # Rutina comprobar GPS Correctamento conectado
        # Registro del GPS
        self.connectionRegistry = QgsApplication.gpsConnectionRegistry()
        self.connectionList = self.connectionRegistry.connectionList()

        if self.connectionList == []:
            utils.iface.messageBar().pushMessage("Error "," Device GPS not found. Check GPS Information",level=Qgis.Critical,duration=5)
            return -1
        else:
            utils.iface.messageBar().pushMessage("OK "," Device GPS found",level=Qgis.Info,duration=5)
            return 1


    def read_Device(self):                                           # Rutina captura y almacenamiento de punto en capa
        
        GPSInformation = self.connectionList[0].currentGPSInformation()
        now = GPSInformation.utcDateTime.currentDateTime().toString(Qt.TextDate)[5:]
        self.dlg.lineLatitude.setText(str(GPSInformation.latitude)[:8])
        self.dlg.lineLongitude.setText(str(GPSInformation.longitude)[:8])
        self.dlg.lineElevation.setText(str(GPSInformation.elevation)[:8])
        self.dlg.lineFix.setText(str(GPSInformation.quality))

        self.showFix(self.dlg.lineEdit,str(GPSInformation.quality))
        quality = GPSInformation.quality
       
        
        if self.flatPAUSE == False:

            pt1 = self.xform.transform(QgsPointXY(GPSInformation.longitude, GPSInformation.latitude))      # Obtener corrdenadas reproyectadas a la capa destino del punto
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPointXY(pt1))
            fet.setAttributes([self.fieldIndex,now, GPSInformation.elevation])

            if (self.fix_filter == '1'):
                if (quality == 4 or quality == 5 or quality == 1):
                    self.layer_to_edit.addFeatures([fet])
            
            elif (self.fix_filter == '5'):
                if (quality == 4 or quality == 5):
                    self.layer_to_edit.addFeatures([fet])
            
            elif (self.fix_filter == '4'):
                if (quality == 4):
                    self.layer_to_edit.addFeatures([fet])    

            utils.iface.mapCanvas().refresh()                  # Redibujamos capa con el punto agregado
            self.fieldIndex = self.fieldIndex + 1


    def selectLayer(self):

        self.layer_to_edit = QgsProject().instance().mapLayersByName(self.dlg.mMapLayerComboBox.currentText())[0] # Tomar capa seleccionada actualmente en comboBox
        
        utils.iface.setActiveLayer(self.layer_to_edit)         # Seleccionamos como capa activa
        self.layer_to_edit.startEditing()                           # Activar edicion capa

        if self.layer_to_edit.dataProvider().fieldNameIndex("id")  == 0:           # Comprobar que disponga campos adecuadas
            self.layer_to_edit.dataProvider().addAttributes([QgsField(name = "date", type = QVariant.String, len = 20), 
                QgsField(name = "alt", type = QVariant.Double, typeName = "double", len = 7, prec = 3)])    # Agregamos campos si faltan

        else:
            self.layer_to_edit.dataProvider().addAttributes([QgsField(name = "id", type = QVariant.Double, len = 10),
                QgsField(name = "date", type = QVariant.String, len = 20), 
                QgsField(name = "alt", type = QVariant.Double, typeName = "double", len = 7, prec = 3)])    # Agregamos campos si faltan
            

        self.layer_to_edit.updateFields()                                       # Actualizamos Campos

        layerEPSG = utils.iface.activeLayer().crs().authid()   # Obtenemos EPSG de la capa Activa

        self.layer_to_edit.commitChanges()                      # Despues de actualizar los campos detenemos edicion de capa

        crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")                      # WGS 84
        crsDest = QgsCoordinateReferenceSystem(layerEPSG)                       # WGS 84 a WGS de la capa seleccionada
        transformContext = QgsProject.instance().transformContext()             # Crear instancia de tranformacion
        self.xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)  # Crear formulario transformacion
         
        self.dlg.buttonGpsActive.setEnabled(True)                   # Habilitar boton inicio
        self.dlg.buttonSelectLayer.setEnabled(False)
        self.flatSelectedLayer = True
        self.fieldIndex = 0

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

    def savePoint(self):

        self.dlg.progressBar.setValue(10)

        print(self.dlg.linePointName.text())
    
######################################################################

    def star_Read(self):                                            # Rutina inicializar toma de puntos

        self.fix_filter = self.dlg.comboBox_Fix.currentText()
        
        if self.fix_filter == 'FIX':
            self.fix_filter = '4'
            
        elif self.fix_filter == 'FLOAT':
            self.fix_filter = '5'
            
        elif self.fix_filter == 'SINGLE':
            self.fix_filter = '1'
            

        self.layer_to_edit.startEditing()
        self.flatPAUSE = False
        
        # Habilitamos botones
        self.dlg.buttonGpsActive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(True)
        self.dlg.buttonGpsDesactive.setEnabled(True)

    def pause_Read(self):

        self.flatPAUSE = True    
        
        # Habilitamos botones
        self.dlg.buttonGpsActive.setEnabled(True)
        self.dlg.buttonGPSPause.setEnabled(False)
        self.dlg.buttonGpsDesactive.setEnabled(True)

    def end_Read(self):                                          # Rutina Finalizar Captura
        
        if self.flatSelectedLayer == True:
            self.layer_to_edit.commitChanges()
        self.flatPAUSE = True

        # Habilitamos Botones
        self.dlg.buttonGpsActive.setEnabled(False)
        self.dlg.buttonGpsDesactive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(False)
        self.dlg.buttonSelectLayer.setEnabled(True)

            
    def close_plugin(self):

        self.store_setting()

        self.end_Read()
        if self.flatGPS == True:
            self.timer.stop()
        self.dlg.close()

    
    def showFix(self,parent,fix):

        if fix == "1":
            parent.setText('SINGLE')
            parent.setStyleSheet("background-color: rgb(255, 0, 0);color: rgb(255, 255, 255);")
        if fix == "5":
            parent.setText('FLOAT')
            parent.setStyleSheet("background-color: rgb(255, 128, 0);color: rgb(255, 255, 255);")
        if fix == "4":
            parent.setText('FIX')
            parent.setStyleSheet("background-color: rgb(0, 255, 0);color: rgb(255, 255, 255);")

    
