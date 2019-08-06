# coding=utf-8
"""
/***************************************************************************
 Help
                              -------------------
        begin                : 2015-03-19
        copyright            : (C) 2014 by RSE
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
import locale
import logging

from .FloodRiskExceptions import HelpFileMissingError

LOGGER = logging.getLogger('FloodRisk2')


def show_context_help(context=None):
    """Show help using the user's web browser.

    :type context: str
    :param context: Page name (without path) of a document in the
       user-docs subdirectory. e.g. 'keywords'
    """

    try:
        _show_local_help(context)
    except HelpFileMissingError:
        _show_online_help(context)


def _show_local_help(context=None):
    """Show help using the user's web browser - uses local help file.

    :type context: str
    :param context: Page name (without path) of a document in the
       user-docs subdirectory. e.g. 'keywords'

    :raises: HelpFileMissingError
    """

    # First we try using local filesystem
    base_url = os.path.abspath(os.path.join(
        __file__, os.path.pardir,'docs' ))

    # set default value for locale
    locale = 'en'

    if 'LANG' in os.environ:
        locale = os.environ['LANG']
    else:
        try:
            locale = QSettings().value('locale/userLocale')[0:2]
        except:
            pass

    if locale not in ['it', 'en']:
        locale = 'en'

    base_url = os.path.join(base_url, locale)

    if context is not None:
        base_url = os.path.join(base_url, context + '.html')
        LOGGER.debug(os.path.isfile(base_url))
    else:
        base_url = os.path.join(base_url, 'index.html')

    if not os.path.exists(base_url):
        HelpFileMissingError('Help file not found: %s' % base_url)

    print ('help')
    # noinspection PyTypeChecker,PyArgumentList
    # url = QtCore.QUrl.fromLocalFile(base_url)
    url = QUrl.fromLocalFile(base_url)

    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    QDesktopServices.openUrl(url)


def _show_online_help(context=None):
    """Show help using the user's web browser - uses inasafe web site.

    :type context: str
    :param context: Page name (without path) of a document in the
       user-docs subdirectory. e.g. 'keywords'
    """

    # First we try using local filesystem

    base_url = 'http://floodRisk.org/'

    # set default value for locale
    locale = 'en'

    if 'LANG' in os.environ:
        locale = os.environ['LANG']

    if locale not in ['it', 'en']:
        locale = 'en'

    base_url += locale
    base_url += '/user-docs/'

    if context is not None:
        base_url += context + '.html'
        LOGGER.debug(os.path.isfile(base_url))
    else:
        base_url += 'index.html'

    # url = QtCore.QUrl(base_url)
    url = QUrl(base_url)

