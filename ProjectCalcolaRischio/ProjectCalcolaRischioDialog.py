"""
/***************************************************************************
 ProjectCalcolaRischioDialog
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
# ============================================================================================

#import CreaGeodatabase
#import CaricaGeodatiFloodRisk
#import CaricaCurve

from .tableViewer_gui import TableViewer

# to reading cvs file
import csv
import locale

try:
    from pylab import *
except:
    pass

# from qgis.gui import QgsGenericProjectionSelector                     ??????????????????????????????
# from pyspatialite import dbapi2 as db
from time import sleep

import os.path
import os, shutil, subprocess
import string

from .CalcolaScenarioRischio import mainCalcolaRischio                  # import dello script per il calcolo dello scenario
from .help import show_context_help

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


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ProjectCalcolaRischioDialog_base.ui'))


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


def checkNumRowsFromCSV(pathToCsvFile,sep):
    ok=False

    try :
        with open(pathToCsvFile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=sep, quotechar='"')
##            headers = reader.next()
            headers = reader.__next__()
            numheaders=len(headers)

            if numheaders>1:
##                row = reader.next()
                row = reader.__next__()
                numrow=len(row)

                if numheaders==numrow:
                    ok=True
    except:
        pass

    return ok


def check_csv_separator(pathToCsvFile):
    locale.setlocale(locale.LC_ALL, '') # set to user's locale, not "C"
    dec_pt_chr = locale.localeconv()['decimal_point']

    if dec_pt_chr == ",":
        list_delimiter = ";"
    else:
        list_delimiter = ","

    check1=checkNumRowsFromCSV(pathToCsvFile,list_delimiter)

    if not check1:
        if list_delimiter==',':
            list_delimiter=';'
        elif list_delimiter==';':
            list_delimiter=','

        check2 = checkNumRowsFromCSV(pathToCsvFile,list_delimiter)

        if not check2:
            list_delimiter=' '

    return list_delimiter


class CalcolaRischio_Dialog(QDialog, FORM_CLASS):
    def __init__(self,iface, parent=None):
        """Constructor."""
        super(CalcolaRischio_Dialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface=iface

        # initialize actions
        self.comboBox_3.currentIndexChanged.connect(self.selectComboScenario)

        # QObject.connect(self.pushButtonSalvaProgetto_2, SIGNAL("clicked()"), self.ScriviDB_Scenario)
        self.pushButtonSalvaProgetto_2.pressed.connect(self.ScriviDB_Scenario)

        # QObject.connect(self.toolButtonEsegui_2, SIGNAL("clicked()"), self.EseguiScenario)
        self.toolButtonEsegui_2.pressed.connect(self.EseguiScenario)

        # QObject.connect(self.pushButtonView_3, SIGNAL("clicked()"), self.CaricaLayers)
        self.pushButtonView_3.pressed.connect(self.CaricaLayers)

        # QObject.connect(self.pushButtonView_2, SIGNAL("clicked()"), self.VediTabellaDanni)
        self.pushButtonView_2.pressed.connect(self.VediTabellaDanni)

        # QObject.connect(self.pushButtonIstogrammi, SIGNAL("clicked()"), self.istogrammi)
        self.pushButtonIstogrammi.pressed.connect(self.istogrammi)

        self.comboBox_9.currentIndexChanged.connect(self.selectComboScenarioVOD)
        self.comboBox_10.currentIndexChanged.connect(self.selectComboTempoVOD)

        self.radioButton_1.toggled.connect(self.setComboBox)
        self.radioButton_2.toggled.connect(self.setComboBox)

        self.pushButton_SUFRI_Table.pressed.connect(self.Image1)
        # QObject.connect(self.buttonBox, SIGNAL(_fromUtf8("helpRequested()")), self.show_help)
        self.buttonBox.helpRequested.connect(self.show_help)

        self.DirDefault = __file__
        # self.comboBox_7.clear()

    #------------- Actions -----------------------

    def show_help(self):
        """Load the help text into the system browser."""
        show_context_help(context='include4')


    def selectComboScenario(self):                                       # Seleziono il combo e carico il DB
        self.NomeFileSQLITE = str(self.txtShellFilePath_2.text())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('mod_spatialite')")
        cursor = conn.execute("SELECT Numscenario, HazardInstance, ExposureInstance, FRType, Understanding, Description from POPSCENARIOS")

        for row in cursor:
            self.p1= str(row[0])                                        # Numscenario
            self.p2= str(self.comboBox_3.currentText())

            if self.p1 == self.p2:
                self.s2 = str(row[1])                                   # HazardInstance
                self.s3 = str(row[2])                                   # ExposureInstance
                self.s4 = str(row[3])                                   # FRType
                self.s5 =  str(row[4])                                  # Understanding
                self.s6 =  str(row[5])                                  # Descrizione
                self.lineEdit.setText(self.s6)                          # Carico la descrizione nel TextBox 'Scenario'

                # -------------------- set ComboBox HazardInstance ----------------------
                nC =  self.comboBox_6.count()
                I = -1

                for ID in range(0,nC):
                    self.p3 = self.comboBox_6.itemText(ID)
                    I = I + 1

                    if self.s2 == self.p3:
                        self.comboBox_6.setCurrentIndex(int(I))
                        break

                # -------------------- set ComboBox ExposureInstance ----------------------
                nC = self.comboBox_8.count()
                I = -1

                for ID in range(0,nC):
                    self.p3 = self.comboBox_8.itemText(ID)
                    I = I + 1

                    if self.s3 == self.p3:
                        self.comboBox_8.setCurrentIndex(int(I))
                        break

                # -------------------- set RadioButton Vulnerabilty ----------------------
                if self.s4 == "1":
                    self.radioButton_1.setChecked(True)
                else:
                    self.radioButton_2.setChecked(True)

                # -------------------- set ComboBox Understanding (1) ----------------------
                if self.s5 == "Vague":
                    self.comboBox.setCurrentIndex(0)
                else:
                    self.comboBox.setCurrentIndex(1)

                # -------------------- set ComboBox Understanding (2) ----------------------
                nC = self.comboBox_2.count()
                I = -1

                for ID in range(0,nC):
                    self.p3 = self.comboBox_2.itemText(ID)
                    I = I + 1

                    if self.s5 == self.p3:
                        self.comboBox_2.setCurrentIndex(int(I))
                        break

                # -------------------- set ComboBox Understanding (ENABLED) ----------------------
                self.setComboBox()

                # -------------------- set ComboBox Scenario VOD ----------------------
                II = self.comboBox_3.currentIndex()
                self.comboBox_9.setCurrentIndex(II)

        conn.commit()
        conn.close()


    def setComboBox(self):                                                  #
        if self.radioButton_1.isChecked():
            self.comboBox.setEnabled(True)
            self.comboBox_2.setDisabled(True)
        elif self.radioButton_2.isChecked():
            self.comboBox.setDisabled(True)
            self.comboBox_2.setEnabled(True)


    def ScriviDB_Scenario(self):                                            # Scrivo il nella tabella 'POPSCENARIOS' del DB
        # numero dello scenario
        self.s1 = str(self.comboBox_3.currentText())
        # descrizione dello scenario
        self.s2 = str(self.lineEdit.text())
        # Hazard Instance
        self.s3 = str(self.comboBox_6.currentText())
        # Exposure Instance
        self.s4 = str(self.comboBox_8.currentText())

        if self.radioButton_1.isChecked():
            self.s5 = 1
            # Understanding
            self.s6 = str(self.comboBox.currentText())
        elif self.radioButton_2.isChecked():
            self.s5 = 2
            # Understanding
            self.s6 = str(self.comboBox_2.currentText())

        if self.s1 !="":
            self.NomeFileSQLITE = str(self.txtShellFilePath_2.text())
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.enable_load_extension(True)
            conn.execute("SELECT load_extension('mod_spatialite')")
            cur = conn.cursor()
            sql = "SELECT OBJECTID FROM POPSCENARIOS WHERE Numscenario=%s OR (HazardInstance=%s AND ExposureInstance=%s AND FRType=%s AND Understanding='%s'); " % (self.s1, self.s3, self.s4, self.s5, self.s6)
            cur = conn.execute(sql)
            ListOBJ = cur.fetchone()

            if ListOBJ != None:
                quit_msg = self.tr("This record already exists, do you want to overwrite it?")
                reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    sql = "UPDATE POPSCENARIOS SET Numscenario = %s, HazardInstance = %s, ExposureInstance = %s, FRType = %s, Understanding = '%s', Description = '%s' WHERE OBJECTID=%d;" % (self.s1, self.s3, self.s4, self.s5, self.s6, self.s2, ListOBJ[0])
                    cur.execute(sql)
            else:
                sql = "INSERT INTO POPSCENARIOS (Numscenario, HazardInstance, ExposureInstance, FRType, Understanding, Description) VALUES (%s,%s,%s,%s,'%s','%s'); "  %  (self.s1, self.s3, self.s4, self.s5, self.s6, self.s2)
                cur.execute(sql)
                self.comboBox_3.addItem(self.s1)                            # Combo Scenario
                self.comboBox_9.addItem(self.s1)                            # Combo Scenario VOD

        conn.commit()
        conn.close()


    def EseguiScenario(self):                                               # Eseguo lo scenario corrente
        # leggo il path del database
        self.NomeFileSQLITE = str(self.txtShellFilePath_2.text())

        # creo un oggetto unicode : esso ha il metodo isnumeric() per verificare se e' un numero
        ScenarioUnicode =u'%s' % self.comboBox_3.currentText()

        # controllo se esiste il database e se nel combo dello scenario c'e' un numero
        if os.path.exists(self.NomeFileSQLITE) and ScenarioUnicode.isnumeric():

            CurrentScenarioInt=int(ScenarioUnicode)
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.enable_load_extension(True)
            conn.execute("SELECT load_extension('mod_spatialite')")
            cur =  conn.cursor()

            # seleziono dal database i dati dello scenario
            sql='SELECT HazardInstance, ExposureInstance, FRType, Understanding FROM POPSCENARIOS WHERE Numscenario=%d' % CurrentScenarioInt
            cur.execute(sql)
            record=cur.fetchone()

            # se lo scenario esiste nel database
            if record!=None:
                HazardInstance=record[0]
                ExposureInstance=record[1]
                FRType=record[2]
                Understanding=record[3]

                # crea la lista degli input per lo script che calcola lo scenario
                InputList=[]
                # primo dato il path del geodatabase
                InputList.append(self.NomeFileSQLITE)
                # secondo dato NumeroScenario
                InputList.append(CurrentScenarioInt)
                # terzo dato HazardInstance
                InputList.append(HazardInstance)
                # quarto dato HazardInstance
                InputList.append(ExposureInstance)
                # quinto dato FRType
                InputList.append(FRType)
                # sesto dato Understanding
                InputList.append(Understanding)

                # lo script di calcolo restituisce
                # NotErr: flag che indica se e' stato completato o no il calcolo
                # errMsg: messaggio di errore
                # TotalDamageDic: dizionario con il danno totale per ogni tempo di ritorno

                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                NotErr, errMsg, TotalDamageDic = mainCalcolaRischio(InputList,self.progressBar)
                QApplication.restoreOverrideCursor()

                if NotErr:
                    # salvo i risultati nella tabella FreqDamage del database
                    for tr in TotalDamageDic:
                        # controllo se esiste gia il dato
                        sql='SELECT OBJECTID FROM FreqNumLOL WHERE Numscenario=%d AND YearReturnPeriod=%d;' % (CurrentScenarioInt,tr)
                        cur.execute(sql)
                        ListOBJ=cur.fetchone()
                        self.setPriority()

                        if ListOBJ!=None:
                            # update
                            sql = "UPDATE FreqNumLOL SET LOL = %s WHERE OBJECTID=%d;" % (TotalDamageDic[tr],ListOBJ[0])
                            cur.execute(sql)
                        else:
                            # append
                            sql = "INSERT INTO FreqNumLOL (Numscenario, YearReturnPeriod, LOL) VALUES (%d,%d,%s); "  %  (CurrentScenarioInt,tr,TotalDamageDic[tr])
                            cur.execute(sql)
                    # salvo
                    conn.commit()

                    msg=self.tr('End of Job')
                    QMessageBox.information(None, "FloodRisk_2", msg)

                else:
                    msg=errMsg + " - " + self.tr("Run not executed")
                    QMessageBox.information(None, "Run", msg)


            conn.close()


    def selectComboScenarioVOD(self):                                   # Seleziono il combo e carico il DB
        self.VisualizaPath()


    def selectComboTempoVOD(self):                                      # Seleziono il combo e carico il DB
        self.VisualizaPath()


    def VisualizaPath(self):
        self.NomeFileSQLITE =  str(self.txtShellFilePath_2.text())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('mod_spatialite')")
        cursor = conn.execute("SELECT Numscenario, YearReturnPeriod, Type, Path from OUTPUTFiles")

        for row in cursor:
            p1= row[0]                                                  # Numscenario
            p2= row[1]                                                  # YearReturnPeriod
            p3= row[2]                                                  # Type
            p4= row[3]                                                  # Path
            E1= str(self.comboBox_9.currentText())                      # Set SCENARIO
            E2= str(self.comboBox_10.currentText())                     # Set Flood Return Period

            if E1 == "" or E2 == "":
                return

            if p1 == int(E1) and p2 == int(E2):
                if p3 == 4 :
                    self.txtShellFilePath_4.setText(str(p4))            # Popolation
                elif p3 == 5 :
                    self.txtShellFilePath_7.setText(str(p4))            # Global Summary Table

        conn.close()

    def CaricaLayers(self):
        #filePath=str(self.txtShellFilePath_2.text())

        #if os.path.exists(filePath):
         # case geodatabase
        #    tabelle=['StructurePoly','InfrastrLines','CensusBlocks']

        #    for nomelayer in tabelle:
        #        if not LayerCaricato(self,nomelayer):
        #            openFile(self,filePath,nomelayer)

        filePath=str(self.txtShellFilePath_4.text())

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')


    def istogrammi(self):
        self.NomeFile=str(self.txtShellFilePath_7.text())

        if os.path.exists(self.NomeFile):
            try:
                import matplotlib
                import matplotlib.patches as mpatches
                self.sep = check_csv_separator(self.NomeFile)

                # Reading csv file
                finp = open(self.NomeFile)
                csv_reader = csv.reader(finp, delimiter=self.sep, quotechar='"')

                #headers = csv_reader.next()
                headers = csv_reader.__next__()

                self.fields=[]

                for p in headers:
                    self.fields.append(p)

                progress = unicode('Reading data ') # As a progress bar is used the main window's status bar, because the own one is not initialized yet
                yEuro1=[]
                yEuro2=[]
                xCodice=[]

                for record in csv_reader:
                    for i in range(len(record)):
                        if i == 0:
                            xCodice += [record[i]]
                        if i == 4:
                            yEuro2 += [float(record[i])]
                        if i == 5:
                            yEuro1 += [float(record[i])]

                finp.close()

                #---------------Draw Chart-----------------
                y1=yEuro1
                y2=yEuro2
                x1=xCodice
                width=0.3
                i=arange(len(y1))
                r1=bar(i, y1,width, color='r',linewidth=1)
                r2=bar(i+width,y2,width,color='b',linewidth=1)
                xticks(i+width/2,x1)
                xlabel(self.tr('Range water depth (m)')); ylabel(self.tr('Number people')); title(self.tr('Consequences for the population'))

                try:
                    plt.legend((r1[0],r2[0]),(self.tr('Loss of Life'), self.tr('Total Polpulation at Risk')))
                except:
                    pass

                grid()
                show()
            except:
                QMessageBox.information(None, "Warning", "The current version of QGIS does not allow import matplotlib")

        else:
            txt1=self.tr('Warning the file')
            txt2=self.tr('does not exists')
            msg='%s\n\n %s\n\n %s' % (txt1,self.NomeFile,txt2)
            QMessageBox.information(None, "Input", msg)


    def VediTabellaDanni(self):
        self.NomeTabella=str(self.txtShellFilePath_7.text())
        self.TabView = TableViewer(self.iface,self.NomeTabella)
        self.TabView.show()# show the dialog
        result = self.TabView.exec_()


    def setPriority(self,pid=None,priority=1):
        """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
            2 is normal priority.  Default sets the priority of the current
            python process but can take any valid process ID. """

        import win32api,win32process,win32con

        priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                           win32process.BELOW_NORMAL_PRIORITY_CLASS,
                           win32process.NORMAL_PRIORITY_CLASS,
                           win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                           win32process.HIGH_PRIORITY_CLASS,
                           win32process.REALTIME_PRIORITY_CLASS]

        if pid == None:
            pid = win32api.GetCurrentProcessId()

        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, priorityclasses[priority])

    def Image1(self):
        from .Image1_gui import Image1
        self.Image1 = Image1(self.iface)
        self.Image1.show()
