from PyQt5.QtWidgets import QAction, QMessageBox, QWidget, QPushButton
from PyQt5.QtCore import QTimer, QVariant, Qt
from PyQt5.QtGui import QIcon, QColor

from qgis import utils

from qgis.core import (Qgis, QgsApplication, 
    QgsProject, QgsWkbTypes, QgsPoint, 
    QgsPointXY, QgsFeature, QgsGeometry, 
    QgsField, QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform, QgsSettings)

from .survey_dialog import survey_Dialog, tools_Dialog
import os.path

from .layerMake import layerMake
from .direction import direction, point_pos, guide
from .informationScripts import informations

class ATNPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):                                              # Rutina al cargar complemento al Qgis
        
        plg_dir = os.path.dirname(__file__)                         # Obtener ruta absoluta de plugis, necesaria para acceder recursos
        icon_path = os.path.join(plg_dir, "icon.png")               # Leemos icon

        self.info_user = informations('Espanol')

        self.action = QAction(QIcon(icon_path), self.info_user.plugin_name, self.iface.mainWindow())
        self.action.setObjectName("RunAction")
        self.action.setWhatsThis("Configuration for RTK plugin")
        self.action.setStatusTip("Plugin RTK Survey")
        self.action.triggered.connect(self.run)                     # Configuramos accion a clip icon y menu 

        # Agregamos barra de herramientas e Icon en interfas de Qgis
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.info_user.plugin_menu, self.action)

        self.dlg = survey_Dialog()                                  # Cargamos dialogo de archivo .ui

        # Creamos acciones para los botones y comandos
        self.dlg.buttonGpsActive.clicked.connect(self.star_Read)
        self.dlg.buttonGPSPause.clicked.connect(self.pause_Read)
        self.dlg.buttonGpsDesactive.clicked.connect(self.end_Read)
        self.dlg.buttonSelectLayer.clicked.connect(self.SelectLayerSurvey)
        self.dlg.buttonClose_plugin.clicked.connect(self.close_plugin)
        self.dlg.zoomInbutton.clicked.connect(self.zoomInMapCanvas)
        self.dlg.zoomOutbutton.clicked.connect(self.zoomOutMapCanvas)
        self.dlg.savePointButton.clicked.connect(self.StartSavePoint)
        self.dlg.setRotation.clicked.connect(self.rotation)
        self.dlg.configButton.clicked.connect(self.filters)
        # Deshabilitar botones 
        self.dlg.buttonSelectLayer.setEnabled(False)
        self.dlg.buttonGpsActive.setEnabled(False)          
        self.dlg.buttonGPSPause.setEnabled(False)
        self.dlg.buttonGpsDesactive.setEnabled(False)
        self.dlg.savePointButton.setEnabled(False)

        # Flat de control
        self.flatSurveyContinuos  = False
        self.flatRotationMap = False
        self.flatDirection = False
        self.flatSurveyPoint = False
        self.flatSurveyStar = False
        self.countSurveyName = 0

        select_fixMode = ["FIX","FLOAT","SINGLE"]
        self.dlg.comboBox_Fix.addItems(select_fixMode)

        self.dlg.lineEdit_2.setText('No Activo')
        self.dlg.lineEdit_2.setStyleSheet("background-color: rgb(255, 0, 0);color: rgb(255, 255, 255);")

        # Configurar temporizador
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_Device)                 # Enlazamos temporizador con funcion objetivo

    def unload(self):                                               # Rutina ejecutada al deshabilitar plugin en complementos
        # remove the plugin menu item and icon
        self.iface.removePluginMenu(self.info_user.plugin_menu, self.action)
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):                                                  # Rutina ejecuta al llamar plugin
        self.read_setting()
        self.flatGPS = self.testSignal()
    
        self.guide = guide(self.iface.mapCanvas())
        
        self.namePointFlat = self.dlg.linePointName.text()[:self.dlg.linePointName.text().find('-')]

        if self.flatGPS == True:                                  # Verificamos que este GPS conectado
            self.dlg.buttonSelectLayer.setEnabled(True)
            self.dlg.savePointButton.setEnabled(True)
            self.timer.start(1000)

        self.dlg.show()                                         # Cargamos Plugin

    def testSignal(self):                                           # Rutina comprobar GPS Correctamento conectado
        # Registro del GPS
        self.connectionList = QgsApplication.gpsConnectionRegistry().connectionList()

        if self.connectionList == []:
            utils.iface.messageBar().pushMessage("Error ",self.info_user.plugin_error_gps1,level=Qgis.Critical,duration=5)
            return -1
        else:
            utils.iface.messageBar().pushMessage("OK ",self.info_user.plugin_ok1,level=Qgis.Info,duration=5)
            return 1

    def read_Device(self):                                           # Rutina captura y almacenamiento de punto en capa
        
        try:
            GPSInformation = self.connectionList[0].currentGPSInformation()
        except:
            utils.iface.messageBar().pushMessage("Error ",self.info_user.plugin_error_gps2,level=Qgis.Critical,duration=10)
            self.timer.stop()
            
        now = GPSInformation.utcDateTime.currentDateTime().toString(Qt.TextDate)
        self.dlg.lineLatitude.setText(str(GPSInformation.latitude)[:11])
        self.dlg.lineLongitude.setText(str(GPSInformation.longitude)[:11])
        self.dlg.lineElevation.setText(str(GPSInformation.elevation)[:8])
        self.dlg.lineFix.setText(str(GPSInformation.quality))

        self.showFix(self.dlg.lineEdit,str(GPSInformation.quality))
        
        quality = GPSInformation.quality
        date = now[22:]+'-'+now[5:8]+'-'+now[10:12]
        time = now[13:21]

        # Rutina para coleccion de puntos de forma continua
        if self.flatSurveyContinuos == True:
            
            if self.flatDirection == True:
            	self.direc = direction(clockwise=True)
            	self.direc.new_point(GPSInformation.longitude,GPSInformation.latitude)
            	self.flatDirection = False
            else:
                angle = self.direc.angle_to(GPSInformation.longitude,GPSInformation.latitude)
                dist = self.direc.distance(GPSInformation.longitude,GPSInformation.latitude)
                
                #self.guide.paint()
                
                if dist > self.filter_length:
                    self.layerSurvey.add_point(date,time,GPSInformation.longitude,GPSInformation.latitude,GPSInformation.elevation,quality,len(GPSInformation.satPrn))
                    self.direc.new_point(GPSInformation.longitude,GPSInformation.latitude)

                #Rutina para rotar mapa con forme nos movemos en el campo
                if self.flatRotationMap == True:
                    if dist > self.filter_rotation:
                        utils.iface.mapCanvas().setRotation(360 - angle)

        # Rutina para acumular coordenadas para crear un punto promedio
        if self.flatSurveyPoint == True:
            if self.layer_for_point.SurveyPointEnabled == True:
                self.layer_for_point.collect_point(date,time,GPSInformation.longitude,GPSInformation.latitude,GPSInformation.elevation,quality,len(GPSInformation.satPrn))
                self.dlg.progressBar.setValue(self.layer_for_point.porcent)

            if self.layer_for_point.SurveyPointEnabled == False:
                self.flatSurveyPoint = self.layer_for_point.SurveyPointEnabled
                self.flatSurveyStar = False
                self.countSurveyName += 1
                self.dlg.linePointName.setText(self.layer_for_point.pointName[:self.layer_for_point.pointName.find('-')+1]+str(self.countSurveyName))
                self.dlg.savePointButton.setText('SavePoint')


    def SelectLayerSurvey(self):

        self.layerSurvey = layerMake(
            QgsProject().instance().mapLayersByName(self.dlg.mMapLayerComboBox.currentText())[0],
            filt = self.dlg.comboBox_Fix.currentText())

        if self.layerSurvey.error == False: 
            self.dlg.buttonGpsActive.setEnabled(True)                   # Habilitar boton inicio
            self.dlg.buttonSelectLayer.setEnabled(False)
            
        else:
            utils.iface.messageBar().pushMessage("Warning "," The select layer is not enable",level=Qgis.Warning,duration=5)

    def StartSavePoint(self):

        if self.flatSurveyStar == False:

            if self.dlg.linePointName.text().find('-') != -1:
                self.namePoint = self.dlg.linePointName.text()[:self.dlg.linePointName.text().find('-') + 1]
            else:
                self.namePoint = self.dlg.linePointName.text() + '-'

            if self.namePointFlat + '-' != self.namePoint:
                self.namePointFlat = self.namePoint[:self.namePoint.find('-')]
                self.countSurveyName = 0

            self.layer_for_point = layerMake(QgsProject().instance().mapLayersByName(self.dlg.mMapLayer_for_point.currentText())[0],
                self.namePoint + str(self.countSurveyName),
                self.dlg.spinBoxTime.value(),
                self.dlg.comboBox_Fix.currentText())
        
            if self.layer_for_point.error == False:            
                self.flatSurveyPoint = True
                self.dlg.savePointButton.setText('Cancel')
                self.flatSurveyStar = True
            
            else:
                utils.iface.messageBar().pushMessage("Warning "," The select layer is not enable",level=Qgis.Warning,duration=5)

        else:
            self.flatSurveyPoint = False
            self.flatSurveyStar = False
            self.dlg.progressBar.setValue(0)
            self.dlg.savePointButton.setText('SavePoint')

    def star_Read(self):                                            # Rutina inicializar toma de puntos
        self.flatSurveyContinuos = True
        self.flatDirection = True
              
        # Habilitamos botones
        self.dlg.buttonGpsActive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(True)
        self.dlg.buttonGpsDesactive.setEnabled(True)
        self.dlg.configButton.setEnabled(False)

    def pause_Read(self):
        self.flatSurveyContinuos = False    
        # Habilitamos botones
        self.dlg.buttonGpsActive.setEnabled(True)
        self.dlg.buttonGPSPause.setEnabled(False)
        self.dlg.buttonGpsDesactive.setEnabled(True)

    def end_Read(self):                                          # Rutina Finalizar Captura
        self.flatSurveyContinuos = False
        self.flatDirection = True
        # Habilitamos Botones
        self.dlg.buttonGpsActive.setEnabled(False)
        self.dlg.buttonGpsDesactive.setEnabled(False)
        self.dlg.buttonGPSPause.setEnabled(False)
        self.dlg.buttonSelectLayer.setEnabled(True)
        self.dlg.configButton.setEnabled(True)

    def close_plugin(self):
        self.store_setting()
        
        self.guide.erase()

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

    def read_setting(self):
        s = QgsSettings()
        self.plugin_name = s.value("quick_survey_plugin/plugin_name")
        timeSurvey = s.value("quick_survey_plugin/timeSurveyPoint","10")
        self.dlg.spinBoxTime.setValue(int(timeSurvey))
        namePoint = s.value("quick_survey_plugin/namePoint","WP")
        self.dlg.linePointName.setText(namePoint+'-'+str(self.countSurveyName))
        indexFilter = s.value("quick_survey_plugin/indexFilter", 0)
        self.dlg.comboBox_Fix.setCurrentIndex(int(indexFilter))
        
        self.filter_length = float(s.value("quick_survey_plugin/filter_len", 1))
        self.filter_rotation = float(s.value("quick_survey_plugin/filter_rotation", 1))

    def store_setting(self):
        s = QgsSettings()
        s.setValue("quick_survey_plugin/plugin_name", "Quick Survey Plugin")
        s.setValue("quick_survey_plugin/timeSurveyPoint", self.dlg.spinBoxTime.value())
        s.setValue("quick_survey_plugin/indexFilter", self.dlg.comboBox_Fix.currentIndex())
        s.setValue("quick_survey_plugin/filter_len",self.filter_length)
        s.setValue("quick_survey_plugin/filter_rotation",self.filter_rotation)

        if self.dlg.linePointName.text().find('-') != -1:
            name = self.dlg.linePointName.text()[:self.dlg.linePointName.text().find('-')]
        else:
            name = self.dlg.linePointName.text()
        
        s.setValue("quick_survey_plugin/namePoint",name)

    def filters(self):
        self.dlgtools = tools_Dialog(self.dlg)
        self.dlgtools.filter_distance.setValue(self.filter_length)
        self.dlgtools.filter_rotation.setValue(self.filter_rotation)
        
        self.dlgtools.pushButton.clicked.connect(self.closeFilter)
        self.dlgtools.show()

    def closeFilter(self):
        self.filter_length = self.dlgtools.filter_distance.value()
        self.filter_rotation = self.dlgtools.filter_rotation.value()

        self.dlgtools.close()
        del self.dlgtools

    def zoomInMapCanvas(self):
        utils.iface.mapCanvas().zoomByFactor(0.8)

    def zoomOutMapCanvas(self):
        utils.iface.mapCanvas().zoomByFactor(1.2)
        
    def rotation(self):
        if self.flatRotationMap == False:
            self.dlg.lineEdit_2.setText('Activo')
            self.dlg.lineEdit_2.setStyleSheet("background-color: rgb(0, 255, 0);color: rgb(255, 255, 255);")
            self.flatRotationMap = True            
        else:
            utils.iface.mapCanvas().setRotation(0)
            self.dlg.lineEdit_2.setText('No Activo')
            self.dlg.lineEdit_2.setStyleSheet("background-color: rgb(255, 0, 0);color: rgb(255, 255, 255);")
            self.flatRotationMap = False
