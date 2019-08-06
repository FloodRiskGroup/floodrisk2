# ============================================================================================
import sys
import os
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from qgis.core import *
from qgis.gui import *
# ============================================================================================

#from ui_Image1 import Ui_Dialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Image1.ui'))

class Image1(QDialog, FORM_CLASS):

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(Image1, self).__init__(parent)

		#QDialog.__init__(self)
        self.setupUi(self)
        self.iface=iface

        self.label.setPixmap(QPixmap(":/plugins/floodrisk2/ProjectCalcolaRischio/SUFRI_Table.png"))


