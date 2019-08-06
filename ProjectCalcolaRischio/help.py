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

import os
import logging
import locale

from .FloodRiskExceptions import HelpFileMissingError

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSettings

LOGGER = logging.getLogger('FloodRisk')


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
        __file__, os.path.pardir,os.path.pardir,'docs' ))

    # set default value for loclang
    loclang = 'en'
    if 'LANG' in os.environ:
        loclang = os.environ['LANG']
    else:
        try:
            loclang = QSettings().value('locale/userLocale')[0:2]
        except:
            pass

    if loclang not in ['it', 'en']:
        loclang = 'en'

    base_url = os.path.join(base_url, loclang)

    if context is not None:
        base_url = os.path.join(base_url, context + '.html')
        LOGGER.debug(os.path.isfile(base_url))
    else:
        base_url = os.path.join(base_url, 'index.html')

    if not os.path.exists(base_url):
        raise HelpFileMissingError('Help file not found: %s' % base_url)

    print ('help')
    # noinspection PyTypeChecker,PyArgumentList
    url = QtCore.QUrl.fromLocalFile(base_url)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    QtGui.QDesktopServices.openUrl(url)


def _show_online_help(context=None):
    """Show help using the user's web browser - uses inasafe web site.

    :type context: str
    :param context: Page name (without path) of a document in the
       user-docs subdirectory. e.g. 'keywords'
    """

    # First we try using local filesystem

    base_url = 'http://floodRisk.org/'

    # set default value for loclang
    loclang = 'en'
    if 'LANG' in os.environ:
        loclang = os.environ['LANG']
    else:
        try:
            loc=locale.getdefaultlocale()[0]
            loclang=loc.split('_')[0]
        except:
            pass

    if loclang not in ['it', 'en']:
        loclang = 'en'

    base_url += loclang
    base_url += '/user-docs/'

    if context is not None:
        base_url += context + '.html'
        LOGGER.debug(os.path.isfile(base_url))
    else:
        base_url += 'index.html'
    url = QtCore.QUrl(base_url)
##    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
##    QtGui.QDesktopServices.openUrl(url)
