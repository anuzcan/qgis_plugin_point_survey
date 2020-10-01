import os

from PyQt5 import uic
from PyQt5 import QtWidgets

from .informationScripts import informations
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'dlgmain.ui'))

class survey_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(survey_Dialog, self).__init__(parent)
        self.info_user = informations('Espanol')
        self.setupUi(self)
    
    def closeEvent(self,event):
        reply = QtWidgets.QMessageBox.question(self,self.info_user.close,
            self.info_user.question1, 
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()

        else:
            event.ignore()
