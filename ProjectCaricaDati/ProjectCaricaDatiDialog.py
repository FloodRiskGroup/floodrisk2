"""
/***************************************************************************
 ProjectCaricaDatiDialog
                                 A QGIS plugin
 Caricamento GeoDatabase, query sql e grafico
                             -------------------
        begin                : 2017-10-23
        copyright            : (C) 2017 by RSE
        email                : FloodRiskGroup@rse-web.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

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


from time import sleep

##import CreaGeodatabase
# import CaricaGeodatiFloodRisk
from .CaricaGeodatiFloodRisk import mainCaricaGeodatiFloodRisk                  # import script

# import CaricaCurve
from .CaricaCurve import mainCaricaCurve                                        # import script

from .help import show_context_help

# from pyspatialite import dbapi2 as db

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

vectors = [
            'shp','mif', 'tab','000','dgn','vrt','bna','csv','gml',
            'gpx','kml','geojson','itf','xml','ili','gmt',
            'sqlite','mdb','e00','dxf','gxt','txt','xml'
            ]

rasters = [
          'ecw','sid','vrt','tiff',
          'tif','ntf','toc','img',
          'gff','asc','ddf','dt0',
          'dt1','dt2','png','jpg',
          'jpeg','mem','gif','n1',
          'xpm','bmp','pix','map',
          'mpr','mpl','rgb','hgt',
          'ter','nc','grb','hdr',
          'rda','bt','lcp','rik',
          'dem','gxf','hdf5','grd',
          'grc','gen','img','blx',
          'blx','sqlite','sdat','adf'
          ]

def openFile(self,filePath,table):
    #Get the extension without the .
    extn = os.path.splitext(filePath)[1][1:].lower()

    if extn == 'qgs':
        #If we are project file we can just open that.
        self.iface.addProject(filePath)
    elif extn in vectors:
        if extn=='mdb':
            uri = "DRIVER='Microsoft Access Driver (*.mdb)',Database=%s,host=localhost|layername=%s" % (filePath,'HydroArea')
            uri = "%s |layername=%s" % (filePath,'HydroArea')
            uri = "%s |layer=%s" % (filePath,0)
        elif extn=='sqlite':
            uri = QgsDataSourceURI()
            uri.setDatabase(filePath)
            schema = ''
            geom_column = 'geom'
            uri.setDataSource(schema, table, geom_column)
            display_name=table
            self.iface.addVectorLayer(uri.uri(),display_name,"spatialite")
        else:
            self.iface.addVectorLayer(filePath,"","ogr")

    elif extn in rasters:
        self.iface.addRasterLayer(filePath,"")
    else:
        #We should never really get here, but just in case.
        pass


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ProjectCaricaDatiDialog_base.ui'))


def LayerCaricato(self,NomeLayer):
    ok=bool()
    lista= str.split(str(os.path.basename(NomeLayer)),'.')
    nome = str.split(str(os.path.basename(NomeLayer)),'.')[0]
    # layers = QgsMapLayerRegistry.instance().mapLayers().values()
    layers = QgsProject.instance().mapLayers().values()                            # Leggo i layers della mappa

    for l in layers:
        if l.name()==nome:
            ok=bool('True')
            break

    return ok

class CaricaDati_Dialog(QDialog, FORM_CLASS):
# class CaricaDati_Dialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self,iface, parent=None):
        """Constructor."""
        super(CaricaDati_Dialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface=iface
        self.numEPGS = 32633
        self.instance=0
##        self.label_loading.hide()
##        self.label_sr.hide()
        self.FilesListGeoDati = ['', '', '', '', '', '']
        self.UpLoadGeoDati = [0, 0, 0, 0, 0, 0]
        self.FilesListCsv = ['', '', '', '', '', '']
        self.UpLoadCsv = [0, 0, 0, 0, 0, 0]
        self.nomeFileSQlite = str(self.txtShellFilePath.text())

        # initialize actions
        self.txtShellFilePath.textChanged.connect(self.setNameFileSQlite)

        self.btnChooseShellFile_2.pressed.connect(self.openSystem)

        self.btnChooseShellFile_4.pressed.connect(self.setAreaStudio)

        self.btnChooseShellFile_5.pressed.connect(self.setCensimento)

        self.btnChooseShellFile_6.pressed.connect(self.setBeniAreali)

        self.btnChooseShellFile_7.pressed.connect(self.setBeniLineari)

        self.btnChooseShellFile_8.pressed.connect(self.caricaGeoDati)

        self.btnChooseShellFile_9.pressed.connect(self.CaricaLayers1)

        self.btnChooseShellFile_10.pressed.connect(self.CaricaLayers2)

        self.btnChooseShellFile_11.pressed.connect(self.CaricaLayers3)

        self.comboBox_6.currentIndexChanged.connect(self.selectComboInstance)

        self.checkBox.stateChanged.connect(self.setCheckAreaStud)
        self.checkBox_2.stateChanged.connect(self.setCheckCensimento)
        self.checkBox_3.stateChanged.connect(self.setCheckBA)
        self.checkBox_4.stateChanged.connect(self.setCheckBL)
        self.checkBox_All.stateChanged.connect(self.setCheckAll)

        self.btnChooseShellFile_16.pressed.connect(self.setFatalityR)

        self.btnChooseShellFile_17.pressed.connect(self.setFloodS)

        self.btnChooseShellFile_21.pressed.connect(self.setTipoV)

        self.btnChooseShellFile_18.pressed.connect(self.setVulnerabilita)

        self.btnChooseShellFile_22.pressed.connect(self.setTipoCategoriaBeni)

        self.checkBox_9.stateChanged.connect(self.setCheckFatalityR)
        self.checkBox_10.stateChanged.connect(self.setCheckFloodS)
        self.checkBox_12.stateChanged.connect(self.setCheckTipoV)
        self.checkBox_11.stateChanged.connect(self.setCheckTipoVulnerabilita)
        self.checkBox_13.stateChanged.connect(self.setCheckTipoCategoriaBeni)
        self.checkBox_All_3.stateChanged.connect(self.setCheckAllCsv)

        self.btnChooseShellFile_20.pressed.connect(self.caricaCurve)

        # help
        self.buttonBox.helpRequested.connect(self.show_help)

        self.DirDefault = __file__
        self.comboBox_6.clear()
        self.nomeFileSQlite =  str(self.txtShellFilePath.text())

    #----------------------------------------- Actions -----------------------------------------

    def show_help(self):
        """Load the help text into the system browser."""
        show_context_help(context='include2')

    def setNameFileSQlite(self):
        self.nomeFileSQlite =  str(self.txtShellFilePath.text())

    def setFileSql(self):
        if self.nomeFileSQlite == "":
            s = QFileDialog.getOpenFileName(None, self.tr("FloodRisk2 | Geodatabase Sqlite"),  self.DirDefault, "FloodRisk File (*.sqlite)")
            self.nomeFileSQlite = s[0]

        if self.nomeFileSQlite != "":
            self.txtShellFilePath.setText(self.nomeFileSQlite)
            self.btnChooseShellFile_2.setEnabled(True)
            self.FilesListGeoDati[0] = self.nomeFileSQlite
            self.FilesListCsv[0] = self.nomeFileSQlite
            self.UpLoadGeoDati[0] = 1
            self.UpLoadCsv[0] = 1

            # check Reference System
            res, srid = self.CheckReferenceSystem()

            if res:
                self.numEPGS = int(srid)
                msg=self.tr("Current Reference System :  EPSG=") + str(srid)
                self.label_sr.setText(msg)
                self.label_sr.show()

            self.DirDefault=os.path.dirname(self.nomeFileSQlite)    # Setto la Dir di default all'ultimo file caricato


    def openSystem(self):

        projection_selection_widget = QgsProjectionSelectionWidget()
        projection_selection_widget.selectCrs()
        SelectedQgsCoordinateReferenceSystem= projection_selection_widget.crs()
        b=SelectedQgsCoordinateReferenceSystem.authid()


        if b == '':
            QMessageBox.information(None,  self.tr("Warning"), self.tr("Attention no Reference System selected"))
        else:
            self.numEPGS = int(str(b).split(':')[1])
            self.setSistemaRiferimento()
            self.label_sr.setText(self.tr("Reference System Loaded:  ") + b)
            self.label_sr.show()

    def setSistemaRiferimento(self):
        try:
            conn = sqlite3.connect(self.nomeFileSQlite, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.enable_load_extension(True)
            conn.execute("SELECT load_extension('mod_spatialite')")
##            conn = db.connect(self.nomeFileSQlite)
            cur = conn.cursor()
            testoSql = 'UPDATE geometry_columns SET srid=%d' % (self.numEPGS)
            cur.execute(testoSql)
            conn.commit()
            cur=None
            conn.close()
        except:
            msg = self.tr("Attention: error in the definition of the reference system of the file ")  + self.nomeFileSQlite
            QMessageBox.information(None, self.tr("Setting Reference System"), msg)

    def selectComboInstance(self):
        conn = sqlite3.connect(self.nomeFileSQlite, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('mod_spatialite')")

        cur = conn.cursor()

        try:
            self.instance=self.comboBox_6.currentText()

            sql='SELECT Description from ExposureInstance WHERE instance=%s' % self.instance
            cur.execute(sql)

            Description=cur.fetchone()[0]
            self.txtDescription.setText(str(Description))
        except:
            pass

        # Close communication with the database
        cur.close()
        conn.close()


    def setAreaStudio(self):
        s = QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Analysis Area shapefile"), self.DirDefault, "FloodRisk File (*.shp)")
        self.nomeFileAreaStud = s[0]

        if self.nomeFileAreaStud !="":
            self.comboBox.setEditText(self.nomeFileAreaStud)
            self.FilesListGeoDati[1] = self.nomeFileAreaStud
            self.UpLoadGeoDati[1] = 1
            self.DirDefault=os.path.dirname(self.FilesListGeoDati[1])

    def setCensimento(self):
        s = QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Census shapefile"), self.DirDefault, "FloodRisk File (*.shp)")
        self.nomeFileCensimento = s[0]

        if self.nomeFileCensimento !="" and self.checkBox_2.isChecked():
##            self.txtShellFilePath_20.setText(self.nomeFileCensimento)
            self.comboBox_2.setEditText(self.nomeFileCensimento)
            self.FilesListGeoDati[2] = self.nomeFileCensimento
            self.UpLoadGeoDati[2] = 1
            self.DirDefault=os.path.dirname(self.FilesListGeoDati[2])

    def setBeniAreali(self):
        s = QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Estate Polygon shapefile"), self.DirDefault, "FloodRisk File (*.shp)")
        self.nomeFileBA=s[0]

        if self.nomeFileBA !="":
##            self.txtShellFilePath_18.setText(self.nomeFileBA)
            self.comboBox_4.setEditText(self.nomeFileBA)
            self.FilesListGeoDati[4] = self.nomeFileBA
            self.UpLoadGeoDati[4] = 1
            self.DirDefault=os.path.dirname(self.FilesListGeoDati[4])

    def setBeniLineari(self):
        s = QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Infrastructures Line shapefile"), self.DirDefault, "FloodRisk File (*.shp)")
        self.nomeFileBL=s[0]

        if self.nomeFileBL !="":
            self.comboBox_5.setEditText(self.nomeFileBL)
            self.FilesListGeoDati[5] = self.nomeFileBL
            self.UpLoadGeoDati[5] = 1
            self.DirDefault=os.path.dirname(self.FilesListGeoDati[5])

    #-----Managing Check
    def setCheckAreaStud(self, state):
        if state == QtCore.Qt.Checked:
            self.btnChooseShellFile_4.setEnabled(True)
            self.comboBox.setEnabled(True)
            listaFile = self.caricaComboBox([2])

            if len(listaFile) != 0:
                self.comboBox.clear()
                self.comboBox.addItems(listaFile)
        else:
            self.btnChooseShellFile_4.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.comboBox.clear()

    def setCheckCensimento(self, state2):
        if state2 == QtCore.Qt.Checked:
            if self.checkAnalysisArea():
                self.btnChooseShellFile_5.setEnabled(True)
                self.btnChooseShellFile_11.setEnabled(True)
                self.comboBox_2.setEnabled(True)
                listaFile = self.caricaComboBox([2])
                if len(listaFile) != 0:
                    self.comboBox_2.clear()
                    self.comboBox_2.addItems(listaFile)
            else:
                self.msgAnalysisArea()
        else:
            self.btnChooseShellFile_5.setEnabled(False)
            self.btnChooseShellFile_11.setEnabled(False)
            self.comboBox_2.setEnabled(False)
            self.comboBox_2.clear()

    def setCheckBA(self, state3):
        if state3 == QtCore.Qt.Checked:
            if self.checkAnalysisArea():
                self.btnChooseShellFile_6.setEnabled(True)
                self.btnChooseShellFile_9.setEnabled(True)
                self.comboBox_4.setEnabled(True)
                listaFile = self.caricaComboBox([2])

                if len(listaFile) != 0:
                    self.comboBox_4.clear()
                    self.comboBox_4.addItems(listaFile)
            else:
                self.msgAnalysisArea()
        else:
            self.btnChooseShellFile_6.setEnabled(False)
            self.btnChooseShellFile_9.setEnabled(False)
            self.comboBox_4.setEnabled(False)
            self.comboBox_4.clear()

    def setCheckBL(self, state4):
        if state4 == QtCore.Qt.Checked:
            if self.checkAnalysisArea():
                self.btnChooseShellFile_7.setEnabled(True)
                self.btnChooseShellFile_10.setEnabled(True)
                self.comboBox_5.setEnabled(True)
                listaFile = self.caricaComboBox([1])

                if len(listaFile) != 0:
                    self.comboBox_5.clear()
                    self.comboBox_5.addItems(listaFile)
            else:
                self.msgAnalysisArea()
        else:
            self.btnChooseShellFile_7.setEnabled(False)
            self.btnChooseShellFile_10.setEnabled(False)
            self.comboBox_5.setEnabled(False)
            self.comboBox_5.clear()

    def setCheckAll(self, stateAll):
        if stateAll == QtCore.Qt.Checked:
            self.btnChooseShellFile_7.setEnabled(True)
            self.btnChooseShellFile_10.setEnabled(True)
            self.checkBox_4.setChecked(True)
            self.btnChooseShellFile_6.setEnabled(True)
            self.btnChooseShellFile_9.setEnabled(True)
            self.checkBox_3.setChecked(True)
            self.btnChooseShellFile_5.setEnabled(True)
            self.btnChooseShellFile_11.setEnabled(True)
            self.checkBox_2.setChecked(True)

            listaFile = self.caricaComboBox([2])
            listaFile2 = self.caricaComboBox([1])
            self.comboBox_5.clear()
            self.comboBox_5.addItems(listaFile2)
            self.comboBox_4.clear()
            self.comboBox_4.addItems(listaFile)
            self.comboBox_2.clear()
            self.comboBox_2.addItems(listaFile)
            self.comboBox.clear()
            self.comboBox.addItems(listaFile)
        else:
            self.btnChooseShellFile_7.setEnabled(False)
            self.btnChooseShellFile_10.setEnabled(False)
            self.checkBox_4.setChecked(False)
            self.btnChooseShellFile_6.setEnabled(False)
            self.btnChooseShellFile_9.setEnabled(False)
            self.checkBox_3.setChecked(False)
            self.btnChooseShellFile_5.setEnabled(False)
            self.btnChooseShellFile_11.setEnabled(False)
            self.checkBox_2.setChecked(False)
            self.checkBox.setChecked(False)
            self.comboBox_5.clear()
            self.comboBox_4.clear()
            self.comboBox_2.clear()

    def setFatalityR(self):
        s = QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Fatality Rate file"), self.DirDefault, "FloodRisk File (*.csv)")
        self.nomeFileFatalityR=s[0]

        if self.nomeFileFatalityR !="":
            self.txtShellFilePath_12.setText(self.nomeFileFatalityR)
            self.FilesListCsv[1] = self.nomeFileFatalityR
            self.UpLoadCsv[1] = 1
            self.DirDefault=os.path.dirname(self.FilesListCsv[1])

    def setFloodS(self):
        s= QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Flood Severity file"), self.DirDefault, "FloodRisk File (*.csv)")
        self.nomeFileFloodS=s[0]

        if self.nomeFileFloodS !="":
            self.txtShellFilePath_13.setText(self.nomeFileFloodS)
            self.FilesListCsv[2] = self.nomeFileFloodS
            self.UpLoadCsv[2] = 1
            self.DirDefault=os.path.dirname(self.FilesListCsv[2])

    def setTipoV(self):
        s= QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select List of Depth-Damage Curves file"), self.DirDefault, "FloodRisk File (*.csv)")
        self.nomeFileTipoV=s[0]

        if self.nomeFileTipoV !="":
            self.txtShellFilePath_16.setText(self.nomeFileTipoV)
            self.FilesListCsv[3] = self.nomeFileTipoV
            self.UpLoadCsv[3] = 1
            self.DirDefault=os.path.dirname(self.FilesListCsv[3])

    def setVulnerabilita(self):
        s= QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select Depth-Damage Curves file"), self.DirDefault, "FloodRisk File (*.csv)")
        self.nomeFileVulnerabilita=s[0]

        if self.nomeFileVulnerabilita !="":
            self.txtShellFilePath_14.setText(self.nomeFileVulnerabilita)
            self.FilesListCsv[4] = self.nomeFileVulnerabilita
            self.UpLoadCsv[4] = 1
            self.DirDefault=os.path.dirname(self.FilesListCsv[4])

    def setTipoCategoriaBeni(self):
        s= QFileDialog.getOpenFileName(None, self.tr("FloodRisk: select OccupancyType file"), self.DirDefault, "FloodRisk File (*.csv)")
        self.nomeFileCatBeni=s[0]

        if self.nomeFileCatBeni !="":
            self.txtShellFilePath_17.setText(self.nomeFileCatBeni)
            self.FilesListCsv[5] = self.nomeFileCatBeni
            self.UpLoadCsv[5] = 1
            self.DirDefault=os.path.dirname(self.FilesListCsv[5])

    def setCheckFatalityR(self, state):
        if state == QtCore.Qt.Checked:
            self.txtShellFilePath_12.setEnabled(True)
            self.btnChooseShellFile_16.setEnabled(True)
        else:
            self.txtShellFilePath_12.setEnabled(False)
            self.btnChooseShellFile_16.setEnabled(False)

    def setCheckFloodS(self, state):
        if state == QtCore.Qt.Checked:
            self.txtShellFilePath_13.setEnabled(True)
            self.btnChooseShellFile_17.setEnabled(True)
        else:
            self.txtShellFilePath_13.setEnabled(False)
            self.btnChooseShellFile_17.setEnabled(False)

    def setCheckTipoV(self, state):
        if state == QtCore.Qt.Checked:
            self.txtShellFilePath_16.setEnabled(True)
            self.btnChooseShellFile_21.setEnabled(True)
        else:
            self.txtShellFilePath_16.setEnabled(False)
            self.btnChooseShellFile_21.setEnabled(False)

    def setCheckTipoVulnerabilita(self, state):
        if state == QtCore.Qt.Checked:
            self.txtShellFilePath_14.setEnabled(True)
            self.btnChooseShellFile_18.setEnabled(True)
        else:
            self.txtShellFilePath_14.setEnabled(False)
            self.btnChooseShellFile_18.setEnabled(False)

    def setCheckTipoCategoriaBeni(self, state):
        if state == QtCore.Qt.Checked:
            self.txtShellFilePath_17.setEnabled(True)
            self.btnChooseShellFile_22.setEnabled(True)
        else:
            self.txtShellFilePath_17.setEnabled(False)
            self.btnChooseShellFile_22.setEnabled(False)

    def setCheckAllCsv(self, stateAll):
        if stateAll == QtCore.Qt.Checked:
            self.txtShellFilePath_12.setEnabled(True)
            self.btnChooseShellFile_16.setEnabled(True)
            self.checkBox_9.setChecked(True)
            self.txtShellFilePath_13.setEnabled(True)
            self.btnChooseShellFile_17.setEnabled(True)
            self.checkBox_10.setChecked(True)
            self.txtShellFilePath_16.setEnabled(True)
            self.btnChooseShellFile_21.setEnabled(True)
            self.checkBox_12.setChecked(True)
            self.txtShellFilePath_14.setEnabled(True)
            self.btnChooseShellFile_18.setEnabled(True)
            self.checkBox_11.setChecked(True)
            self.txtShellFilePath_17.setEnabled(True)
            self.btnChooseShellFile_22.setEnabled(True)
            self.checkBox_13.setChecked(True)
        else:
            self.txtShellFilePath_12.setEnabled(False)
            self.btnChooseShellFile_16.setEnabled(False)
            self.checkBox_9.setChecked(False)
            self.txtShellFilePath_13.setEnabled(False)
            self.btnChooseShellFile_17.setEnabled(False)
            self.checkBox_10.setChecked(False)
            self.txtShellFilePath_16.setEnabled(False)
            self.btnChooseShellFile_21.setEnabled(False)
            self.checkBox_12.setChecked(False)
            self.txtShellFilePath_14.setEnabled(False)
            self.btnChooseShellFile_18.setEnabled(False)
            self.checkBox_11.setChecked(False)
            self.txtShellFilePath_17.setEnabled(False)
            self.btnChooseShellFile_22.setEnabled(False)
            self.checkBox_13.setChecked(False)

    def caricaGeoDati(self):

        if self.CheckGeodatabase():
            if not self.checkAnalysisArea():
                self.msgAnalysisArea()
            else:
##                self.label_loading.show()
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                self.udateGeoFileLists()
                NotErr, errMsg = mainCaricaGeodatiFloodRisk(self,self.FilesListGeoDati, self.UpLoadGeoDati, self.progressBarGeo,int(self.instance))
                QApplication.restoreOverrideCursor()

                if NotErr:
                    QMessageBox.information(None, "FloodRisk", self.tr("Files have been uploaded"))
                else:
                    QMessageBox.information(None, "FloodRisk", errMsg)
##                self.label_loading.hide()
                res=self.checkAnalysisAreaReferenceSystem()
        else:
            QMessageBox.information(None, "FloodRisk", self.tr("You must first create the Geodb.Sqlite"))


    def caricaCurve(self):
        FileSql= str(self.txtShellFilePath.text())

        if (FileSql == ""):
            QMessageBox.information(None, "FloodRisk", self.tr("First load the DataBase"))
        else:
            if self.CheckGeodatabase()==True:
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
##                self.label_loading.show()
                NotErr, errMsg = mainCaricaCurve(self.FilesListCsv, self.UpLoadCsv, self.progressBarAlfa, int(self.instance))
                QApplication.restoreOverrideCursor()

                if NotErr:
                    QMessageBox.information(None, "FloodRisk", self.tr("Files have been uploaded"))
                else:
                    QMessageBox.information(None, "FloodRisk", errMsg)
##                self.label_loading.hide()
            else:
                QMessageBox.information(None, "FloodRisk", self.tr("You must first create the Geodb.Sqlite"))


    def caricaComboBox(self, FeatureType):
        listAreaStudio = []
        listAreaStudio = self.getLayerSourceByMe(FeatureType)
        return listAreaStudio

    def getLayerSourceByMe(self, vTypes):
        import locale
         # layermap = QgsMapLayerRegistry.instance().mapLayers()
        layermap = QgsProject.instance().mapLayers().values()                            # Leggo i layers della mappa
        layerlist = []

        if vTypes == "all":
            # for name, layer in layermap.iteritems():
            #     layerlist.append( layer.source() )

            for layer in layermap:
                layerlist.append(layer.source())
        else:

            for layer in layermap:
                if layer.type() == QgsMapLayer.VectorLayer:
                    geomType= layer.geometryType()
                    if  geomType in vTypes:
                        layerlist.append(layer.source())
                elif layer.type() == QgsMapLayer.RasterLayer:
                    if "Raster" in vTypes:
                        layerlist.append( layer.source() )

        return sorted( layerlist)


    def checkAnalysisArea(self):
        nome = self.comboBox.currentText()

        if nome != "":
            if os.path.exists(nome):
                res = bool('True')
                return res
            else:
                res = bool()
                return res
        else:
            mydb_path = str(self.txtShellFilePath.text())

            if os.path.exists(mydb_path):
                # creating/connecting the db
                conn = sqlite3.connect(mydb_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
                conn.enable_load_extension(True)
                conn.execute("SELECT load_extension('mod_spatialite')")

                # conn = db.connect(mydb_path)
                # creating a Cursor
                cur = conn.cursor()
                NomeTabella='AnalysisArea'
                sql="SELECT AsText(geom) FROM %s;" % (NomeTabella)
                cur.execute(sql)
                GeomAreawkt=cur.fetchone()

                if GeomAreawkt != None:
                    res = bool('True')
                else:
                    res = bool('')
            else:
                res = bool('')

            return res


    def msgAnalysisArea(self):
        msg=self.tr("Please, upload firstly Analysis Area")
        QMessageBox.information(None, "Warning", msg)

    def udateGeoFileLists(self):
        nomeFileAreaStud = self.comboBox.currentText()
        state=self.checkBox.checkState()

        if len(nomeFileAreaStud)>0 and state == QtCore.Qt.Checked:
            self.FilesListGeoDati[1] = nomeFileAreaStud
            self.UpLoadGeoDati[1] = 1
        else:
            self.UpLoadGeoDati[1] = 0

        nomeFileCensimento = self.comboBox_2.currentText()
        state=self.checkBox_2.checkState()

        if len(nomeFileCensimento)>0 and state == QtCore.Qt.Checked:
            self.FilesListGeoDati[2] = nomeFileCensimento
            self.UpLoadGeoDati[2] = 1
        else:
            self.UpLoadGeoDati[2] = 0

        self.UpLoadGeoDati[3] = 0

        nomeFileBA = self.comboBox_4.currentText()

        if len(nomeFileBA)>0 and self.checkBox_3.isChecked():
            self.FilesListGeoDati[4] = nomeFileBA
            self.UpLoadGeoDati[4] = 1
        else:
            self.UpLoadGeoDati[4] = 0

        nomeFileBL = self.comboBox_5.currentText()

        if len(nomeFileBL)>0 and self.checkBox_4.isChecked():
            self.FilesListGeoDati[5] = nomeFileBL
            self.UpLoadGeoDati[5] = 1
        else:
            self.UpLoadGeoDati[5] = 0


    def CheckGeodatabase(self):
        res=bool()

        if os.path.exists(self.FilesListGeoDati[0]):
            mydb_path=self.FilesListGeoDati[0]

            try:
                conn = sqlite3.connect(mydb_path,detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
                conn.enable_load_extension(True)
                conn.execute("SELECT load_extension('mod_spatialite')")

                # conn = db.connect(mydb_path)                    # creating/connecting the test_db
                cur = conn.cursor()                             # creating a Cursor

                TablesList=['spatial_ref_sys','AnalysisArea','CensusBlocks','FatalityRate']
                TablesList.append('FatalityRate')
                TablesList.append('FloodSeverity')
                TablesList.append('InfrastrLines')
                TablesList.append('VulnType')
                TablesList.append('Vulnerability')
                TablesList.append('StructurePoly')

                for NomeTabella in TablesList:
                    sql="SELECT sql FROM sqlite_master WHERE type='table' AND name='%s';" % (NomeTabella)
                    cur.execute(sql)
                    Tabella=str(cur.fetchone()[0])

                res = bool('True')
            except:
                res = bool()
        else:
            res = bool()
        return res


    def CheckReferenceSystem(self):
        res=bool()
        srid=0

        if os.path.exists(self.FilesListGeoDati[0]):
            mydb_path=self.FilesListGeoDati[0]

            try:
                # connecting the db
                conn = sqlite3.connect(mydb_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
                conn.enable_load_extension(True)
                conn.execute("SELECT load_extension('mod_spatialite')")
##                conn = db.connect(mydb_path)
                # creating a Cursor
                cur = conn.cursor()
                NomeTabella='analysisarea'
                sql="SELECT srid FROM geometry_columns WHERE f_table_name='%s';" % (NomeTabella)
                cur.execute(sql)
                listasrid=cur.fetchone()
                srid=str(listasrid[0])
                res=bool('True')

            except:
                res=bool()
        else:
            res=bool()

        return res, srid


    def checkAnalysisAreaReferenceSystem(self):
        res = bool('')

        try:
            mydb_path = str(self.txtShellFilePath.text())

            if os.path.exists(mydb_path):
                # creating/connecting the test_db
                conn = sqlite3.connect(mydb_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
                conn.enable_load_extension(True)
                conn.execute("SELECT load_extension('mod_spatialite')")

##                conn = db.connect(mydb_path)
                # creating a Cursor
                cur = conn.cursor()
                NomeTabella='AnalysisArea'
                sql="SELECT AsText(geom) FROM %s;" % (NomeTabella)
                cur.execute(sql)
                GeomAreawkt=cur.fetchone()

                if GeomAreawkt != None:
                    res = bool('True')
                    self.btnChooseShellFile_2.setEnabled(False)
                    # check Reference System
                    res, srid=self.CheckReferenceSystem()

                    if res:
                        self.numEPGS = int(srid)
                        msg=self.tr("Current Reference System :  EPSG=") + str(srid)
                        self.label_sr.setText(msg)
                        self.label_sr.show()

            else:
                res = bool('')
                self.btnChooseShellFile_2.setEnabled(True)

            return res
        except:
            res = bool('')
            self.btnChooseShellFile_2.setEnabled(True)
            return res


    def CaricaLayers1(self):
        filePath = self.comboBox_4.currentText()

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')


    def CaricaLayers2(self):
        filePath = self.comboBox_5.currentText()

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')


    def CaricaLayers3(self):
        filePath = self.comboBox_2.currentText()

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')

