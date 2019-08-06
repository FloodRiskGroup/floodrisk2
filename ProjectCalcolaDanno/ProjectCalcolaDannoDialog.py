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
# ============================================================================================

# from ui_calcolodanno import Ui_FloodRisk
# import CalcoloDannoInondazione

from xml.dom import minidom
from xml.dom.minidom import Document
from .tableViewer_gui import TableViewer

try:
    from pylab import *
except:
    pass

# to reading cvs file
import csv
import locale

#import CreaGeodatabase
#import CaricaGeodatiFloodRisk
#import CaricaCurve

# from qgis.gui import QgsGenericProjectionSelector                     # ??????????????????
from time import sleep

import os.path
import os, shutil, subprocess
import string

from .CalcolaScenarioDanno import mainScenarioDanno                     # import dello script per il calcolo dello scenario
from .help import show_context_help

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
        #We should never really get here, but just in case.
        pass


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ProjectCalcolaDannoDialog_base.ui'))

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
            # headers = reader.next()
            headers = reader.__next__()
            numheaders=len(headers)

            if numheaders>1:
                # row = reader.next()
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

#---------------------- Compilazione file.ui ----------------------------

#FORM_CLASS, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'ui_graficofloodrisk.ui'))

#class CalcolaDanno_Dialog(QDialog, FORM_CLASS):
    # def __init__(self, iface, NomeFile, parent=None):
    #     """Constructor."""
    #     super(CalcolaDanno_Dialog, self).__init__(parent)

#-------------------------------------------------------------------------

class CalcolaDanno_Dialog(QDialog, FORM_CLASS):
    def __init__(self,iface, parent=None):
        """Constructor."""
        super(CalcolaDanno_Dialog, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface=iface

        # initialize actions
        self.comboBox_7.currentIndexChanged.connect(self.selectComboScenario)
        self.comboBox_9.currentIndexChanged.connect(self.selectComboScenarioVOD)
        self.comboBox_10.currentIndexChanged.connect(self.selectComboTempoVOD)

        # QObject.connect(self.pushButtonSalvaProgetto_2, SIGNAL("clicked()"), self.ScriviDB_Scenario)
        self.pushButtonSalvaProgetto_2.pressed.connect(self.ScriviDB_Scenario)

        # QObject.connect(self.toolButtonEsegui, SIGNAL("clicked()"), self.EseguiScenario)
        self.toolButtonEsegui.pressed.connect(self.EseguiScenario)

        # QObject.connect(self.buttonGrafici, SIGNAL("clicked()"), self.EseguiGrafico)
        self.buttonGrafici.pressed.connect(self.EseguiGrafico)

        # QObject.connect(self.pushButtonLoadLayer, SIGNAL("clicked()"), self.CaricaLayers)
        self.pushButtonLoadLayer.pressed.connect(self.CaricaLayers)

        # QObject.connect(self.pushButtonView, SIGNAL("clicked()"), self.VediTabellaDanni)
        self.pushButtonView.pressed.connect(self.VediTabellaDanni)

        # QObject.connect(self.pushButton, SIGNAL("clicked()"), self.istogrammi)
        self.pushButton.pressed.connect(self.istogrammi)

        self.dic_TypeId={}
        self.CurveType=''
        self.TotalDamage=0.0

        # help
        # QObject.connect(self.buttonBox, SIGNAL(_fromUtf8("helpRequested()")), self.show_help)
        self.buttonBox.helpRequested.connect(self.show_help)

        self.DirDefault = __file__
        self.comboBox_7.clear()

    #------------- Actions -----------------------

    def show_help(self):
        """Load the help text into the system browser."""
        show_context_help(context='include3')

    def selectComboScenario(self):                                       # Seleziono il combo e carico il DB
        self.NomeFileSQLITE =  str(self.txtShellFilePath_2.text())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = conn.execute("SELECT Numscenario, HazardInstance, ExposureInstance, VulnID, Description from DAMAGESCENARIOS")

        for row in cursor:
            self.p1= str(row[0])                                        # Numscenario
            self.p2= str(self.comboBox_7.currentText())

            if self.p1 == self.p2:
                self.s2 = str(row[1])                                   # HazardInstance
                self.s3 = str(row[2])                                   # ExposureInstance
                self.s4 = str(row[3])                                   # VulnID
                self.s5 =  str(row[4])                                  # Descrizione
                self.lineEdit.setText(self.s5)                          # Carico la descrizione nel TextBox 'Scenario'

                # -------------------- set ComboBox HazardInstance ----------------------
                self.nC =  self.comboBox_6.count()
                self.I = -1

                for self.ID in range(0,self.nC):
                    self.p3 = self.comboBox_6.itemText(self.ID)
                    self.I = self.I + 1

                    if self.s2 == self.p3:
                        self.comboBox_6.setCurrentIndex(int(self.I))
                        break

                # -------------------- set ComboBox ExposureInstance ----------------------
                self.nC = self.comboBox_8.count()
                self.I = -1

                for self.ID in range(0,self.nC):
                    self.p3 = self.comboBox_8.itemText(self.ID)
                    self.I = self.I + 1

                    if self.s3 == self.p3:
                        self.comboBox_8.setCurrentIndex(int(self.I))
                        break

                # -------------------- set ComboBox VulnID ----------------------
                self.nC = self.comboBoxGrafici.count()
                self.I = -1

                for self.ID in range(0,self.nC):
                    self.p3 = self.comboBoxGrafici.itemText(self.ID)
                    nn = str.find(self.p3, " - ")                      # Cerco la posizione del numero nella stringa
                    nn = self.p3[0:nn]                                  # Memorizzo solo il numero
                    self.I = self.I + 1

                    if self.s4 == nn:
                        self.comboBoxGrafici.setCurrentIndex(int(self.I))
                        break

        II = self.comboBox_7.currentIndex()
        self.comboBox_9.setCurrentIndex(II)

        conn.close()

    def selectComboScenarioVOD(self):                                   # Seleziono il combo e carico il DB
        self.VisualizaPath()


    def selectComboTempoVOD(self):                                      # Seleziono il combo e carico il DB
        self.VisualizaPath()


    def ScriviDB_Scenario(self):                                        # Scrivo il nella tabella 'DAMAGESCENARIOS' del DB
        self.s1 = str(self.comboBox_7.currentText())
        self.s2 = str(self.lineEdit.text())
        self.s3 = str(self.comboBox_6.currentText())
        self.s4 = str(self.comboBox_8.currentText())
        self.s5 = str(self.comboBoxGrafici.currentText())
        self.s6 = self.ProcessaStringaVuln(self.s5)

        if self.s1 !="":
            self.NomeFileSQLITE = str(self.txtShellFilePath_2.text())
            self.conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            self.cur = self.conn.cursor()
            sql = "SELECT OBJECTID FROM DAMAGESCENARIOS WHERE Numscenario=%s OR (HazardInstance=%s AND ExposureInstance=%s AND VulnID=%s); " % (self.s1, self.s3, self.s4, self.s6)
            self.cur = self.conn.execute(sql)
            ListOBJ = self.cur.fetchone()

            if ListOBJ != None:
                quit_msg = self.tr("This record already exists, do you want to overwrite it?")
                reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    sql = "UPDATE DAMAGESCENARIOS SET Numscenario = %s, HazardInstance = %s, ExposureInstance = %s, VulnID = %s, Description = '%s' WHERE OBJECTID=%d;" % (self.s1, self.s3, self.s4, self.s6, self.s2,ListOBJ[0])
                    self.cur.execute(sql)

                    sql = "DELETE FROM FreqDamage WHERE Numscenario = %s" % (self.s1)
                    self.cur.execute(sql)
            else:
                sql = "INSERT INTO DAMAGESCENARIOS (Numscenario, HazardInstance, ExposureInstance, VulnID, Description) VALUES (%s,%s,%s,%s,'%s'); "  %  (self.s1, self.s3, self.s4, self.s6, self.s2)
                self.cur.execute(sql)
                self.comboBox_7.addItem(self.s1)                        # Combo Scenario
                self.comboBox_9.addItem(self.s1)                        # Combo Scenario VOD


        self.conn.commit()
        self.conn.close()
        self.txtShellFilePath_5.setText("")
        self.txtShellFilePath_6.setText("")
        self.txtShellFilePath_7.setText("")

    def ProcessaStringaVuln(self,sStringa):                             # Tolgo il numero dalla stringa
        a1 = sStringa.find(' - ')
        a2 = str(sStringa[0:a1])
        return a2

    def EseguiScenario(self):                                           # Eseguo lo scenario corrente
        # leggo il path del database
        self.NomeFileSQLITE = str(self.txtShellFilePath_2.text())

        # creo un oggetto unicode : esso ha il metodo isnumeric() per verificare se e' un numero
        ScenarioUnicode =u'%s' % self.comboBox_7.currentText()

        # controllo se esiste il database e se nel combo dello scenario c'e' un numero
        if os.path.exists(self.NomeFileSQLITE) and ScenarioUnicode.isnumeric():
            CurrentScenarioInt=int(ScenarioUnicode)
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            cur =  conn.cursor()

            # seleziono dal database i dati dello scenario
            sql='SELECT HazardInstance,ExposureInstance,VulnID FROM DAMAGESCENARIOS WHERE Numscenario=%d' % CurrentScenarioInt
            cur.execute(sql)
            record=cur.fetchone()

            # se lo scenario esiste nel database
            if record!=None:
                HazardInstance=record[0]
                ExposureInstance=record[1]
                VulnID=record[2]

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

                # quinto dato VulnID
                InputList.append(VulnID)

                # lo script di calcolo restituisce
                # NotErr: flag che indica se e' stato completato o no il calcolo
                # errMsg: messaggio di errore
                # TotalDamageDic: dizionario con il danno totale per ogni tempo di ritorno

                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                NotErr, errMsg, TotalDamageDic = mainScenarioDanno(InputList,self.progressBar)
                QApplication.restoreOverrideCursor()

                if NotErr:
                    # salvo i risultati nella tabella FreqDamage del database
                    for tr in TotalDamageDic:
                        # controllo se esiste gia il dato
                        sql='SELECT OBJECTID FROM FreqDamage WHERE Numscenario=%d AND YearReturnPeriod=%d;' % (CurrentScenarioInt,tr)
                        cur.execute(sql)
                        ListOBJ=cur.fetchone()
                        self.setPriority()

                        if ListOBJ!=None:
                            # update
                            sql = "UPDATE FreqDamage SET DAMAGE = %s WHERE OBJECTID=%d;" % (TotalDamageDic[tr],ListOBJ[0])
                            cur.execute(sql)
                        else:
                            # append
                            sql = "INSERT INTO FreqDamage (Numscenario, YearReturnPeriod, DAMAGE) VALUES (%d,%d,%s); "  %  (CurrentScenarioInt,tr,TotalDamageDic[tr])
                            cur.execute(sql)

                    conn.commit()                                       # salvo

                    msg=self.tr('End of Job')
                    QMessageBox.information(None, "FloodRisk_2", msg)

                else:
                    msg=errMsg + " - " + self.tr("Run not executed")
                    QMessageBox.information(None, "Run", msg)

            conn.close()
            self.VisualizaPath()


    def VisualizaPath(self):
        self.NomeFileSQLITE =  str(self.txtShellFilePath_2.text())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
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
                if p3 == 1 :
                    self.txtShellFilePath_5.setText(str(p4))            # Economic Damage Layer
                elif p3 == 2 :
                    self.txtShellFilePath_6.setText(str(p4))            # Vulnerability Layer
                elif p3 == 3 :
                    self.txtShellFilePath_7.setText(str(p4))            # Global Summary Table

        conn.close()

    def CaricaLayers(self):
        #filePath=str(self.txtShellFilePath_7.text())

        #if os.path.exists(filePath):
         # case geodatabase
        #    tabelle=['StructurePoly','InfrastrLines','CensusBlocks']

        #    for nomelayer in tabelle:
        #        if not LayerCaricato(self,nomelayer):
        #            openFile(self,filePath,nomelayer)

        filePath=str(self.txtShellFilePath_5.text())

        if os.path.exists(filePath):
            if not LayerCaricato(self,filePath):
                openFile(self,filePath,'')

        filePath=str(self.txtShellFilePath_6.text())

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
                xlabel('Code'); ylabel('Euro'); title(self.tr('Damage assessment results'))

                try:
                    legend((r1[0],r2[0]),(self.tr('Content Damage'), self.tr('Structure Damage')))
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
        self.TabView.show()                                                 # show the dialog
        result = self.TabView.exec_()


    def EseguiGrafico(self):
        self.setListaTipoCurvaVuln()
        a1 = str(self.comboBoxGrafici.currentText())
        a2 = a1.find(' - ')
        a3 = str(a1[a2 + 3 : len(a1)])
        tipo= a3

        #try:
        self.idTipo = self.dic_TypeId[tipo]
        from .graficofloodriskdialog import graficofloodriskDialog
        gfd=graficofloodriskDialog(self.iface, self.idTipo, tipo)
        geoDataBase=str(self.txtShellFilePath_2.text())

        if geoDataBase!="":
            gfd.lineEdit.setText(geoDataBase)
            gfd.run()

        #except:
        #    txt0='Geodatabase: %s \n\n' % self.txtShellFilePath_2.text()
        #    txt1=self.tr("Error in table Vulnerability")
        #    msg='%s %s' % (txt0,txt1)
        #    QMessageBox.information(None, "Graph", msg)


    def setListaTipoCurvaVuln(self):
        FileGDB = str(self.txtShellFilePath_2.text())

        if FileGDB != "":
            if self.CheckGeodatabase():
                conn = sqlite3.connect(FileGDB)
                cursor = conn.cursor()
                sql='SELECT VulnID FROM Vulnerability GROUP BY VulnID'
                cursor.execute(sql)
                ListaTipi1 = cursor.fetchall()
                ListaTipi = []

                for row in ListaTipi1:
                    ListaTipi.append(int(row[0]))

                dic_VulnType={}
                self.dic_TypeId={}
                sql='SELECT * FROM VulnType'
                cursor.execute(sql)
                ListaDescription = cursor.fetchall()

                if len(ListaDescription)>0:
                    for row in ListaDescription:
                        dic_VulnType[int(row[1])] = str(row[2])
                        self.dic_TypeId[str(row[2])] = int(row[1])

                    # ListaDescrizione=[]

                    # for num in ListaTipi:
                    #     ListaDescrizione.append(dic_VulnType[num])

                    # self.comboBoxGrafici.clear()
                    # self.comboBoxGrafici.addItems(ListaDescrizione)

            else:
                 QMessageBox.information(None, "FloodRisk", self.tr("You must first create the Geodb.Sqlite"))
        else:
             QMessageBox.information(None, "FloodRisk", self.tr("You must first create the Geodb.Sqlite"))


    def CheckGeodatabase(self):
        res=bool()

        if os.path.exists(self.txtShellFilePath_2.text()):
            mydb_path=self.txtShellFilePath_2.text()

            try:
                # connecting the db
                conn = sqlite3.connect(mydb_path)

                # creating a Cursor
                cur = conn.cursor()

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

                res=bool('True')
            except:
                res=bool()
        else:
            res=bool()
        return res

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
