"""
/***************************************************************************
 CalcolaScenarioDanno
                                 A QGIS plugin
 Caricamento GeoDatabase, query sql e grafico
                             -------------------
        begin                : 2017-11-24
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
import sqlite3
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def mainFD(InputList):
    # leggo i dati di input
    NomeFileSQLITE=InputList[0]
    CurrentScenarioInt=InputList[1]
    Labels=InputList[2]
    Label_x= Labels[0]
    Label_y= Labels[1]
    NotErr=bool('True')
    errMsg='OK'

    # per il caricamento dei dati alfanumerici creo la connessione con sqlite3
    conn = sqlite3.connect(NomeFileSQLITE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.enable_load_extension(True)
    conn.execute("SELECT load_extension('mod_spatialite')")
    cur =  conn.cursor()

    # seleziona la curva
    sql='SELECT YearReturnPeriod, DAMAGE FROM FreqDamage WHERE Numscenario=%d ORDER BY YearReturnPeriod;' % (CurrentScenarioInt)
    cur.execute(sql)
    ListaDamages=cur.fetchall()

    if len(ListaDamages)>0:
        font0 = FontProperties()
        alignment = {'horizontalalignment': 'center', 'verticalalignment': 'baseline'}
        families = ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
        font1 = font0.copy()
        sizes = ['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']
        font1.set_size('x-large')
        font2=font0.copy()
        font2.set_size('xx-large')

        font3=font0.copy()
        font3.set_size('medium')

        ListaTR=[]
        DanniScenari=[]

        for row in ListaDamages:
            ListaTR.append(row[0])
            DanniScenari.append(row[1])

        # grafico la curva F-D
        plt.subplot(1, 1, 1)
        P=[]
        Ytik=[]

        for Tr in ListaTR:
            txt='1/%d' % Tr
            Ytik.append(txt)
            P.append(1.0/float(Tr))

        txt='Scenario %d' % CurrentScenarioInt
        plt.semilogy(DanniScenari, P,".-",label=txt )
        plt.yticks(P,Ytik, fontproperties=font3)
        plt.xticks(fontproperties=font1)
        plt.grid(True)
        plt.title('CURVE F-D', fontproperties=font2)
##        plt.xlabel('Damage (Euro)', fontproperties=font1)
##        plt.ylabel('Annual Exceedance Probability (AEP)', fontproperties=font1)
        plt.xlabel(Label_x, fontproperties=font1)
        plt.ylabel(Label_y, fontproperties=font1)
        plt.legend(loc='upper right')
        plt.show()

    return NotErr, errMsg

if __name__ == '__main__':
    main()
