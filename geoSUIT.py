# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : MESUE - Modelo de Evaluación de Sustentabilidad Urbana Espacial
Description     : geographical MCDA for urban sustainability assessment
Date            : 10/05/2019
copyright       : LlactaLAB - Universidad de Cuenca (C) 2019
email           : (developper) Johnatan Astudillo (johnatan@ucuenca.edu.ec)

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMenu, QFileDialog
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
	
import os
import webbrowser
import shutil
import csv
import pickle

from . import DOMLEM
from . import htmlGraph
from .cartogram import *

from .ui_geoSUIT import Ui_Dialog

from .Zettings import *

class geoSUITDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.active_layer = self.iface.activeLayer()
		self.base_layer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)
		#self.SetBtnQuit.clicked.connect(self.reject)
		self.RetriveFileTBtn.clicked.connect(self.outFile)
		self.SetBtnBox.clicked.connect(self.settingStart)
		#self.SetBtnBox.clicked.connect(self.reject)
		self.SetBtnAbout.clicked.connect(self.about)
		self.SetBtnHelp.clicked.connect(self.open_help)
		self.BuiltSaveCfgBtn.clicked.connect(self.saveCfg)
		self.BioSaveCfgBtn.clicked.connect(self.saveCfg)
		self.MobSaveCfgBtn.clicked.connect(self.saveCfg)
		self.SocioSaveCfgBtn.clicked.connect(self.saveCfg)

		self.addLayerBtnBUILT.clicked.connect(self.addBuiltLayers)
		self.removeLayerBtnBUILT.clicked.connect(self.removeBuiltLayers)
		self.addLayerBtnBIO.clicked.connect(self.addBioLayers)
		self.removeLayerBtnBIO.clicked.connect(self.removeBioLayers)
		self.addLayerBtnMOB.clicked.connect(self.addMobLayers)
		self.removeLayerBtnMOB.clicked.connect(self.removeMobLayers)
		self.addLayerBtnSocialSpatial.clicked.connect(self.addSocialSpatialLayers)
		self.removeLayerBtnSocialSpatial.clicked.connect(self.removeSocialSpatialLayers)

		self.BuiltGetWeightBtn.clicked.connect(self.elaborate)
		self.BioGetWeightBtn.clicked.connect(self.elaborate)
		self.MobilityGetWeightBtn.clicked.connect(self.elaborate)
		self.SocioGetWeightBtn.clicked.connect(self.elaborate)

		
		self.sliders = [self.BuiltSlider,self.BioSlider,self.MobSlider, self.SocioSlider]
		i=0
		slider_amount=10
		slider_precision = 10 
		for slider in self.sliders:
			i=i+1
			slider.setRange(0, slider_amount*slider_precision)
			slider.setSingleStep(slider.maximum()/100.0)
			slider.setPageStep(slider.maximum()/20.0)
			slider.valueChanged.connect(self.onSliderValueChanged)
			slider.float_value = (i+1)/((1+slider_amount)/2.0*slider_amount)
		self.updateSliderValues()
		
		self.pushBtnEval.clicked.connect(self.overalValue)
		self.RenderMapBtn.clicked.connect(self.renderLayer)
		# self.RenderCarogramBtn.clicked.connect(self.renderCartogram)
		# self.GraphBtn.clicked.connect(self.buildOutput)
		
		self.AnlsBtnBox.clicked.connect(self.reject)
		self.CritExtractBtn.clicked.connect(self.extractRules)
		self.SaveRulesBtn.clicked.connect(self.saveRules)

###############################ContextMenu########################################
		builtHeaders = self.BuiltWeighTableWidget.horizontalHeader()
		builtHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		builtHeaders.customContextMenuRequested.connect(self.popMenu)
		
		bioHeaders = self.BioWeighTableWidget.horizontalHeader()
		bioHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		bioHeaders.customContextMenuRequested.connect(self.popMenu)
		
		mobHeaders = self.MobilityWeighTableWidget.horizontalHeader()
		mobHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		mobHeaders.customContextMenuRequested.connect(self.popMenu)

		socioHeaders = self.SocioWeighTableWidget.horizontalHeader()
		socioHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		socioHeaders.customContextMenuRequested.connect(self.popMenu)		
##################################################################################
		sourceIn=str(self.iface.activeLayer().source())
		self.BaseLayerLbl.setText(sourceIn)
		
		self.baseLbl.setText(sourceIn)
		pathSource=os.path.dirname(sourceIn)
		outputFile="mesue.shp"
		sourceOut=os.path.join(pathSource,outputFile)
		self.OutlEdt.setText(str(sourceOut))
		
		fields = [field.name() for field in self.active_layer.fields() ]
		# self.LabelListFieldsCBox.addItems(fields) #all fields
		# self.LabelCartogramCBox.addItems(['a_ideal','b_ideal','c_ideal', 'd_ideal', 'sus_ideal'])
				
		self.BuiltMapNameLbl.setText(self.active_layer.name())
		self.BioMapNameLbl.setText(self.active_layer.name())
		self.MobMapNameLbl.setText(self.active_layer.name())
		self.SocioMapNameLbl.setText(self.active_layer.name())
		
###############build list widget field#############################################
		allFields=self.getFieldNames(self.active_layer)
		self.listAllFields.addItems(allFields)
#################################################################################
		currentDir=unicode(os.path.abspath( os.path.dirname(__file__)))
		self.LblLogo.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"icon.png")))

#################################################################################
		self.automaticMoveFliedsToCategories()		


	def addBuiltLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listBuiltFields.addItems([item.text() for item in selectedItems])

	def removeBuiltLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listBuiltFields.selectedItems()
		[self.listBuiltFields.takeItem(self.listBuiltFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])

	def addBioLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listBioFields.addItems([item.text() for item in selectedItems])

	def removeBioLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listBioFields.selectedItems()
		[self.listBioFields.takeItem(self.listBioFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])
		
	def addMobLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listMobFields.addItems([item.text() for item in selectedItems])

	def removeMobLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listMobFields.selectedItems()
		[self.listMobFields.takeItem(self.listMobFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])

	def addSocialSpatialLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listSocioFields.addItems([item.text() for item in selectedItems])

	def removeSocialSpatialLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listSocioFields.selectedItems()
		[self.listSocioFields.takeItem(self.listSocioFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])		
		

	def popMenu(self):
		fields=range(10)
		menu = QMenu()
		removeAction = menu.addAction("Remove selected fields")
		#reloadAllFields=menu.addAction("Add deleted fields")
		action = menu.exec_(self.mapToGlobal(QPoint(100,100)))
		if action == removeAction:
			if self.toolBox.currentIndex()==1:
				self.removePopup(self.BuiltWeighTableWidget)
			elif self.toolBox.currentIndex()==2:
				self.removePopup(self.BioWeighTableWidget)
			elif self.toolBox.currentIndex()==3:
				self.removePopup(self.MobilityWeighTableWidget)
			
		
			
	def removePopup(self,table):
		#selected = sorted(self.BuiltWeighTableWidget.selectedColumns(),reverse=True)
		selected = sorted(table.selectionModel().selectedColumns(),reverse=True)
		if len(selected) > 0:
			for s in selected:
				self.removeField(s.column(),table)
			table.setCurrentCell(-1,-1)
			table.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "SSAM",
			("column must to be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0
		
	def removeField(self,i,table):
		"""Remove field in table in GUI"""
		table.removeColumn(i)
		return 0
		
	def getFieldNames(self, layer):
		"""retrive field names from active map/layer"""
		fields = layer.dataProvider().fields()
		field_list = []
		for field in fields:
			if field.typeName()!='String':
				field_list.append(str(field.name()))
		return field_list


	def outFile(self):
		"""Display file dialog for output  file"""
		self.OutlEdt.clear()
		outvLayer = QFileDialog.getSaveFileName(self, "Output map",".", "ESRI Shapefile (*.shp)")
		self.OutlEdt.insert(outvLayer[0])
		return outvLayer


	def settingStart(self):
		""" Prepare file for processing """
		self.lblOutputA.setText(str("mesue:"))
		self.lblOutputB.setText(str("mesue:"))
		self.lblOutputC.setText(str("mesue:"))
		self.lblOutputD.setText(str("mesue:"))
	
		outputFilename=self.OutlEdt.text()
		for i in range(1,(self.toolBox.count()-1)):
			self.toolBox.setItemEnabled (i,True)
		alayer = self.base_layer #self.iface.activeLayer()
		provider = alayer.dataProvider()
		fields = provider.fields()
		writer = QgsVectorFileWriter(outputFilename, "CP1250", fields, alayer.wkbType(), alayer.crs(), "ESRI Shapefile")
		outFeat = QgsFeature()
		self.LoadProgressBar.setRange(1,alayer.featureCount())
		progress=0
		for inFeat in alayer.getFeatures():
			progress=progress+1
			outFeat.setGeometry(inFeat.geometry() )
			outFeat.setAttributes(inFeat.attributes() )
			writer.addFeature( outFeat )
			self.LoadProgressBar.setValue(progress)
		del writer
		newlayer = QgsVectorLayer(outputFilename, os.path.basename(outputFilename), "ogr")
		#QgsMapLayerRegistry.instance().addMapLayer(newlayer)
		QgsProject.instance().addMapLayer(newlayer)
		self.active_layer=newlayer
		self.active_layer=QgsVectorLayer(self.OutlEdt.text(), self.active_layer.name(), "ogr") ##TODO check
		self.toolBox.setEnabled(True)
		######build tables###############
		self.BuiltGetWeightBtn.setEnabled(True)
		builtFields =  [str(self.listBuiltFields.item(i).text()) for i in range(self.listBuiltFields.count())]
		# print(builtFields)
		self.buildTables(self.BuiltWeighTableWidget,builtFields)
		self.updateGUIIdealPointFctn(self.BuiltWeighTableWidget,provider)
		
		self.BioGetWeightBtn.setEnabled(True)
		bioFields =[str(self.listBioFields.item(i).text()) for i in range(self.listBioFields.count())]
		self.buildTables(self.BioWeighTableWidget,bioFields)
		self.updateGUIIdealPointFctn(self.BioWeighTableWidget,provider)


		self.MobilityGetWeightBtn.setEnabled(True)
		mobFields =[str(self.listMobFields.item(i).text()) for i in range(self.listMobFields.count())]
		self.buildTables(self.MobilityWeighTableWidget,mobFields)
		self.updateGUIIdealPointFctn(self.MobilityWeighTableWidget,provider)


		self.SocioGetWeightBtn.setEnabled(True)
		socioFields =[str(self.listSocioFields.item(i).text()) for i in range(self.listSocioFields.count())]
		self.buildTables(self.SocioWeighTableWidget,socioFields)
		self.updateGUIIdealPointFctn(self.SocioWeighTableWidget,provider)		

		self.readSettingFile(self.BuiltWeighTableWidget,builtFields) #load setting data stored in setting.csv
		self.readSettingFile(self.BioWeighTableWidget,bioFields) #load setting data stored in setting.csv
		self.readSettingFile(self.MobilityWeighTableWidget,mobFields) #load setting data stored in setting.csv
		self.readSettingFile(self.SocioWeighTableWidget,socioFields) #load setting data stored in setting.csv

		self.EnvProgressBar.setRange(0,100)
		self.EnvProgressBar.setValue(0)
		self.EcoProgressBar.setRange(0,100)
		self.EcoProgressBar.setValue(0)
		self.SocProgressBar.setRange(0,100)
		self.SocProgressBar.setValue(0)
		self.SocioProgressBar.setRange(0,100)
		self.SocioProgressBar.setValue(0)			
		return 0

	def buildTables(self,weighTableWidget,fields):
		"""base function for updateTable()"""
		Envfields=self.getFieldNames(self.active_layer) #field list
		setLabel=["Etiquetas","Pesos","Preferencia","Punto ideal", "Punto anti-ideal "]
		weighTableWidget.setColumnCount(len(fields))
		weighTableWidget.setHorizontalHeaderLabels(fields)
		weighTableWidget.setRowCount(5)
		weighTableWidget.setVerticalHeaderLabels(setLabel)
		for r in range(len(fields)):
			defaultLabel = self.loadDefaultLabel(fields[r])
			# print("el nombre es: " + defaultLabel)
			weighTableWidget.setItem(0,r,QTableWidgetItem(defaultLabel))
			weighTableWidget.setItem(1,r,QTableWidgetItem("1.0"))
			weighTableWidget.setItem(2,r,QTableWidgetItem("gain"))
		
		#retrieve signal for modified cells
		try:
			weighTableWidget.cellClicked[(int,int)].connect(self.changeValue)
		except:
			pass

	def loadDefaultLabel(self, field):
		isIndicatorSisurbano, group, name = self.isIndicatorSisurbano(field)
		if(name == "-"):
			description = "-"
		else:
			description = NAMES_INDEX[name.upper()][2]
		return description		

	def readSettingFile(self,WeighTableWidget,fields):
		pathSource = (os.path.dirname(str(self.base_layer.source())))
		print("Leyendo archivo de configuraciones")
		try:
			if (os.path.exists(os.path.join(pathSource,"setting.csv"))==True):
				setting=[i.strip().split(';') for i in open(os.path.join(pathSource,"setting.csv")).readlines()]
				for i in range(len(fields)):
					for l in range(len(setting[1])):
						if fields[i]==setting[1][l]:
							WeighTableWidget.horizontalHeaderItem(i).setToolTip((str(setting[0][l])))
							WeighTableWidget.setItem(0,i,QTableWidgetItem(str(setting[0][l])))
							WeighTableWidget.setItem(1,i,QTableWidgetItem(str(setting[2][l])))
							WeighTableWidget.setItem(2,i,QTableWidgetItem(str(setting[3][l])))
							WeighTableWidget.setItem(3,i,QTableWidgetItem(str(setting[4][l])))
							WeighTableWidget.setItem(4,i,QTableWidgetItem(str(setting[5][l])))
		except:
				QgsMessageLog.logMessage("Problemas leyendo el archivo de configuraciones","SSAM")
				#self.fillTableFctn(fields,WeighTableWidget)
		return 0
				

	def updateGUIIdealPointFctn(self,WeighTableWidget,provider):
		"""base function for updateGUIIdealPoint()"""
		criteria=[WeighTableWidget.horizontalHeaderItem(f).text() for f in range(WeighTableWidget.columnCount())]
		preference=[str(WeighTableWidget.item(2, c).text()) for c in range(WeighTableWidget.columnCount())]
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]
		for r in range(len(preference)):
			if preference[r]=='gain':
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(maxField[r])))#ideal point
				WeighTableWidget.setItem(4,r,QTableWidgetItem(str(minField[r])))#worst point
			elif preference[r]=='cost':
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(minField[r])))
				WeighTableWidget.setItem(4,r,QTableWidgetItem(str(maxField[r])))
			else:
				WeighTableWidget.setItem(3,r,QTableWidgetItem("0"))
				WeighTableWidget.setItem(4,r,QTableWidgetItem("0"))
	


	def changeValue(self):
		"""Event for change gain/cost"""
		if self.toolBox.currentIndex()==1:
			cell=self.BuiltWeighTableWidget.currentItem()
			r=cell.row()
			c=cell.column()
			first=self.BuiltWeighTableWidget.item(3, c).text()
			second=self.BuiltWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.BuiltWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.BuiltWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.BuiltWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.BuiltWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.BuiltWeighTableWidget.setItem(4,c, QTableWidgetItem(first))
		elif self.toolBox.currentIndex()==2:
			cell=self.BioWeighTableWidget.currentItem()
			r=cell.row()
			c=cell.column()
			first=self.BioWeighTableWidget.item(3, c).text()
			second=self.BioWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.BioWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.BioWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.BioWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.BioWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.BioWeighTableWidget.setItem(4,c, QTableWidgetItem(first))
		elif self.toolBox.currentIndex()==3:
			cell=self.MobilityWeighTableWidget.currentItem()
			c=cell.column()
			first=self.MobilityWeighTableWidget.item(3, c).text()
			second=self.MobilityWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.MobilityWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.MobilityWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.MobilityWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.MobilityWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.MobilityWeighTableWidget.setItem(4,c, QTableWidgetItem(first))
		elif self.toolBox.currentIndex()==4:
			cell=self.SocioWeighTableWidget.currentItem()
			c=cell.column()
			first=self.SocioWeighTableWidget.item(3, c).text()
			second=self.SocioWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.SocioWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.SocioWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.SocioWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.SocioWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.SocioWeighTableWidget.setItem(4,c, QTableWidgetItem(first))				
		else:
			pass
		
		
	def onSliderValueChanged(self, value):
		changed_slider = self.sender()
		changed_slider.float_value = float(value)/changed_slider.maximum()
		delta = sum(slider.float_value for slider in self.sliders)-1
		while abs(delta)>0.00001:
			d = len(self.sliders)-1
			for slider in self.sliders:
				if slider is changed_slider:
					continue
				old_value = slider.float_value
				slider.float_value = min(max(0, old_value-delta/d), 1)
				delta -= old_value-slider.float_value
				d -= 1
		self.updateSliderValues()
		
		
	def updateSliderValues(self):
		for slider in self.sliders:
			slider_signals_blocked = slider.blockSignals(True)
			slider.setValue(round(slider.float_value*slider.maximum()))
			slider.blockSignals(slider_signals_blocked)
			#slider.label.setText('{:.2f}'.format(slider.float_value))

		
	# def setBuiltSlider(self):
	# 	builtDelta=self.BuiltSlider.maximum()-self.BuiltSlider.value()
	# 	bioDelta=self.BioSlider.maximum()-self.BioSlider.value()
	# 	mobDelta=self.MobSlider.maximum()-self.MobSlider.value()
	# 	socialDelta=self.SocioSlider.maximum()-self.SocioSlider.value()
	# 	if self.ecoCheckBox.isChecked():
	# 		bioMove=self.BioSlider.value()
	# 	else:
	# 		bioMove=float(bioDelta)/float(bioDelta+mobDelta+socialDelta)*builtDelta
	# 	if self.socCheckBox.isChecked():
	# 		mobMove=self.MobSlider.value()
	# 	else:
	# 		mobMove=float(mobDelta)/float(bioDelta+mobDelta+socialDelta)*builtDelta
	# 	self.BioSlider.setValue(bioMove)
	# 	self.MobSlider.setValue(mobMove)
		
	# def setBioSlider(self):
	# 	builtDelta=self.BuiltSlider.maximum()-self.BuiltSlider.value()
	# 	bioDelta=self.BioSlider.maximum()-self.BioSlider.value()
	# 	mobDelta=self.MobSlider.maximum()-self.MobSlider.value()
	# 	builtMove=float(builtDelta)/float(builtDelta+mobDelta)*bioDelta
	# 	mobMove=float(mobDelta)/float(builtDelta+mobDelta)*bioDelta
	# 	self.BuiltSlider.setValue(builtMove)
	# 	self.MobSlider.setValue(mobMove)
	
	# def setMobSlider(self):
	# 	builtDelta=self.BuiltSlider.maximum()-self.BuiltSlider.value()
	# 	bioDelta=self.BioSlider.maximum()-self.BioSlider.value()
	# 	mobDelta=self.MobSlider.maximum()-self.MobSlider.value()
	# 	bioMove=float(bioDelta)/float(bioDelta+builtDelta)*mobDelta
	# 	builtMove=float(builtDelta)/float(bioDelta+builtDelta)*mobDelta
	# 	self.BioSlider.setValue(bioMove)
	# 	self.BuiltSlider.setValue(builtMove)
		
	def elaborate(self):
		self.standardizationIdealPoint()
		self.relativeCloseness()
		# self.overalValue()
		self.saveCfg()
		#self.setModal(True)
		return 0
#############################################################################################################

	def addDecisionField(self,layer,Label):
		"""Add field on attribute table"""
		caps = layer.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddAttributes:
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double,"",24,4,"")] )
		return 0


###########################################################################################
	def extractFieldSumSquare(self,field):
		"""Retrive single field value from attributes table"""
		provider=self.base_layer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		for feat in self.base_layer.getFeatures():
			attribute=feat.attributes()[fid]
			listValue.append(attribute)
		listValue=[pow(l,2) for l in listValue]
		return (sum(listValue)**(0.5))
	
	def standardizationIdealPoint(self):
		"""Perform STEP 1 and STEP 2 of TOPSIS algorithm
		Se calcula la matriz de decision normalizada ponderada
		raiz(valor/(sum(cada_valor^2))) * peso
		"""

		if self.toolBox.currentIndex()==1:
			criteria=[self.BuiltWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BuiltWeighTableWidget.columnCount())]
			weight=[float(self.BuiltWeighTableWidget.item(1, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())]
			# print(weight)
			weight=[ round(w/sum(weight),4) for w in weight ]
			print("----peso recalculado------")
			# print(weight)
			for c,w in zip(range(len(criteria)),weight):
				self.BuiltWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.BuiltGetWeightBtn.setEnabled(False)
		elif self.toolBox.currentIndex()==2:
			criteria=[self.BioWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BioWeighTableWidget.columnCount())]
			weight=[float(self.BioWeighTableWidget.item(1, c).text()) for c in range(self.BioWeighTableWidget.columnCount())]
			weight=[ round(w/sum(weight),4) for w in weight ]
			for c,w in zip(range(len(criteria)),weight):
				self.BioWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.BioGetWeightBtn.setEnabled(False)
		elif self.toolBox.currentIndex()==3:
			criteria=[self.MobilityWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.MobilityWeighTableWidget.columnCount())]
			weight=[float(self.MobilityWeighTableWidget.item(1, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())]
			weight=[ round(w/sum(weight),4) for w in weight ]
			for c,w in zip(range(len(criteria)),weight):
				self.MobilityWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.MobilityGetWeightBtn.setEnabled(False)
		elif self.toolBox.currentIndex()==4:
			criteria=[self.SocioWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.SocioWeighTableWidget.columnCount())]
			weight=[float(self.SocioWeighTableWidget.item(1, c).text()) for c in range(self.SocioWeighTableWidget.columnCount())]
			weight=[ round(w/sum(weight),4) for w in weight ]
			for c,w in zip(range(len(criteria)),weight):
				self.SocioWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.SocioGetWeightBtn.setEnabled(False)			
		else:
			pass
		provider=self.active_layer.dataProvider()
		feat = QgsFeature()
		#obtiene los id de los atributos
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		# print(fids)
		#self.EnvTEdit.append(str(dict(zip(fids,[(field) for field in criteria]))))
		sumSquareColumn=dict(zip(fids,[self.extractFieldSumSquare(field) for field in criteria]))
		#provider.select(fids)
		self.active_layer.startEditing()
		for f,w in zip(fids,weight): #N.B. verifica corretto allineamento con i pesi
			for feat in self.active_layer.getFeatures():
				attributes=feat.attributes()[f]
				# print(attributes)
				# FIXME: DA PROBLEMAS CUANDO TODOS LOS VALORES SON CERO
				value=(float(attributes)/float(sumSquareColumn[f]))*w   # TOPSIS algorithm: STEP 1 and STEP 2
				#print sumSquareColumn[f]
				self.active_layer.changeAttributeValue(feat.id(),f,round(value,4))
		self.active_layer.commitChanges()
		return 0
		
			
	def relativeCloseness(self):
		""" Calculate distance from ideal point

		Medidas al punto ideal y distacia al punto anti-ideal
		Proximidad Relativa a la alternativa ideal (la mas alejada de la antiideal)

		"""
		if self.toolBox.currentIndex()==1:
			criteria=[self.BuiltWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BuiltWeighTableWidget.columnCount())]
			weight=[float(self.BuiltWeighTableWidget.item(1, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())]
			# print(weight)
			# idealPoint=[float(self.BuiltWeighTableWidget.item(3, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			#el valor ideal se normaliza y se pondera de la misma forma que los valores de las alternativas
			#usando los valores de la matriz ponderada
			idealPoint=[float(self.BuiltWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.BuiltWeighTableWidget.columnCount())]
			print("-----------ideal point------------")
			# print(idealPoint)
			#el valor anti-ideal se normaliza y se pondera de la misma forma que los valores de las alternativas
			#usando los valores de la matriz ponderada
			worstPoint=[float(self.BuiltWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.BuiltWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("a_ideal")==-1:
				self.addDecisionField(self.active_layer,"a_ideal")
			fldValue = provider.fieldNameIndex("a_ideal") #obtain classify field index from its name
			# self.EnvTEdit.append("done") #   setText
			self.lblOutputA.setText(str("mesue: Done!!!!"))
			# self.lblOutputA.append(str("Done!!!!"))
		elif self.toolBox.currentIndex()==2:
			criteria=[self.BioWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BioWeighTableWidget.columnCount())]
			weight=[float(self.BioWeighTableWidget.item(1, c).text()) for c in range(self.BioWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			idealPoint=[float(self.BioWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.BioWeighTableWidget.columnCount())]
			worstPoint=[float(self.BioWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.BioWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("b_ideal")==-1:
				self.addDecisionField(self.active_layer,"b_ideal")
			fldValue = provider.fieldNameIndex("b_ideal") #obtain classify field index from its name
			# self.EcoTEdit.append("done")
			self.lblOutputB.setText(str("mesue: Done!!!!"))
		elif self.toolBox.currentIndex()==3:
			criteria=[self.MobilityWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.MobilityWeighTableWidget.columnCount())]
			weight=[float(self.MobilityWeighTableWidget.item(1, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			idealPoint=[float(self.MobilityWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c]\
				for c in range(self.MobilityWeighTableWidget.columnCount())]
			worstPoint=[float(self.MobilityWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.MobilityWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("c_ideal")==-1:
				self.addDecisionField(self.active_layer,"c_ideal")
			fldValue = provider.fieldNameIndex("c_ideal") #obtain classify field index from its name
			# self.SocTEdit.append("mesue: done")
			self.lblOutputC.setText(str("mesue: Done!!!!"))
		elif self.toolBox.currentIndex()==4:
			criteria=[self.SocioWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.SocioWeighTableWidget.columnCount())]
			weight=[float(self.SocioWeighTableWidget.item(1, c).text()) for c in range(self.SocioWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			idealPoint=[float(self.SocioWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c]\
				for c in range(self.SocioWeighTableWidget.columnCount())]
			worstPoint=[float(self.SocioWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.SocioWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("d_ideal")==-1:
				self.addDecisionField(self.active_layer,"d_ideal")
			fldValue = provider.fieldNameIndex("d_ideal") #obtain classify field index from its name
			# self.SocTEdit.append("mesue: done")
			self.lblOutputD.setText(str("mesue: Done!!!!"))			
		else:
			pass
		#self.EnvTEdit.append(str(idealPoint)+"#"+str(worstPoint))
		features=provider.featureCount() #Number of features in the layer.
		print("total de featrues: " + str(features))
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		self.active_layer.startEditing()
		self.EnvProgressBar.setRange(1,features)
		self.EcoProgressBar.setRange(1,features)
		self.SocProgressBar.setRange(1,features)
		self.SocioProgressBar.setRange(1,features)
		progress=0
		for feat in self.active_layer.getFeatures():
			IP=WP=0
			for f,idp,wrp in zip(fids,idealPoint,worstPoint):
				attributes = feat.attributes()
				# para cada celda o alternativa se suma las diferencias a los puntos ideal y anti-ideal
				# diferencias de distancias globales
				IP =IP+(float(attributes[f]-idp)**2)   # TOPSIS algorithm: STEP 4
				WP =WP+(float(attributes[f]-wrp)**2)
			# distancia relativa de todos los criterios(indicadores)	
			relativeCloseness=(WP**(0.5))/((WP**(0.5))+(IP**(0.5)))
			self.active_layer.changeAttributeValue(feat.id(), fldValue, round(float(relativeCloseness),4))
			progress=progress+1
			if self.toolBox.currentIndex()==1:
				self.EnvProgressBar.setValue(progress)
			elif self.toolBox.currentIndex()==2:
				self.EcoProgressBar.setValue(progress)
			elif self.toolBox.currentIndex()==3:
				self.SocProgressBar.setValue(progress)
			elif self.toolBox.currentIndex()==4:
				self.SocioProgressBar.setValue(progress)
		self.active_layer.commitChanges()
		# self.EnvProgressBar.setValue(1)
		# self.EcoProgressBar.setValue(1)
		# self.SocProgressBar.setValue(1)
		# self.SocioProgressBar.setValue(1)
		return 0

		
		
	def overalValue(self):
		"""Sum Environmental and Socio-economics value for calculate  Sustainable value"""
		weight=[self.BuiltSlider.value(),self.BioSlider.value(),self.MobSlider.value(), self.SocioSlider.value()]
		provider=self.active_layer.dataProvider()
		if provider.fieldNameIndex("sus_ideal")==-1:
			self.addDecisionField(self.active_layer,"sus_ideal")
		fldValue = provider.fieldNameIndex("sus_ideal") #obtain classify field index from its name
		fids=[provider.fieldNameIndex(c) for c in ['a_ideal','b_ideal','c_ideal', 'd_ideal']]
		if -1 not in fids:
			self.active_layer.startEditing()
			for feat in self.active_layer.getFeatures():
				attributes=feat.attributes()
				#self.EnvTEdit.append(str(fids)+"-"+str([(attributes[att]) for att in fids]))
				value=sum([float(str(attributes[att]))*w for att,w in zip(fids,weight)])
				#print [attributes[att] for att in fids], [w for w in weight], value
				self.active_layer.changeAttributeValue(feat.id(), fldValue, round(float(value),4))
			self.active_layer.commitChanges()
			
			#self.LabelCartogramCBox.addItems(self.getFieldNames(self.active_layer)) #numeric fields
			
			# self.pushBtnEval.setEnabled(False)
			self.toolBox.setItemEnabled(5,True) #activate last toolbox
			# self.toolBox.setItemEnabled(6,True) #activate last toolbox
			self.symbolize('sus_ideal')
			return 0
		else:
			return -1
		


###########################################################################################

	def symbolize(self,field):
		"""Prepare legends for environmental, socio economics and sustainable values"""
		numberOfClasses=self.spinBoxClasNum.value()
		if(numberOfClasses==5):
			classes=['muy bajo', 'bajo','medio','alto','muy alto']
		else:
			classes=range(1,numberOfClasses+1)
		fieldName = field
		layer=self.active_layer
		fieldIndex = layer.fields().indexFromName(fieldName)
		provider = layer.dataProvider()
		minimum = provider.minimumValue( fieldIndex )
		maximum = provider.maximumValue( fieldIndex )
		string="%s,%s,%s" %(minimum,maximum,layer.name() )
		#self.SocTEdit.append(string)
		RangeList = []
		Opacity = 1
		for c,i in zip(classes,range(len(classes))):
		# Crea il simbolo ed il range...
			Min = round(minimum + (( maximum - minimum ) / numberOfClasses * i),4)
			Max = round(minimum + (( maximum - minimum ) / numberOfClasses * ( i + 1 )),4)
			Label = "%s [%.2f - %.2f]" % (c,Min,Max)
			if field=='sus_ideal':
				# Colour = QColor((255-85*i/numberOfClasses),\
				# 				(255-255*i/numberOfClasses),\
				# 				(127-127*i/numberOfClasses)) #red to green
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-170*i/numberOfClasses),\
								(127-127*i/numberOfClasses)) #yellow to green				
			elif field=='a_ideal':
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-170*i/numberOfClasses),\
								(127-127*i/numberOfClasses)) #yellow to green
			elif field=='b_ideal':
				# Colour = QColor(255,255-255*i/numberOfClasses,0) #yellow to red
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-170*i/numberOfClasses),\
								(127-127*i/numberOfClasses)) #yellow to green					
			elif field=='c_ideal':
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-85*i/numberOfClasses),\
								(127+128*i/numberOfClasses)) #yellow to cyan 255,255,127
			elif field=='d_ideal':
				# Colour = QColor(255,255-255*i/numberOfClasses,0) #yellow to red		
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-170*i/numberOfClasses),\
								(127-127*i/numberOfClasses)) #yellow to green					
			Symbol = QgsSymbol.defaultSymbol(layer.geometryType())
			Symbol.setColor(Colour)
			Symbol.setOpacity(Opacity)
			Range = QgsRendererRange(Min,Max,Symbol,Label)
			RangeList.append(Range)
		Renderer = QgsGraduatedSymbolRenderer('', RangeList)
		Renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
		Renderer.setClassAttribute(fieldName)
		add=QgsVectorLayer(layer.source(),field,'ogr')
		add.setRenderer(Renderer)
		QgsProject.instance().addMapLayer(add)

	def renderLayer(self):
		""" Load thematic layers in canvas """
		#self.setModal(False)
		layer = self.active_layer
		fields=['a_ideal','b_ideal','c_ideal', 'd_ideal']
		for f in fields:
			self.symbolize(f)
		

###########################################################################################
	def refreshLayer(self):
		self.active_layer.setCacheImage( None )
		self.active_layer.triggerRepaint()
		self.EnvTEdit.append("refresced")
		
		
	def createMemoryLayer(self,layer):
		"""Create an in-memory copy of an existing vector layer."""
		data_provider = layer.dataProvider()

		# create the layer path defining geometry type and reference system
		#geometry_type = QGis.vectorGeometryType(layer.geometryType())
		geometry_type = QgsWkbTypes.geometryDisplayString(layer.geometryType())
		crs_id = layer.crs().authid()
		path = geometry_type + '?crs=' + crs_id + '&index=yes'

		# create the memory layer and get a reference to the data provider
		memory_layer = QgsVectorLayer(path, 'Cartogram', 'memory')
		memory_layer_data_provider = memory_layer.dataProvider()

		# copy all attributes from the source layer to the memory layer
		memory_layer.startEditing()
		memory_layer_data_provider.addAttributes(
			data_provider.fields().toList())
		memory_layer.commitChanges()

		# copy all features from the source layer to the memory layer
		for feature in data_provider.getFeatures():
			memory_layer_data_provider.addFeatures([feature])

		return memory_layer
		
		
	def extractAttributeValue(self,field):
		"""Retrive single field value from attributes table"""
		fields=self.active_layer.fields()
		provider=self.active_layer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		if fields[fid].typeName()=='Real' or fields[fid].typeName()=='Integer':
			for feat in self.active_layer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(float(attribute))
		else:
			for feat in self.active_layer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(str(attribute))
		return listValue

	def buildOutput(self):
		"""General function for all graphical and tabula output"""
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		self.exportTable()
		if os.path.isfile(os.path.join(currentDir,"points.png"))==True:
			os.remove(os.path.join(currentDir,"points.png"))
		if os.path.isfile(os.path.join(currentDir,"histogram.png"))==True:
			os.remove(os.path.join(currentDir,"histogram.png"))
		# self.buildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		#self.setModal(False)
		return 0

	# def renderCartogram(self):
	# 	layer=self.createMemoryLayer(self.active_layer)
	# 	input_field=self.LabelCartogramCBox.currentText()
	# 	iterations=5
	# 	Cartogram=CartogramWorker(layer, input_field, iterations)
	# 	Cartogram.run()
	# 	if layer is not None:
	# 		QgsProject.instance().addMapLayer(layer)
	# 	else:
	# 		"None!"
		#export2JSON(layer)


		
	# def buildHTML(self):
	# 	EnvValue=self.extractAttributeValue('a_ideal')
	# 	EcoValue=self.extractAttributeValue('b_ideal')
	# 	SocValue=self.extractAttributeValue('c_ideal')
	# 	SocValue=self.extractAttributeValue('d_ideal')
	# 	SustValue=self.extractAttributeValue('sus_ideal')
	# 	#SuitValue=[x+y+z for (x,y,z) in zip(EnvValue,EcoValue,SocValue)]
	# 	label=self.LabelListFieldsCBox.currentText()
	# 	labels=self.extractAttributeValue(label)
	# 	labels=[str(l) for l in labels]
	# 	htmlGraph.BuilHTMLGraph(SustValue,EnvValue,EcoValue,SocValue,labels)
	# 	return 0
		
	def exportTable(self):
		try:
			criteria=[self.BuiltWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BuiltWeighTableWidget.columnCount())]
			currentDIR = (os.path.dirname(str(self.base_layer.source())))
			bLayer=self.base_layer
			field_names = [field.name() for field in bLayer.fields()]+['a_ideal','b_ideal','c_ideal','d_ideal','sus_ideal']
			EnvValue=self.extractAttributeValue('a_ideal')
			EcoValue=self.extractAttributeValue('b_ideal')
			SocValue=self.extractAttributeValue('c_ideal')
			SocValue=self.extractAttributeValue('d_ideal')
			SustValue=self.extractAttributeValue('sus_ideal')
			att2csv=[]
			for feature,env,eco,soc in zip(bLayer.getFeatures(),EnvValue,EcoValue,SocValue):
				row=feature.attributes()+[env,eco,soc]
				att2csv.append(row)
			with open(os.path.join(currentDIR,'attributes.csv'), 'wb') as csvfile:
				spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
				spamwriter.writerow(field_names)
				spamwriter.writerows(att2csv)
			return 0
		except:
			QgsMessageLog.logMessage("Problem in writing export table file","MESUE")
		
###################################################################################################
	def saveCfg(self):
		currentDIR = (os.path.dirname(str(self.base_layer.source())))
		setting=(os.path.join(currentDIR,"setting.csv"))
		fileCfg = open(os.path.join(currentDIR,"setting.csv"),"w")
		builtLabel=[(self.BuiltWeighTableWidget.item(0, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())]
		bioLabel=[(self.BioWeighTableWidget.item(0, c).text()) for c in range(self.BioWeighTableWidget.columnCount())]
		mobLabel=[(self.MobilityWeighTableWidget.item(0, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())]
		socialLabel=[(self.SocioWeighTableWidget.item(0, c).text()) for c in range(self.SocioWeighTableWidget.columnCount())]
		label=builtLabel+bioLabel+mobLabel+socialLabel
		# print(label)
		criteria,preference,weight,ideal,worst=self.usedCriteria()
		for l in label:
			fileCfg.write(str(l)+";")
		fileCfg.write("\n")
		for c in criteria:
			fileCfg.write(str(c)+";")
		fileCfg.write("\n")
		fileCfg.write(";".join(weight))
		fileCfg.write("\n")
		for p in preference:
			fileCfg.write(str(p)+";")
		fileCfg.write("\n")
		fileCfg.write(";".join(ideal))
		fileCfg.write("\n")
		fileCfg.write(";".join(worst))
		fileCfg.close()

		
	def about(self):
		"""    Visualize an About window."""
		QMessageBox.about(self, "Acerca de MESUE",
		"""
			<p>MESUE<br />2019-12-31<br />License: GPL v. 3</p>
			<hr>
			<p>Universidad de Cuenca - Departamento de Espacio y Población - LLactaLAB <a href="https://llactalab.ucuenca.edu.ec/">llactalab.ucuenca.edu.ec</a></p>
			<hr>
			<p>Documentación: <a href="https://llactalab.ucuenca.edu.ec">llactalab.ucuenca.edu.ec</a></p>
			<p>Reporta errores a <a href="mailto:johnatan.astudillo@ucuenca.edu.ec">johnatan.astudillo@ucuenca.edu.ec</a></p>
		""")



	def open_help(self):
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		webbrowser.open(os.path.join(currentDir,"data.html"))
		webbrowser.open("https://llactalab.ucuenca.edu.ec/")

###################################################################################################

	def discretizeDecision(self,value,listClass,numberOfClasses):
		DiscValue=-1
		for o,t in zip(range(numberOfClasses),range(1,numberOfClasses+1)) :
			if ((float(value)>=float(listClass[o])) and (float(value)<=float(listClass[t]))):
				DiscValue=o+1
		return DiscValue
	
			
	def addDiscretizedField(self):
		"""add new field"""
		field="sus_ideal"
		numberOfClasses=5
		provider=self.base_layer.dataProvider()
		#provider=self.active_layer.dataProvider()
		if provider.fieldNameIndex("Classified")==-1:
			self.addDecisionField(self.base_layer,"Classified")
		fidClass = provider.fieldNameIndex("Classified") #obtain classify field index from its name
		listInput=self.extractAttributeValue(field)
		widthOfClass=float((max(listInput))-float(min(listInput)))/float(numberOfClasses)
		listClass=[(min(listInput)+(widthOfClass)*i) for i in range(numberOfClasses+1)]
		#self.EnvTEdit.setText(str(listClass))
		self.base_layer.startEditing()
		decision=[]
		for feat in self.base_layer.getFeatures():
			DiscValue=self.discretizeDecision(listInput[int(feat.id())],listClass,numberOfClasses)
			self.base_layer.changeAttributeValue(feat.id(), fidClass, float(DiscValue))
			decision.append(DiscValue)
		self.base_layer.commitChanges()
		return list(set(decision))

	def usedCriteria(self):
		criteria=[self.BuiltWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BuiltWeighTableWidget.columnCount())] + \
			[self.BioWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.BioWeighTableWidget.columnCount())] + \
			[self.MobilityWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.MobilityWeighTableWidget.columnCount())]
		weight=[str(self.BuiltWeighTableWidget.item(1, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())] +\
			[str(self.BioWeighTableWidget.item(1, c).text()) for c in range(self.BioWeighTableWidget.columnCount())] + \
			[str(self.MobilityWeighTableWidget.item(1, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())]
		preference=[str(self.BuiltWeighTableWidget.item(2, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())] +\
			[str(self.BioWeighTableWidget.item(2, c).text()) for c in range(self.BioWeighTableWidget.columnCount())] + \
			[str(self.MobilityWeighTableWidget.item(2, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())] 
		ideal=[str(self.BuiltWeighTableWidget.item(3, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())] +\
			[str(self.BioWeighTableWidget.item(3, c).text()) for c in range(self.BioWeighTableWidget.columnCount())] + \
			[str(self.MobilityWeighTableWidget.item(3, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())] 
		worst=[str(self.BuiltWeighTableWidget.item(4, c).text()) for c in range(self.BuiltWeighTableWidget.columnCount())] +\
			[str(self.BioWeighTableWidget.item(4, c).text()) for c in range(self.BioWeighTableWidget.columnCount())] + \
			[str(self.MobilityWeighTableWidget.item(4, c).text()) for c in range(self.MobilityWeighTableWidget.columnCount())] 
		return criteria, preference,weight,ideal,worst
		
	def writeISFfile(self,decision):
		#currentDIR = (os.path.dirname(str(self.base_layer.source())))
		currentDIR = (os.path.dirname(str(self.active_layer.source())))
		out_file = open(os.path.join(currentDIR,"example.isf"),"w")
		criteria,preference,weight,ideal,worst=self.usedCriteria()
		criteria.append("Classified")
		preference.append("gain")
		#decision=list(set(self.extractAttributeValue("Classified")))
		decision=[int(i) for i in decision]
		out_file.write("**ATTRIBUTES\n") 
		for c in (criteria):
			if(str(c)=="Classified"):
				out_file.write("+ Classified: %s\n"  % (decision))
			else:
				out_file.write("+ %s: (continuous)\n"  % (c))
		out_file.write("decision: Classified")
		out_file.write("\n\n**PREFERENCES\n")
		for c,p in zip(criteria,preference):
			out_file.write("%s: %s\n"  % (c,p))
		out_file.write("\n**EXAMPLES\n")
		provider=self.base_layer.dataProvider()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its names
		for feat in self.base_layer.getFeatures():
			attribute = [feat.attributes()[j] for j in fids]
			for i in (attribute):
				out_file.write(" %s " % (i))
			out_file.write("\n")
		out_file.write("\n**END")
		out_file.close()
		return 0


	def showRules(self):
		currentDIR = (os.path.dirname(str(self.base_layer.source())))
		rules=open(os.path.join(currentDIR,"rules.rls"))
		R=rules.readlines()
		self.RulesListWidget.clear()
		for E in R:
			self.RulesListWidget.addItem(E)
		self.RulesListWidget.itemClicked.connect(self.selectFeatures)
		rules.close()
		return 0

	def queryByRule(self,R):
		"""perform query based on extracted rules"""
		E=R[0]
		exp="%s %s %s" % (E['label'],E['sign'],E['condition'])
		if len(R)>1:
			for F in R[1:]:
				exp=exp + " AND %s %s %s" % (F['label'],F['sign'],F['condition'])
		return exp


	def extractFeaturesByExp(self,layer,exp):
		exp = QgsExpression(exp)
		it=layer.getFeatures(QgsFeatureRequest(exp))
		listOfResults=[i.id() for i in it]
		return listOfResults


	def selectFeatures(self):
		"""select feature in attribute table based on rules"""
		activeLayer= self.iface.activeLayer()
		baseLayer=self.base_layer
		#currentDIR = QgsProject.instance().readPath("./")
		currentDIR = (os.path.dirname(str(self.base_layer.source())))		
		rulesPKL = open(os.path.join(currentDIR,"RULES.pkl"), 'rb')
		RULES=pickle.load(rulesPKL) #save RULES dict in a file for use it in geoRULES module
		rulesPKL.close()
		selectedRule=self.RulesListWidget.currentItem().text()
		selectedRule=int(selectedRule.split(":")[0])
		R=RULES[selectedRule-1]
		exp=self.queryByRule(R)
		idSel=self.extractFeaturesByExp(baseLayer,exp)
		activeLayer.selectByIds(idSel)
		return 0
		


	def extractRules(self):
		pathSource=os.path.dirname(str(self.active_layer.source()))
		print("active:%s;base:%s" % (os.path.dirname(str(self.active_layer.source())),os.path.dirname(str(self.base_layer.source()))))
		#pathSource=os.path.dirname(str(self.iface.activeLayer().source()))
		decision=self.addDiscretizedField()
		self.writeISFfile(decision)
		DOMLEM.main(pathSource)
		self.showRules()
		#self.setModal(False)
		return 0
		
	def saveRules(self):
		currentDIR = (os.path.dirname(str(self.active_layer.source())))
		rules=(os.path.join(currentDIR,"rules.rls"))
		#filename = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'),".rls")
		filename = QFileDialog.getSaveFileName(self, 'Save File', ".rls") 
		shutil.copy2(rules, filename[0])
		return 0

	def openFile(self):
		filename = QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME')) 
		f = open(filename, 'r') 
		filedata = f.read() 
		self.text.setText(filedata) 
		f.close()

	def isIndicatorSisurbano(self, item):
		group = item[:2]
		isCorrectLength = len(item[2:]) == 2
		isNumber = (item[2:]).isdigit()		
		if not isNumber or not isCorrectLength:
			item = "-"
		return isNumber and isCorrectLength, group, item 

	def automaticMoveFliedsToCategories(self):
		"add criteria fiends in environmental list"
		# print("moving flieds")
		items = []
		for index in range(self.listAllFields.count()):
			item = self.listAllFields.item(index)
			nameIndicator = item.text()
			isIndicatorSisurbano, group, nameIndicator = self.isIndicatorSisurbano(nameIndicator)
			if(isIndicatorSisurbano):
				if(group == "ia"):
					self.listBuiltFields.addItem(nameIndicator)	
				elif(group == "ib"):
					self.listBioFields.addItem(nameIndicator)	
				elif(group == "ic"):
					self.listMobFields.addItem(nameIndicator)	
				elif(group == "id"):
					self.listSocioFields.addItem(nameIndicator)											
				items.append(item)
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in items]					
		# print(items)



		# 

