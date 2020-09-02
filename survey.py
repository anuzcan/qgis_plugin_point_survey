from PyQt5.QtWidgets import QAction, QMessageBox, QWidget, QPushButton
from PyQt5.QtCore import QTimer, QVariant, Qt
from PyQt5.QtGui import QIcon

from qgis import*
from qgis.core import (Qgis, QgsApplication, 
    QgsProject, QgsWkbTypes, QgsPoint, 
    QgsPointXY, QgsFeature, QgsGeometry, 
    QgsField, QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform)

import gdal
from gdalconst import *

from .survey_dialog import survey_Dialog, tools_Dialog
import os.path

class ATNPlugin:
    def __init__(self, iface):
        self.iface = iface


    def initGui(self):                                              # Rutina al cargar complemento al Qgis
        
        plg_dir = os.path.dirname(__file__)                         # Obtener ruta absoluta de plugis, necesaria para acceder recursos
        icon_path = os.path.join(plg_dir, "icon.png")               # Leemos icon

        self.action = QAction(QIcon(icon_path), "ATN", self.iface.mainWindow())
        self.action.setObjectName("RunAction")
        self.action.setWhatsThis("Configuration for RTK plugin")
        self.action.setStatusTip("Plugis RTK Survey")
        self.action.triggered.connect(self.run)                     # Configuramos accion a clip icon y menu 

        # Agregamos barra de herramientas e Icon en interfas de Qgis
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&ATN herramientas", self.action)

        # connect to signal renderComplete which is emitted when canvas rendering is done
        self.iface.mapCanvas().renderComplete.connect(self.renderTest)
        
        self.dlg = survey_Dialog()                                  # Cargamos dialogo de archivo .ui
        self.dlgtools = tools_Dialog(self.dlg)

        # Creamos acciones para los botones y comandos
        self.dlg.buttonRotationPrint.clicked.connect(self.rotation)
        self.dlg.buttonGpsActive.clicked.connect(self.star_Read)
        self.dlg.buttonGPSPause.clicked.connect(self.pause_Read)
        self.dlg.buttonGpsDesactive.clicked.connect(self.cancel_Read)
        self.dlg.buttonSelectLayer.clicked.connect(self.selectLayer)
        self.dlg.buttonAbort.clicked.connect(self.Abort)
        
        # Deshabilitar botones 
        self.dlg.buttonGpsActive.setEnabled(False)          
        self.dlg.buttonGpsDesactive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(False)
        
        # Flat de control
        self.flatGPS    = False
        self.flatPAUSE  = True

        # Configurar temporizador
        self.timer = QTimer()
        self.timer.timeout.connect(self.point_Read)                 # Enlazamos temporizador con funcion objetivo


    def unload(self):                                               # Rutina ejecutada al deshabilitar plugin en complementos
        # remove the plugin menu item and icon
        self.iface.removePluginMenu("&ATN herramientas", self.action)
        self.iface.removeToolBarIcon(self.action)

        # disconnect form signal of the canvas
        self.iface.mapCanvas().renderComplete.disconnect(self.renderTest)
        del self.action


    def run(self):                                                  # Rutina ejecuta al llamar plugin

        if self.testSignal() == 0:                                  # Verificamos que este GPS conectado
            self.dlg.close()                                        # Si GPS no Conectado cerrar plugin
        
        else:
            self.dlg.show()                                         # Cargamos Plugin
            #self.dlgtools.show()


    def selectLayer(self):
        self.layer_to_edit = QgsProject().instance().mapLayersByName(self.dlg.mMapLayerComboBox.currentText())[0] # Tomar capa seleccionada actualmente en comboBox
        #print (self.layer_to_edit.id())                            # Print capa ID
        qgis.utils.iface.setActiveLayer(self.layer_to_edit)         # Seleccionamos como capa activa
        self.layer_to_edit.startEditing()                           # Activar edicion capa

        if self.layer_to_edit.dataProvider().fieldNameIndex("DATE")  == -1:           # Comprobar que disponga campos adecuadas
            self.layer_to_edit.dataProvider().addAttributes([QgsField(name = "DATE", type = QVariant.String, len = 20), 
                QgsField(name = "ALT", type = QVariant.Double, typeName = "double", len = 4, prec = 3)])    # Agregamos campos si faltan
            self.layer_to_edit.updateFields()                                       # Actualizamos Campos

        layerEPSG = qgis.utils.iface.activeLayer().crs().authid()   # Obtenemos EPSG de la capa Activa
        #print(layerEPSG[layerEPSG.find(":") + 1 : ])               # Imprimimos EPSG

        crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")                      # WGS 84
        crsDest = QgsCoordinateReferenceSystem(layerEPSG)                       # WGS 84 a WGS de la capa seleccionada
        transformContext = QgsProject.instance().transformContext()             # Crear instancia de tranformacion
        self.xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)  # Crear formulario transformacion

        self.timer.start(1000)                                      # Lanzamos inicio de temporizador 

        self.dlg.buttonGpsActive.setEnabled(True)                   # Habilitar boton inicio
        self.dlg.buttonSelectLayer.setEnabled(False)

    def star_Read(self):                                            # Rutina inicializar toma de puntos

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

    def cancel_Read(self):                                          # Rutina Finalizar Captura
        
        self.flatPAUSE = True

        # Habilitamos Botones
        self.dlg.buttonGpsActive.setEnabled(False)
        self.dlg.buttonGpsDesactive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(False)
        self.dlg.buttonSelectLayer.setEnabled(True)

        self.layer_to_edit.commitChanges()                          # Detener edicion y almacenar cambios de la capa

        
    def point_Read(self):                                           # Rutina captura y almacenamiento de punto en capa
        
        GPSInformation = self.connectionList[0].currentGPSInformation()
        now = GPSInformation.utcDateTime.currentDateTime().toString(Qt.TextDate)[5:]
        self.dlg.lineLatitude.setText(str(GPSInformation.latitude))
        self.dlg.lineLongitude.setText(str(GPSInformation.longitude))
        self.dlg.lineElevation.setText(str(GPSInformation.elevation))
        self.dlg.lineFix.setText(str(GPSInformation.fixMode))

        # Listado de Informacion disponible del GPS
        #GPSInformation.latitude
        #GPSInformation.longitude
        #GPSInformation.elevation
        #GPSInformation.utcDateTime
        """
        # https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)
        print('hdop: ',GPSInformation.hdop)     # horizontal dilution of precision
        print('vdop: ',GPSInformation.vdop)     # vertical dilution of precision
        print('pdop: ',GPSInformation.pdop)     # position (3D) dilution of precision
        print('quality: ',GPSInformation.quality)  # Calidad
        
        print('hacc: ',GPSInformation.hacc)          
        print('vacc: ',GPSInformation.vacc)
        print('fixMode: ',GPSInformation.fixMode)

        print('direction: ',GPSInformation.direction)
        #
        print('fixType: ',GPSInformation.fixType)
        #(GPSInformation.satInfoComplete)
        #(GPSInformation.satPrn)
        #(GPSInformation.satellitesInView)
        #(GPSInformation.speed)
        #GPSInformation.status
        
        
        #print(now) # PyQt5.QtCore.QDateTime(2020, 8, 28, 4, 2, 32, 0, PyQt5.QtCore.Qt.TimeSpec(1))
        """
        
        if self.flatPAUSE == False:
                
            pt1 = self.xform.transform(QgsPointXY(GPSInformation.longitude, GPSInformation.latitude))      # Obtener corrdenadas reproyectadas a la capa destino del punto
            
            fet = QgsFeature()                                      # Instancia de entidad
            fet.setGeometry(QgsGeometry.fromPointXY(pt1))           # Asignamos geometria
            fet.setAttributes([now, GPSInformation.elevation])   # Asignamos propiedades 
            self.layer_to_edit.addFeatures([fet])                   # Agregamos entidad a la capa

            qgis.utils.iface.mapCanvas().refresh()                  # Redibujamos capa con el punto agregado

    
    def testSignal(self):                                           # Rutina comprobar GPS Correctamento conectado
        # Registro del GPS
        self.connectionRegistry = QgsApplication.gpsConnectionRegistry()
        self.connectionList = self.connectionRegistry.connectionList()

        if self.connectionList == []:
        	qgis.utils.iface.messageBar().pushMessage("Error"," Dispositivo GPS no encontrado. Verificar Informacion GPS",level=Qgis.Critical,duration=5)
        	return -1
        else:
            return 1

    def Abort(self):
        
        self.timer.stop()
        self.cancel_Read()

        try:
            self.layer_to_edit.commitChanges()                      # Detener edicion y almacenar cambios de la capa
        except:
            print("ok")

        self.dlgtools.close()
        self.dlg.close()


    def rotation(self):

        rot = qgis.utils.iface.mapCanvas().rotation()
        qgis.utils.iface.mapCanvas().setRotation(rot + 10)
    

    def renderTest(self, painter):
        # use painter for drawing to map canvas
        print("TestPlugin: renderTest called!")
