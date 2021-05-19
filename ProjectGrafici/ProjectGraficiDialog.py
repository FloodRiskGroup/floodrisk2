"""
/***************************************************************************
 ProjectGraficiDialog
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
# ============================================================================================

##import CreaGeodatabase

# import Graph_curve_FD
from .Graph_curve_FD import mainFD

# import Graph_curve_FN
from .Graph_curve_FN import mainFN

# import Graph_curve_ED
from .Graph_curve_ED import mainED

# import Graph_curve_PD
from .Graph_curve_PD import mainPD

# from qgis.gui import QgsGenericProjectionSelector             # ????????????????
# from pyspatialite import dbapi2 as db
from time import sleep

from .help import show_context_help
from numpy.distutils.fcompiler import none

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ProjectGraficiDialog_base.ui'))

class Grafici_Dialog(QDialog, FORM_CLASS):

    def __init__(self,iface, parent=None):
        """Constructor."""
        super(Grafici_Dialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface=iface

        # initialize actions
        # QObject.connect(self.toolButtonEsegui_2, SIGNAL("clicked()"), self.Graph_curve_FD)
        self.toolButtonEsegui_2.pressed.connect(self.Graph_curve_FD)

        # QObject.connect(self.toolButtonEsegui_3, SIGNAL("clicked()"), self.Graph_curve_FN)
        self.toolButtonEsegui_3.pressed.connect(self.Graph_curve_FN)

        # QObject.connect(self.toolButtonEsegui_4, SIGNAL("clicked()"), self.Graph_curve_ED)
        self.toolButtonEsegui_4.pressed.connect(self.Graph_curve_ED)

        # QObject.connect(self.toolButtonEsegui_6, SIGNAL("clicked()"), self.Graph_curve_PD)
        self.toolButtonEsegui_6.pressed.connect(self.Graph_curve_PD)

        # QObject.connect(self.toolButtonEsegui_5, SIGNAL("clicked()"), self.Calcola_ED)
        self.toolButtonEsegui_5.pressed.connect(self.Calcola_ED)

        # QObject.connect(self.toolButtonEsegui_7, SIGNAL("clicked()"), self.Calcola_PD)
        self.toolButtonEsegui_7.pressed.connect(self.Calcola_PD)

        # QObject.connect(self.pushButtonSalvaProgetto_2, SIGNAL("clicked()"), self.SalvaCostBen1)
        self.pushButtonSalvaProgetto_2.pressed.connect(self.SalvaCostBen1)

        # QObject.connect(self.pushButtonSalvaProgetto_3, SIGNAL("clicked()"), self.SalvaCostBen2)
        self.pushButtonSalvaProgetto_3.pressed.connect(self.SalvaCostBen2)

        self.comboBox_14.currentIndexChanged.connect(self.selectComboDescription1)
        self.comboBox_14.editTextChanged.connect(self.Cancella1)
        self.comboBox_15.currentIndexChanged.connect(self.selectComboDescription2)
        self.comboBox_15.editTextChanged.connect(self.Cancella2)

        help
        # QObject.connect(self.buttonBox, SIGNAL(_fromUtf8("helpRequested()")), self.show_help)
        self.buttonBox.helpRequested.connect(self.show_help)

        self.DirDefault = __file__

    #------------- Actions -----------------------

    def show_help(self):
        """Load the help text into the system browser."""
        show_context_help(context='include2')


    def Graph_curve_FD(self):                                                                       # Grafico FD Economic
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())

        if (self.NomeFileSQLITE == ""):
            QMessageBox.information(None, "FloodRisk_2", self.tr("Load the file DB SQLITE"))
        else:
            InputList=[]
            InputList.append(self.NomeFileSQLITE)
            n= self.comboBox_7.currentText()

            if (n == ""):
                return

            InputList.append(int(n))
            graph_label=[]
            graph_label.append(self.tr("Damage (Euro)"))
            graph_label.append(self.tr("Annual Exceedance Probability (AEP)"))
            InputList.append(graph_label)

            NotErr, errMsg = mainFD(InputList)

            if NotErr:
                pass
            else:
                QMessageBox.information(None, "FloodRisk_2", errMsg)

        # ============================================================================================================
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cur =  conn.cursor()
        CurrentScenarioInt=int(n)
        sql='SELECT YearReturnPeriod, DAMAGE FROM FreqDamage WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
        s = self.CalcolaArea(sql)
        s = format(s)
        self.label_sr_2.setText(s)

        # -------------------------- Salvo ANNUALDAMAGE -----------------------------
        sql = "SELECT OBJECTID FROM DAMAGESCENARIOS WHERE Numscenario=%s; " % (n)
        self.cur = conn.execute(sql)
        ListOBJ = self.cur.fetchone()

        if ListOBJ != None:
            A = self.label_sr_2.text()

            if A == "" or A == 0:
                return

            sql = "UPDATE DAMAGESCENARIOS SET ANNUALDAMAGE = %s WHERE OBJECTID=%d;" % (A, ListOBJ[0])
            self.cur.execute(sql)
            conn.commit()                                                       # Scrivo il DB

        conn.close()                                                            # Chiudo il db

    def show_help(self):
        """Load the help text into the system browser."""
        show_context_help(context='include5')

    def Graph_curve_FN(self):                                                                       # Grafico FN Population
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())

        if (self.NomeFileSQLITE == ""):
            QMessageBox.information(None, "FloodRisk_2", self.tr("Load the file DB SQLITE"))
        else:
            InputList=[]
            InputList.append(self.NomeFileSQLITE)
            n= self.comboBox_11.currentText()

            if (n == ""):
                return

            InputList.append(int(n))
            graph_label=[]
            graph_label.append(self.tr("Number of Loss of Lifes"))
            graph_label.append(self.tr("Annual Exceedance Probability (AEP)"))
            InputList.append(graph_label)
            NotErr, errMsg = mainFN(InputList)

            if NotErr:
                pass
            else:
                QMessageBox.information(None, "FloodRisk_2", errMsg)

        # ============================================================================================================
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cur =  conn.cursor()
        CurrentScenarioInt=int(n)
        sql='SELECT YearReturnPeriod, LOL FROM FreqNumLOL WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
        s = self.CalcolaArea(sql)
        s = format(s)
        self.label_sr_7.setText(s)

        # ----------------------------- Salvo ANNUALLOL ---------------------------------------
        sql = "SELECT OBJECTID FROM POPSCENARIOS WHERE Numscenario=%s; " % (n)
        self.cur = conn.execute(sql)
        ListOBJ = self.cur.fetchone()

        if ListOBJ != None:
            A = self.label_sr_7.text()

            if A == "" or A == 0:
                return

            sql = "UPDATE POPSCENARIOS SET ANNUALLOL = %s WHERE OBJECTID=%d;" % (A, ListOBJ[0])
            self.cur.execute(sql)
            conn.commit()                                                       # Scrivo il DB

        conn.close()                                                            # Chiudo il db


    def Graph_curve_ED(self):                                                                       # Grafico Economic Data
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())

        if (self.NomeFileSQLITE == ""):
            QMessageBox.information(None, "FloodRisk_2", self.tr("Load the file DB SQLITE"))
        else:
            InputList=[]
            InputList.append(self.NomeFileSQLITE)
            n1= self.comboBox_9.currentText()
            n2= self.comboBox_12.currentText()

            if n1 == "" or n2 == "":
                return

            try:
                InputList.append(int(n1))
                InputList.append(int(n2))

                graph_label=[]
                graph_label.append(self.tr("Damage (Euro)"))
                graph_label.append(self.tr("Annual Exceedance Probability (AEP)"))
                InputList.append(graph_label)

                NotErr, errMsg = mainED(InputList)

                if NotErr:
                    pass
                else:
                    QMessageBox.information(None, "FloodRisk_2", errMsg)
            except:
                pass

    def Graph_curve_PD(self):
        # Grafico Popolation Data
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())

        if (self.NomeFileSQLITE == ""):
            QMessageBox.information(None, "FloodRisk_2", self.tr("Load the file DB SQLITE"))
        else:
            InputList=[]
            InputList.append(self.NomeFileSQLITE)
            n1= self.comboBox_10.currentText()
            n2= self.comboBox_13.currentText()

            if n1 == "" or n2 == "":
                return

            try:
                InputList.append(int(n1))
                InputList.append(int(n2))
                graph_label=[]
                graph_label.append(self.tr("Number of Loss of Lifes"))
                graph_label.append(self.tr("Annual Exceedance Probability (AEP)"))
                InputList.append(graph_label)

                NotErr, errMsg = mainPD(InputList)

                if NotErr:
                    pass
                else:
                    QMessageBox.information(None, "FloodRisk_2", errMsg)
            except:
                pass


    def Calcola_ED(self):
        try:
            E1 = self.comboBox_9.currentText()                                                         # Scenario 1 (Economic)
            E2 = self.comboBox_12.currentText()                                                        # Scenario 2 (Economic)

            # ====================== Controllo se la selezione degli scenari e' valida ==============================
            if E1 == E2:
                QMessageBox.information(None,  self.tr("Warning"), self.tr("Check the selections (scenario 1 and 2)"))
                return False

            # ================================= Connetto il database ===============================================
            self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.enable_load_extension(True)
            conn.execute("SELECT load_extension('mod_spatialite')")
            self.cur = conn.cursor()

            # ============================= Calcolo l'area (Economic 1-2) ==========================================
            CurrentScenarioInt=int(self.comboBox_9.currentText())
            sql='SELECT YearReturnPeriod, DAMAGE FROM FreqDamage WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
            AES1 = self.CalcolaArea(sql)

            CurrentScenarioInt=int(self.comboBox_12.currentText())
            sql='SELECT YearReturnPeriod, DAMAGE FROM FreqDamage WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
            AES2 = self.CalcolaArea(sql)

            # ================================= Carico le variabili ===============================================
            if self.lineEdit_1.text() == "" or self.lineEdit_2.text() == "" or self.lineEdit_3.text() == "" or self.lineEdit_4.text() == "":
                return

            E3 = float(self.lineEdit_1.text())                                                          # Intervent Cost
            E4 = float(self.lineEdit_2.text())                                                          # Annual maintenance
            E5Perc = float(self.lineEdit_3.text())                                                      # PercentDiscount Rate
            E5 = float(self.lineEdit_3.text())/100.0                                                    # Discount Rate
            E6 = float(self.lineEdit_4.text())                                                          # Intervent Life
            E7 = float(AES1) - float(AES2)                                                              # Annual Benefit
            E8 = E7*((1.0+E5)**E6-1.0)/E5/(1.0+E5)**E6-E3-E4*((1.0+E5)**E6-1.0)/E5/(1.0+E5)**E6         # NPV (Net Present Value)
            E9 = E7*((1.0+E5)**E6-1.0)/E5/(1.0+E5)**E6/(E3+E4*((1.0+E5)**E6-1.0)/E5/(1.0+E5)**E6)       # Rapporto Benefici/Costi
            E10 = str(self.comboBox_14.currentText())                                                   # Description
            s = '{:0.2f}'.format(float(E8))
            self.label_sr_8.setText("Euro: " + str(s))                                                  # Result
            s = '{:0.2f}'.format(float(E9))
            self.label_sr_9.setText("adim: " + str(s))                                                  # Result
            self.EE1=E1; self.EE2=E2; self.EE3=E3; self.EE4=E4; self.EE5=E5Perc; self.EE6=E6; self.EE7=E7; self.EE8=E8; self.EE9=E9; self.EE10=E10
            return True
        except:
            self.label_sr_8.setText("")                                                                 # Result
            self.label_sr_9.setText("")                                                                 # Result
            return False


    def Calcola_PD(self):
        try:
            P1 = self.comboBox_10.currentText()                                                         # Scenario 1 (Population)
            P2 = self.comboBox_13.currentText()                                                         # Scenario 2 (Population)

            # ====================== Controllo se la selezione degli scenari e' valida ==============================
            if P1 == P2:
                QMessageBox.information(None,  self.tr("Warning"), self.tr("Check the selections (scenario 1 and 2)"))
                return False

            # ================================= Connetto il database ===============================================
            self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())
            conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.enable_load_extension(True)
            conn.execute("SELECT load_extension('mod_spatialite')")
            self.cur = conn.cursor()

            # ============================ Calcolo l'area (Population 1-2) ========================================
            CurrentScenarioInt=int(self.comboBox_10.currentText())
            sql='SELECT YearReturnPeriod, LOL FROM FreqNumLOL WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
            APS1 = self.CalcolaArea(sql)

            CurrentScenarioInt=int(self.comboBox_13.currentText())
            sql='SELECT YearReturnPeriod, LOL FROM FreqNumLOL WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
            APS2 = self.CalcolaArea(sql)

            if self.lineEdit_5.text() == "" or self.lineEdit_6.text() == "" or self.lineEdit_7.text() == "" or self.lineEdit_8.text() == "":
                return

            P3 = float(self.lineEdit_5.text())                                                          # Intervent Cost
            P4 = float(self.lineEdit_6.text())                                                          # Annual maintenance Cost
            P5Perc = float(self.lineEdit_7.text())                                                      # PercentDiscount Rate
            P5 = float(self.lineEdit_7.text())/100.0                                                    # Discount Rate
            P6 = float(self.lineEdit_8.text())                                                          # Intervent Life
            P7 = (P3+P4*((1.0+P5)**P6-1.0)/P5/(1.0+P5)**P6)/P6                                          # Annualised Cost
            P8 = float(APS1) - float(APS2)                                                              # Annual Benefit
            P9 = P7/P8                                                                                  # CSLS
            P10 = str(self.comboBox_15.currentText())                                                   # Description
            s = '{:0.2f}'.format(float(P9))
            self.label_sr_10.setText("Euro: " + str(s))                                                 # Result
            self.PP1=P1; self.PP2=P2; self.PP3=P3; self.PP4=P4; self.PP5=P5Perc; self.PP6=P6; self.PP7=P7; self.PP8=P8; self.PP9=P9; self.PP10=P10
            return True
        except:
            self.label_sr_10.setText("")                                                                # Result
            return False

    def SalvaCostBen1(self):
        # ================================= Connetto il database ===============================================
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())
        self.conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn.enable_load_extension(True)
        self.conn.execute("SELECT load_extension('mod_spatialite')")
        self.cur = self.conn.cursor()

        if self.comboBox_14.currentText() != "" or self.lineEdit_1.text() != "" or self.lineEdit_2.text() != "" or self.lineEdit_3.text() != "" or self.lineEdit_4.text() != "":
            if self.Calcola_ED() == False:
                return

            E1 = self.comboBox_9.currentText()                                                          # Scenario 1
            E2 = self.comboBox_12.currentText()                                                         # Scenario 2

            if (E1 == "" or E2 == ""):
                return

            sql = "SELECT OBJECTID FROM DamageMeasures WHERE IniScenario=%s AND FinScenario=%s; " % (E1, E2)
            self.cur = self.conn.execute(sql)
            ListOBJ = self.cur.fetchone()

            if ListOBJ != None:
                quit_msg = self.tr("This record already exists, do you want to overwrite it?")
                reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    sql = "UPDATE DamageMeasures SET IniScenario = %s, FinScenario = %s, IntervCost = %s, AnnualMaintCost = %s, DiscountRate = %s,InterventLife = %s,AnnualBenefit = %s,NPV = %s,RBC = %s, Description = '%s' WHERE OBJECTID=%d;" % (self.EE1,self.EE2,self.EE3,self.EE4,self.EE5,self.EE6,self.EE7,self.EE8,self.EE9,self.EE10, ListOBJ[0])
                    self.cur.execute(sql)
            else:
                sql = "INSERT INTO DamageMeasures (IniScenario,FinScenario,IntervCost,AnnualMaintCost,DiscountRate,InterventLife,AnnualBenefit,NPV,RBC,Description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s'); "  %  (self.EE1,self.EE2,self.EE3,self.EE4,self.EE5,self.EE6,self.EE7,self.EE8,self.EE9,self.EE10)
                self.cur.execute(sql)

            self.conn.commit()                                                                           # Scrivo nelle tabelle del database

        # ================================ Chiudo la connessione ==============================================
        self.cur.close()
        self.conn.close()


    def SalvaCostBen2(self):
        # ================================= Connetto il database ===============================================
        self.NomeFileSQLITE= str(self.txtShellFilePath_2.text())
        self.conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn.enable_load_extension(True)
        self.conn.execute("SELECT load_extension('mod_spatialite')")
        self.cur = self.conn.cursor()

        if self.comboBox_15.currentText() != "" or self.lineEdit_5.text() != "" or self.lineEdit_6.text() != "" or self.lineEdit_7.text() != "" or self.lineEdit_8.text() != "":
            if self.Calcola_PD()== False:
                return

            P1 = self.comboBox_10.currentText()                                                         # Scenario 1
            P2 = self.comboBox_13.currentText()                                                         # Scenario 2

            if (P1 == "" or P2 == ""):
                return

            sql = "SELECT OBJECTID FROM LOLMeasures WHERE IniScenario=%s AND FinScenario=%s; " % (P1, P2)
            self.cur = self.conn.execute(sql)
            ListOBJ = self.cur.fetchone()

            if ListOBJ != None:
                quit_msg = self.tr("This record already exists, do you want to overwrite it?")
                reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    sql = "UPDATE LOLMeasures SET IniScenario = %s, FinScenario = %s, IntervCost = %s, AnnualMaintCost = %s, DiscountRate = %s,InterventLife = %s,AnnualisedCost = %s,AnnualLifeSaved = %s,CSLS = %s, Description = '%s' WHERE OBJECTID=%d;" % (self.PP1,self.PP2,self.PP3,self.PP4,self.PP5,self.PP6,self.PP7,self.PP8,self.PP9,self.PP10, ListOBJ[0])
                    self.cur.execute(sql)
            else:
                sql = "INSERT INTO LOLMeasures (IniScenario,FinScenario,IntervCost,AnnualMaintCost,DiscountRate,InterventLife,AnnualisedCost,AnnualLifeSaved,CSLS,Description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s'); "  %  (self.PP1,self.PP2,self.PP3,self.PP4,self.PP5,self.PP6,self.PP7,self.PP8,self.PP9,self.PP10)
                self.cur.execute(sql)

            self.conn.commit()                                                                               # Scrivo nelle tabelle del database


        # ================================ Chiudo la connessione ==============================================
        self.cur.close()
        self.conn.close()


    def selectComboDescription1(self):
        self.NomeFileSQLITE = str(self.txtShellFilePath_2.text())
        p= str(self.comboBox_14.currentText())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('mod_spatialite')")
        sql = 'SELECT * FROM DamageMeasures WHERE Description="%s";' % (str(p))
        cur = conn.execute(sql)
        row = cur.fetchone()

        if row != None:
            self.lineEdit_1.setText(str(row[3]))                       # Carico la descrizione nel TextBox
            self.lineEdit_2.setText(str(row[4]))                       # Carico la descrizione nel TextBox
            self.lineEdit_3.setText(str(row[5]))                       # Carico la descrizione nel TextBox
            self.lineEdit_4.setText(str(row[6]))                       # Carico la descrizione nel TextBox
        else:
            return

        # -------------------- set ComboBox Scenario 1 ----------------------
        nC = self.comboBox_9.count()
        s1 = row[1]
        I = -1

        for ID in range(0,nC):
            s2 = int(self.comboBox_9.itemText(ID))
            I = I + 1

            if s1 == s2:
                self.comboBox_9.setCurrentIndex(int(I))
                break

        # -------------------- set ComboBox Scenario 2 ----------------------
        nC = self.comboBox_12.count()
        s1 = row[2]
        I = -1

        for ID in range(0,nC):
            s2 = int(self.comboBox_12.itemText(ID))
            I = I + 1

            if s1 == s2:
                self.comboBox_12.setCurrentIndex(int(I))
                break

        self.Calcola_ED()


    def selectComboDescription2(self):
        self.NomeFileSQLITE =  str(self.txtShellFilePath_2.text())
        p= str(self.comboBox_15.currentText())
        conn = sqlite3.connect(self.NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('mod_spatialite')")
        sql = 'SELECT * FROM LOLMeasures WHERE Description="%s";' % (str(p))
        cur = conn.execute(sql)
        row = cur.fetchone()

        if row != None:
            self.lineEdit_5.setText(str(row[3]))                       # Carico la descrizione nel TextBox
            self.lineEdit_6.setText(str(row[4]))                       # Carico la descrizione nel TextBox
            self.lineEdit_7.setText(str(row[5]))                       # Carico la descrizione nel TextBox
            self.lineEdit_8.setText(str(row[6]))                       # Carico la descrizione nel TextBox
        else:
            return

        # -------------------- set ComboBox Scenario 1 ----------------------
        nC = self.comboBox_10.count()
        s1 = row[1]
        I = -1

        for ID in range(0,nC):
            s2 = int(self.comboBox_10.itemText(ID))
            I = I + 1

            if s1 == s2:
                self.comboBox_10.setCurrentIndex(int(I))
                break

        # -------------------- set ComboBox Scenario 2 ----------------------
        nC = self.comboBox_13.count()
        s1 = row[2]
        I = -1

        for ID in range(0,nC):
            s2 = int(self.comboBox_13.itemText(ID))
            I = I + 1

            if s1 == s2:
                self.comboBox_13.setCurrentIndex(int(I))
                break

        self.Calcola_PD()


    def Cancella1(self):
        self.lineEdit_1.setText("")
        self.lineEdit_2.setText("")
        self.lineEdit_3.setText("")
        self.lineEdit_4.setText("")

    def Cancella2(self):
        self.lineEdit_5.setText("")
        self.lineEdit_6.setText("")
        self.lineEdit_7.setText("")
        self.lineEdit_8.setText("")

    def CalcolaArea(self, sql):
        self.cur.execute(sql)
        ListaDati = self.cur.fetchall()

        if len(ListaDati)>0:
            TR=[]
            DS=[]
            P=[]
            n=0

            for row in ListaDati:
                TR.append(row[0])                   # Campo ...
                DS.append(row[1])                   # Campo ...
                n1 = float(row[0])
#                n2 = 1 / n1 * 100                   # Calcolo la Percentuale
                n2 = 1 / n1                         # Calcolo la probabilita'
                P.append(n2)                        # Inserisco nella lista la Percentuale
                n = n + 1                           # Incremento il contatore

            # A=[]
            n3 = 0

            for i in range(1, n):
                DD = DS[i] + DS[i-1]
                PP = P[i-1] - P[i]
                # n3 = DD / 2 * PP
                # A.append(n3)                       # Area singola
                n3 = n3 + DD / 2 * PP               # Area totale

            return str(n3)
