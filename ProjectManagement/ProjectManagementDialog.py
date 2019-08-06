# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Floodrisk_2Dialog
                                 A QGIS plugin
 Floodrisk_2
                             -------------------
        begin                : 2017-10-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by RSE
        email                : ...@rse-web.it
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
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
# ============================================================================================

import os
import sqlite3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui

from qgis.core import *

from PyQt5 import QtGui, uic
#from pip.utils import call_subprocess

from PyQt5.QtWidgets import QApplication, QDialog

import os, shutil, subprocess
import os.path

from xml.dom import minidom
from xml.dom.minidom import Document
import codecs

import string

from .help import show_context_help

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    from osgeo import ogr
except:
    import ogr


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
        pass


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ProjectManagementDialog_base.ui'))


def LayerCaricato(self,NomeLayer):
    ok=bool()
    lista= str.split(str(os.path.basename(NomeLayer)),'.')
    nome = str.split(str(os.path.basename(NomeLayer)),'.')[0]
    # layers = QgsMapLayerRegistry.instance().mapLayers().values()
    layers = QgsProject.instance().mapLayers().values()

    for l in layers:
        if l.name()==nome:
            ok=bool('True')
            break
    return ok


class ProjectDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(ProjectDialog, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # LM : Save reference to the QGIS interface
        self.iface = iface

##        QObject.connect(self.btnChooseShellFile_2, SIGNAL("clicked()"), self.contextMenuEvent)          # Carica/crea file geodatabase
##        QObject.connect(self.pushButton_NewInstance, SIGNAL("clicked()"), self.ScriviDB_HI)             # HazardInstance save
##        self.comboBox_6.currentIndexChanged.connect(self.selectComboIstanza)                            # Carico il combo instance
        # --------------------------------------------------------------------------------------------------------------------------
##        QObject.connect(self.btnChooseShellFile_Altezze, SIGNAL("clicked()"), self.setFile_HI1)         # Carica file altezze
##        QObject.connect(self.btnChooseShellFile_velocita, SIGNAL("clicked()"), self.setFile_HI2)        # Carica file velocità
##        QObject.connect(self.btnChooseShellFile_tempi, SIGNAL("clicked()"), self.setFile_HI3)           # Carica file tempi
##        self.comboBox.currentIndexChanged.connect(self.selectComboRecent)                               # Carico il combo dei recenti
##        self.comboBox_5.currentIndexChanged.connect(self.selectComboTempo)                              # Carico il combo dei tempi
##        self.comboBox_5.editTextChanged.connect(self.CancellaPercorsi)                                  # Cancello i percorsi
##
##        self.comboBox_6.editTextChanged.connect(self.CancellaDescrizione)                                   #
##
##        # --------------------------------------------------------------------------------------------------------------------------
##        QObject.connect(self.pushButtonLoadLayer, SIGNAL("clicked()"), self.CaricaLayers)               # Carica i layers
##        # --------------------------------------------------------------------------------------------------------------------------
##
##        # help
##        QObject.connect(self.buttonBox, SIGNAL(_fromUtf8("helpRequested()")), self.show_help)
##
##        self.comboBox_6.clear()

# ================================================================================================
        # self.btnChooseShellFile_2.pressed.connect(self.contextMenuEvent)          # Load/make a file geodatabase
        self.btnChooseShellFile_2.pressed.connect(self.setFile2)                    # Load/make a file geodatabase
        self.btnChooseShellFile_3.pressed.connect(self.setNewFileGDB)               # Load/make a file geodatabase

        self.pushButton_NewInstance.pressed.connect(self.ScriviDB_HI)               # HazardInstance save
        self.comboBox_6.currentIndexChanged.connect(self.selectComboIstanza)        # Update combo instance
        # --------------------------------------------------------------------------------------------------------------------------
        self.btnChooseShellFile_Altezze.pressed.connect(self.setFile_HI1)           # Load water depth file
        self.btnChooseShellFile_velocita.pressed.connect(self.setFile_HI2)          # Load velocity file
        self.btnChooseShellFile_tempi.pressed.connect(self.setFile_HI3)             # Load warning time file
        self.comboBox.currentIndexChanged.connect(self.selectComboRecent)           # Carico il combo dei recenti
        self.comboBox_5.currentIndexChanged.connect(self.selectComboTempo)          # Carico il combo dei tempi
        self.comboBox_5.editTextChanged.connect(self.CancellaPercorsi)              # Cancello i percorsi

        self.comboBox_6.editTextChanged.connect(self.CancellaDescrizione)           #
        # --------------------------------------------------------------------------------------------------------------------------
        self.pushButtonLoadLayer.pressed.connect(self.CaricaLayers)                 # Load layers
        # --------------------------------------------------------------------------------------------------------------------------

        #self.buttonBox.accepted.connect(Dialog.accept)
        #self.buttonBox.rejected.connect(Dialog.reject)
        # help
        self.buttonBox.helpRequested.connect(self.show_help)

        self.comboBox_6.clear()
# ================================================================================================

        # self.DirDefault = __file__
        self.DirDefault = 'D:'
        self.DirPG = os.path.dirname(__file__)
        self.NomeFile_TemplateDB = self.DirPG + os.sep + 'db' + os.sep + 'GeoDB_Floodrisk_2_template.sqlite'
        self.NomeFile_ListaRecenti = self.DirPG + os.sep + 'FilesRecent.xml'

        # -----------------------------------------------------------------------------------------
        self.CaricaComboRecenti()

# ================================================================================================
    def show_help(self):
        """Load the help text into the system browser."""
        show_context_help(context='include1')

##    def contextMenuEvent(self):
##        current = QCursor.pos()
##        menu = QMenu(self)
##        menu.addAction(self.tr("Open file"), self.setFile2)
##        menu.addSeparator()
##        menu.addAction(self.tr("New file"), self.setNewFileGDB)
##
##        if not menu.isEmpty():
##            menu.exec_(current)
##
##        menu.deleteLater()


    def setNewFileGDB(self):
        s = QFileDialog.getSaveFileName(None, self.tr("Floodrisk: select new sqlite file"), self.DirDefault, "Floodrisk.sqlite File (*.sqlite)");
        filename = s[0]

        if filename!="":
            self.NomeFileSQLITE = filename

            if os.path.exists(filename):
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setWindowTitle('Floodrisk')
                msgBox.setText(self.tr("File already exists"))
                msgBox.setInformativeText(self.tr("Do you want to overwrite it?"));
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok)
                ret = msgBox.exec_()

                if ret == QMessageBox.Ok:
                    os.remove(filename)
                    shutil.copy(self.NomeFile_TemplateDB, filename)
                    self.AggiornaListaFileRecenti()
                    self.CaricaComboRecenti()
                    self.CaricaDB()
            else:
                shutil.copy(self.NomeFile_TemplateDB, filename)
                self.AggiornaListaFileRecenti()
                self.CaricaComboRecenti()
                self.CaricaDB()


# ================================================================================================
    def setFile2(self):                                                 # Nome File DB
        s = QFileDialog.getOpenFileName(None, self.tr("Open'"), self.DirDefault, "DB file (*.sqlite)")
        self.NomeFileSQLITE = s[0]

        if self.NomeFileSQLITE !="":
            self.DirDefault = os.path.dirname(self.NomeFileSQLITE)      # Setto la Dir di default all'ultimo file caricato
            self.AggiornaListaFileRecenti()
            self.CaricaComboRecenti()
            self.CaricaDB()


    def CaricaDB(self):                                                 #
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.lineEdit_3.setText("")
        self.CancellaPercorsi()

        try:
            # ------------------- Carico il database e inserisco i dati nel ComboBox (Hazard Istance) ---------------------------------
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            cursor = conn.execute("SELECT instance from HazardInstance")

            for row in cursor:
                self.comboBox_6.addItem(str(row[0]))
        except:
            pass


    def ScriviDB_HI(self):                                              # Scrivo il nella tabella HazardInstance del DB
        text, ok = QInputDialog.getText(self, self.tr('Description'), self.tr('Enter your description:'))

        if ok:
            self.lineEdit_3.setText(str(text))
            self.SbloccaTasti(True)
        else:
            return

        self.s1 = str(self.comboBox_6.currentText())                    # Carico l'istanza nella variabile
        self.s3 = str(self.lineEdit_3.text())                           # Carico la descrizione nella variabile

        if self.s1 !="":
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            cur = conn.cursor()

            instance_curr = self.s1
            description_curr = self.s3 = str(self.lineEdit_3.text())    # Carico la descrizione nella variabile
            sql = "SELECT OBJECTID FROM HazardInstance WHERE instance=%s; " % (instance_curr)
            cur = conn.execute(sql)
            ListOBJ = cur.fetchone()

            if ListOBJ != None:
                msg1=self.tr('Instance num=')
                msg2=self.tr('already exists, do you want to change the description ?')
                quit_msg = '%s %s %s' % (msg1,instance_curr,msg2)
                reply = QMessageBox.question(self,self.tr('Message'), quit_msg, QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    sql = "UPDATE HazardInstance SET Description ='%s' WHERE OBJECTID=%d;" % (description_curr ,ListOBJ[0])
                    cur.execute(sql)

                conn.commit()
                cur.close()
                conn.close()
            else:
                sql="INSERT INTO HazardInstance (instance, Description) VALUES (%s,'%s'); "  %  (self.s1 , self.s3)
                cur.execute(sql)
                conn.commit()
                cur.close()
                conn.close()
                self.comboBox_6.addItem( self.s1)

        self.SbloccaTasti(True)
        self.CancellaPercorsi()

    def selectComboIstanza(self):                                       # Seleziono il combo e carico il DB
        try:
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            cursor = conn.execute("SELECT instance, Description from HazardInstance")

            for row in cursor:
                self.p1= str(row[0])
                self.p2= str(self.comboBox_6.currentText())

                if self.p1 == self.p2:
                    self.s1 = str(row[0])                                   # Istanza
                    self.s3 =  str(row[1])                                  # Descrizione
                    self.lineEdit_3.setText(self.s3)                        # Carico la descrizione nel TextBox

            # ------------------- Carico il database e inserisco i dati nel ComboBox (Hazard Files) ---------------------------------
            self.instance_curr=self.comboBox_6.currentText()

            if self.instance_curr == "":
                return ""

            cursor = conn.execute("SELECT DISTINCT YearReturnPeriod from HazardFiles WHERE instance=%s" % self.instance_curr)
            self.comboBox_5.clear()

            for row in cursor:
                self.comboBox_5.addItem(str(row[0]))

            cursor.close()
            conn.close()
        except:
            pass


    def setFile_HI1(self):                                              # File HI1
        s = QFileDialog.getOpenFileName(None, self.tr("Open"), self.DirDefault, "File TIF (*.tif)")
        self.NomeFileHI1 = s[0]

        if self.NomeFileHI1 !="":
            self.DirDefault=os.path.dirname(self.NomeFileHI1)           # Setto la Dir di default all'ultimo file caricato
            self.s4 = '1'                                               # Tipo 1
            self.s5 = self.NomeFileHI1                                  # Path 1
            self.ScriviDB_HF()
            self.lineEdit_4.setText (self.NomeFileHI1)

    def setFile_HI2(self):                                              # File HI2
        s = QFileDialog.getOpenFileName(None, self.tr("Open"), self.DirDefault, "File TIF (*.tif)")
        self.NomeFileHI2 = s[0]

        if self.NomeFileHI2 !="":
            self.DirDefault=os.path.dirname(self.NomeFileHI2)           # Setto la Dir di default all'ultimo file caricato
            self.s4 = '2'                                               # Tipo 2
            self.s5 = self.NomeFileHI2                                  # Path 2
            self.ScriviDB_HF()
            self.lineEdit_5.setText (self.NomeFileHI2)

    def setFile_HI3(self):                                              #File HI3
        s = QFileDialog.getOpenFileName(None, self.tr("Open"), self.DirDefault, "File (*.shp)")
        self.NomeFileHI3 = s[0]

        if self.NomeFileHI3 !="":
            self.DirDefault=os.path.dirname(self.NomeFileHI3)           # Setto la Dir di default all'ultimo file caricato
            self.s4 = '3'                                               # Tipo 3
            self.s5 = self.NomeFileHI3                                  # Path 3
            self.ScriviDB_HF()
            self.lineEdit_6.setText (self.NomeFileHI3)

    def ScriviDB_HF(self):                                              # Scrivo il nella tabella HazardFiles del DB
        self.s3 = str(self.comboBox_5.currentText())                    # Tempo di ritorno

        if self.s3 !="":
            self.conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            self.cur = self.conn.cursor()
            sql = "SELECT OBJECTID FROM HazardFiles WHERE instance=%s AND YearReturnPeriod=%s AND Type=%s; " % (self.s1, self.s3, self.s4)
            self.cur = self.conn.execute(sql)
            ListOBJ = self.cur.fetchone()

            if ListOBJ != None:
                msgBox = QMessageBox();
                msgBox.setText("This record already exists, do you want to overwrite it?");
                msgBox.setInformativeText("Do you want to save your changes?");
                msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
                msgBox.setDefaultButton(QMessageBox.No);
                reply = msgBox.exec();

                if reply == QMessageBox.Yes:
                    sql = "UPDATE HazardFiles SET Path ='%s' WHERE OBJECTID=%d;" % (self.s5 ,ListOBJ[0])
                    self.cur.execute(sql)
            else:
                sql="INSERT INTO HazardFiles (instance, YearReturnPeriod, Type, Path) VALUES (%s,%s,%s,'%s'); "  %  (self.s1, self.s3, self.s4, self.s5)
                self.cur.execute(sql)

                # -------------------- set ComboBox ----------------------
                nC = self.comboBox_5.count()
                OK=False

                for i in range(0,nC):
                    ss = self.comboBox_5.itemText(i)

                    if self.s3 == ss:
                        OK=True
                        break

                if OK == False:
                    self.comboBox_5.addItem(self.s3)
                # --------------------------------------------------------

            self.conn.commit()
            self.cur.close()
            self.conn.close()


    def CancellaPercorsi(self):
        self.lineEdit_4.setText("")
        self.lineEdit_5.setText("")
        self.lineEdit_6.setText("")
        self.SbloccaTasti(True)


    def selectComboTempo(self):
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        Instance_curr=self.comboBox_6.currentText()
        Tr_curr=self.comboBox_5.currentText()

        if Instance_curr == "" or Tr_curr == "":
            return ""

        sql="SELECT Type, Path from HazardFiles WHERE instance=%s AND YearReturnPeriod=%s" % (Instance_curr,Tr_curr)
        cursor = conn.execute(sql)
        ListaFiles=cursor.fetchall()

        self.CancellaPercorsi()

        for row in ListaFiles:
            if row[0]==1:
                self.lineEdit_4.setText(row[1])                       # Carico la descrizione nel TextBox
            elif  row[0]==2:
                self.lineEdit_5.setText(row[1])                       # Carico la descrizione nel TextBox
            elif  row[0]==3:
                self.lineEdit_6.setText(row[1])                       # Carico la descrizione nel TextBox

        cursor.close()
        conn.close()


    def CaricaLayers(self):
        #filePath=str(self.txtShellFilePath_2.text())

        #if os.path.exists(filePath):
            #tabelle=['StructurePoly','InfrastrLines','CensusBlocks']

            #for nomelayer in tabelle:
                # checks if the layer is already loaded
             #   if not LayerCaricato(self,nomelayer):
             #       openFile(self,filePath,nomelayer)

        filePath = self.lineEdit_4.text()

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')

        filePath=self.lineEdit_5.text()

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')

        filePath=self.lineEdit_6.text()

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')


    def CaricaComboRecenti(self):
        self.ListaFilesRecenti = []
        self.ListaFilesRecenti = self.LeggeListaFileRecenti()
        self.comboBox.clear()

        for F in self.ListaFilesRecenti:
            self.comboBox.addItem(str(F))


    def selectComboRecent(self):
        self.NomeFileSQLITE = self.comboBox.currentText()
        self.CaricaDB()
        # self.groupBox.setEnabled(False)
        self.SbloccaTasti(False)

    def LeggeListaFileRecenti(self):
        # reading recent project files
        self.nomefilelista = self.NomeFile_ListaRecenti
        nn = 0
        self.ListaFilesRecenti=[]

        if os.path.exists(self.nomefilelista):
            xmlfile = open(self.nomefilelista)
            dom = minidom.parse(xmlfile)

            for node in dom.getElementsByTagName("General"):
                L = node.getElementsByTagName("File")
                Num=[]

                for node2 in L:
                    nfile = int(node2.getAttribute("Num"))
                    nomefile = node2.getAttribute("name")
                    nomefile = os.path.abspath(nomefile)

                    if os.path.exists(nomefile):
                        Num.append(nfile)
                        self.ListaFilesRecenti.append(nomefile)

            xmlfile.close()
            nn=len(Num)
        return self.ListaFilesRecenti


    def AggiornaListaFileRecenti(self):
        self.nomefilelista = self.NomeFile_ListaRecenti
        nn = len(self.ListaFilesRecenti)

        # fileprogetto = str(self.txtShellFilePath_2.text())
        fileprogetto = str(self.NomeFileSQLITE)

        fileprogetto = os.path.abspath(fileprogetto)

        if os.path.exists(fileprogetto):
            # Create the minidom document
            doc = Document()

            # Create the <wml> base element
            wml = doc.createElement("FLOODRISK_2")
            doc.appendChild(wml)

            # Create the main <card> element
            maincard = doc.createElement("General")
            wml.appendChild(maincard)

            # Create a <p> element
            kf=0
            kfmax=5

            # ShellFilePath = str(self.txtShellFilePath_2.text())
            ShellFilePath = str(self.NomeFileSQLITE)
            # ShellFilePath = self.comboBox.currentText()

            paragraph1 = doc.createElement("File")
            paragraph1.setAttribute("Num", str(kf))
            paragraph1.setAttribute("name", fileprogetto)
            maincard.appendChild(paragraph1)

            if nn > 0:
                for i in range(nn):
                    nome_cur = self.ListaFilesRecenti[i]
                    nome_cur = os.path.abspath(nome_cur)

                    if os.path.exists(nome_cur) and nome_cur!=fileprogetto:
                        kf = kf + 1

                        if kf < kfmax:
                            paragraph1 = doc.createElement("File")
                            paragraph1.setAttribute("Num", str(kf))
                            paragraph1.setAttribute("name", nome_cur)
                            maincard.appendChild(paragraph1)
                        else:
                            break

            with codecs.open(self.nomefilelista, "w", "utf-8") as out:
                doc.writexml(out,"", "   ", "\n")                               # Scrivo il file recenti


    def CancellaDescrizione(self):
        self.lineEdit_3.setText("")
        self.SbloccaTasti(False)


    def SbloccaTasti(self, bStato):
        self.btnChooseShellFile_Altezze.setEnabled(bStato)
        self.btnChooseShellFile_velocita.setEnabled(bStato)
        self.btnChooseShellFile_tempi.setEnabled(bStato)