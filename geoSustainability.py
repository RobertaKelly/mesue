# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name			 	 : Vector geoMCDA
Description          :
Date                 :
copyright            : (C) 2010 by Gianluca Massei
email                : g_massa@libero.it

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
from __future__ import absolute_import
from builtins import object

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QMenu, QAction
from qgis.core import QgsMapLayer
# Initialize Qt resources from file resources.py
from . import resources
import os
import webbrowser

import numpy as np





class geoSustainability:
	def __init__(self, iface):
		self.iface = iface	# salviamo il riferimento all'interfaccia di QGis

	def initGui(self):	# aggiunge alla GUI di QGis i pulsanti per richiamare il plugin
		# creiamo l'azione che lancerà il plugin
		self.actionSUST = QAction(QIcon(":/plugins/ssam/icon.png"), "MESUE - Modelo de Sustentabilidad Urbana Espacial", self.iface.mainWindow())
		self.actionSUST.triggered.connect(self.runSUIT)
		self.iface.addToolBarIcon(self.actionSUST)
		self.iface.addPluginToMenu( "&MESUE ",self.actionSUST )

	def unload(self):	# rimuove dalla GUI i pulsanti aggiunti dal plugin
		self.iface.removePluginMenu( "&MESUE",self.actionSUST)
		self.iface.removeToolBarIcon(self.actionSUST)
		
	def runSUIT(self):	# richiamato al click sull'azione
		from .geoSUIT import geoSUITDialog
		self.active_layer = self.iface.activeLayer()
		if ((self.active_layer == None) or (self.active_layer.type() != QgsMapLayer.VectorLayer)):
			result=QMessageBox.warning(self.iface.mainWindow(), "MESUE",
			("No se ha encontrado un layer activo\n" "Activa el layer con los indicadores\n" \
            "Necesitas más información ?"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
			if result  == QMessageBox.Yes:
				webbrowser.open("https://llactalab.ucuenca.edu.ec/")
		else:
			dlg = geoSUITDialog(self.iface)
			dlg.exec_()

