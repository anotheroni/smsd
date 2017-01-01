import sys
from PyQt4 import QtCore, QtGui, uic

from powerDialog import PowerDetailsDialog
from controlPointDialog import ControlPointDetailsDialog
from ship import Ship

__version__ = 0.1

class SMSDForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # import ui from Qt file
        uic.loadUi('main_smsd.ui', self)
        
        self.__powerDialog = None
        self.__controlPointDialog = None

        # Connect Signals
        QtCore.QObject.connect(self.fuelStorageSpinBox,QtCore.SIGNAL("valueChanged(int)"), self.fuelStorageChanged)
        QtCore.QObject.connect(self.streamlinedCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.streamlinedChanged)
        QtCore.QObject.connect(self.landingGearCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.landingGearChanged)
        
        # Define Ship
        self.ship = Ship()
        self.rulesetNameLabel.setText(u"%s" % self.ship.rulesetName)
        
        shipClassDict = self.ship.getShipClassDict()
        self.classTableWidget.setRowCount(len(shipClassDict))
        line = 0
        for key in shipClassDict:
            item = QtGui.QTableWidgetItem()
            if shipClassDict[key][2] == sys.maxint:
                item.setText(u"%s+" % (shipClassDict[key][1]))
            else:
                item.setText(u"%s-%s" % (shipClassDict[key][1], shipClassDict[key][2]))
            self.classTableWidget.setItem(line, 0, item)
            item1 = QtGui.QTableWidgetItem()
            item1.setText(shipClassDict[key][0])
            self.classTableWidget.setItem(line, 1, item1)
            item2 = QtGui.QTableWidgetItem()
            item2.setText("%d" % key)
            self.classTableWidget.setItem(line, 2, item2)
            line += 1
            
        hullTypeDict = self.ship.getHullTypeDict()
        self.hullTableWidget.setRowCount(len(hullTypeDict))
        newHull = self.ship.findValidHull()
        line = 0
        for cat in hullTypeDict:
            if cat == newHull:
                newHullLine = line
            item1 = QtGui.QTableWidgetItem()
            item1.setText("%d" % cat)    # CAT
            self.hullTableWidget.setItem(line, 0, item1)
            item2 = QtGui.QTableWidgetItem()
            item2.setText(hullTypeDict[cat][0])  # Name
            self.hullTableWidget.setItem(line, 1, item2)
            item3 = QtGui.QTableWidgetItem()
            item3.setText("%0.2f" % hullTypeDict[cat][1])  # Volume Factor
            self.hullTableWidget.setItem(line, 2, item3)
            item4 = QtGui.QTableWidgetItem()
            item4.setText("%0.2f" % (self.ship.getTotalVolume() * hullTypeDict[cat][1]))  # Volume
            self.hullTableWidget.setItem(line, 3, item4)
            item5 = QtGui.QTableWidgetItem()
            item5.setText("%0.1f" % hullTypeDict[cat][2])  # Cost Multiplier
            self.hullTableWidget.setItem(line, 4, item5)
            item6 = QtGui.QTableWidgetItem()
            item6.setText("%d" % (self.ship.getTotalVolume() * hullTypeDict[cat][2]))  # Cost
            self.hullTableWidget.setItem(line, 5, item6)
            item7 = QtGui.QTableWidgetItem()
            item7.setText("%d" % hullTypeDict[cat][3])  # Min Mass
            self.hullTableWidget.setItem(line, 6, item7)
            item8 = QtGui.QTableWidgetItem()
            if hullTypeDict[cat][4] is not None:
                item8.setText("%d" % hullTypeDict[cat][4])  # Max Mass
            else:
                item8.setText(u"-")  # Max Mass
            self.hullTableWidget.setItem(line, 7, item8)
            line += 1
        if newHull is None:
            print "ERROR: Can't find a valid Hull"  #TODO better error handling
        else:
            self.ship.changeHull(newHull)
            self.hullTableWidget.selectRow(newHullLine)
        
        # Drives Tab
        sdtDict = self.ship.getSublightDriveTypesDict()
        self.sublightDriveTableWidget.setRowCount(len(sdtDict))
        line = 0
        for rating, data in sdtDict.items():
            item1 = QtGui.QTableWidgetItem()
            item1.setText("%d" % rating)
            self.sublightDriveTableWidget.setItem(line, 0, item1)
            item2 = QtGui.QTableWidgetItem()
            item2.setText("%0.1f" % data[0])
            self.sublightDriveTableWidget.setItem(line, 1, item2)
            item3 = QtGui.QTableWidgetItem()
            item3.setText("%d" % data[1])
            self.sublightDriveTableWidget.setItem(line, 2, item3)
            (volume, cost) = self.ship.getSublightDriveCost(rating)
            item4 = QtGui.QTableWidgetItem()
            item4.setText("%0.2f" % volume)
            self.sublightDriveTableWidget.setItem(line, 3, item4)
            item5 = QtGui.QTableWidgetItem()
            item5.setText("%d" % cost)
            self.sublightDriveTableWidget.setItem(line, 4, item5)
            line += 1
        self.sublightDriveTableWidget.selectRow(0)  #TODO
        
        tdtDict = self.ship.getTranslightDriveTypesDict()
        self.translightDriveTableWidget.setRowCount(len(tdtDict))
        line = 0
        for rating, data in tdtDict.items():
            item1 = QtGui.QTableWidgetItem()
            item1.setText("%d" % rating)
            self.translightDriveTableWidget.setItem(line, 0, item1)
            item2 = QtGui.QTableWidgetItem()
            item2.setText("%0.1f" % data)
            self.translightDriveTableWidget.setItem(line, 1, item2)
            (volume, cost) = self.ship.getTranslightDriveCost(rating)
            item4 = QtGui.QTableWidgetItem()
            item4.setText("%0.2f" % volume)
            self.translightDriveTableWidget.setItem(line, 2, item4)
            item5 = QtGui.QTableWidgetItem()
            item5.setText("%d" % cost)
            self.translightDriveTableWidget.setItem(line, 3, item5)
            line += 1
        self.translightDriveTableWidget.selectRow(0)  #TODO
        
        # Systems Tab
        sysDict = self.ship.getSystemMkDict()
        self.systemMkTableWidget.setRowCount(len(sysDict))
        self.systemMkTableWidget.setColumnCount(4)
        #QTableWidget::setCellWidget()
        line = 0
        for name, data in sysDict.items():
            item0 = QtGui.QTableWidgetItem()
            item0.setText("%s" % name)
            self.systemMkTableWidget.setItem(line, 0, item0)            
            item1 = QtGui.QTableWidgetItem()
            item1.setText("%d" % data[0])
            self.systemMkTableWidget.setItem(line, 1, item1)
            line += 1
        
        # Armaments Tab
        for name in self.ship.getWeaponMountDict():
            self.cannonMountComboBox.addItem(name)
        for name in self.ship.getMultipleFMDict():
            self.cannonMultipleComboBox.addItem(name)
        for name in self.ship.getWeaponHudDict():
            self.cannonHudComboBox.addItem(name)
        for name in self.ship.getCannonTypeDict():
            self.cannonTypeComboBox.addItem(name)
        QtCore.QObject.connect(self.cannonMountComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateCannonCost)
        QtCore.QObject.connect(self.cannonMultipleComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateCannonCost)
        QtCore.QObject.connect(self.cannonMkComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateCannonCost)
        QtCore.QObject.connect(self.cannonHudComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateCannonCost)
        
        self.on_massSpinBox_valueChanged(1)

#------------------------------------------------------------------------------
# MAIN Tab

    def updateMainStats(self):
        percentage = (self.ship.getTotalVolume() - self.ship.getVolumeUsed()) * 100.0 / self.ship.getTotalVolume()
        self.totalVolumeLabel.setText("Total Volume: %d Cumets" % self.ship.getTotalVolume())        
        if percentage >= 0:
            self.volumeProgressBar.setValue(percentage)
            self.availableVolumeLabel.setText ("Available Volume: %0.2f" % \
                (self.ship.getTotalVolume() - self.ship.getVolumeUsed()))
        else:
            self.volumeProgressBar.setValue(0)
            self.availableVolumeLabel.setText ("<font color=red><b>Available Volume: %0.2f</b></font>" % \
                (self.ship.getTotalVolume() - self.ship.getVolumeUsed()))
        self.costLineEdit.setText ("%d" % self.ship.getTotalCost())
        self.classTableWidget.selectRow(self.ship.category - 1)  #TODO find the correct row

    @QtCore.pyqtSignature("int")
    def on_massSpinBox_valueChanged(self, mass):
        self.ship.setMass (mass)
        
        # Armor Belt
        self.ship.updateArmorBelt(self.armorBeltComboBox.currentIndex())
        self.armorBeltCostLineEdit.setText("%d" % self.ship.getCost("Armor Belt"))        

        # Update RIF
        self.ship.addVolume ("RIF", self.ship.getTotalVolume() * 0.01)
        self.rifVolumeLineEdit.setText ("%.2f" % (self.ship.getTotalVolume() * 0.01))
        self.ship.addCost ("RIF", ((mass * 100) + 10000))
        self.rifCostLineEdit.setText ("%d" % ((mass * 100) + 10000))

        # Update Power
        self.ship.addPower("Base", mass * 0.01)

        self.updateHullTable()
        if not self.ship.changeHull(self.ship.getHull()):
            cat = self.ship.findValidHull()
            if cat is not None:
                self.ship.changeHull(cat)
            else:
                print "No Valid hull!"      # TODO real error message
        self.updateSublightTable()
        self.updateTranslightTable()
        self.landingGearChanged()
        self.streamlinedChanged()
        self.updatePowerStats()
        self.updateControlPointStats()
        self.updateMainStats()

    def updateHullTable(self):
        hullTypeDict = self.ship.getHullTypeDict()
        line = 0
        for cat in hullTypeDict:
            self.hullTableWidget.item(line, 3).setText("%0.2f" % (self.ship.getTotalVolume() * hullTypeDict[cat][1]))  # Volume
            self.hullTableWidget.item(line, 5).setText("%d" % (self.ship.getTotalVolume() * hullTypeDict[cat][2]))  # Cost
            line += 1

    @QtCore.pyqtSignature("int,int,int,int")
    def on_hullTableWidget_currentCellChanged(self, newrow, newcol, oldrow, oldcol):
        if (newrow == oldrow):  # Same row, no change
            return
        #print "Cell Changed %d %d %d %d" % (newrow, newcol, oldrow, oldcol)
        item = self.hullTableWidget.item(newrow, 0)
        cat = item.text().toInt()
        if self.ship.changeHull(cat[0]):
            self.updateMainStats()
        else:
            self.hullTableWidget.selectRow(oldrow)
            print "New hull not valid! %d" % oldrow     # TODO better error message

    @QtCore.pyqtSignature("int")
    def on_armorBeltComboBox_currentIndexChanged(self, index):
        self.ship.updateArmorBelt(index)
        self.armorBeltCostLineEdit.setText("%d" % self.ship.getCost("Armor Belt"))
        self.updateMainStats()

    def streamlinedChanged(self):
        stState = self.streamlinedCheckBox.isChecked()
        self.ship.streamlinedChanged(stState)
        self.streamlinedCostLineEdit.setText(self.ship.getStreamlinedCost())
        self.updateMainStats()

#------------------------------------------------------------------------------
# DRIVES Tab

    @QtCore.pyqtSignature("int,int,int,int")
    def on_sublightDriveTableWidget_currentCellChanged(self, newrow, newcol, oldrow, oldcol):
        if (newrow == oldrow):  # Same row, no change
            return
        item = self.sublightDriveTableWidget.item(newrow, 0)
        rating = item.text().toInt()[0]
        self.ship.changeSublightDrive(rating)
        self.updatePowerStats()
        self.updateControlPointStats()     
        self.updateMainStats()

    @QtCore.pyqtSignature("int,int,int,int")
    def on_translightDriveTableWidget_currentCellChanged(self, newrow, newcol, oldrow, oldcol):
        if (newrow == oldrow):  # Same row, no change
            return
        item = self.translightDriveTableWidget.item(newrow, 0)
        rating = item.text().toInt()[0]
        self.ship.changeTranslightDrive(rating)
        self.updateControlPointStats()
        self.updateMainStats()
        
    @QtCore.pyqtSignature("")
    def on_powerDetailsPushButton_clicked(self):
        if self.__powerDialog is None:
            self.__powerDialog = PowerDetailsDialog(self.ship.getPowerDict())
        self.__powerDialog.show()
        self.__powerDialog.raise_()

    def fuelStorageChanged(self, capacity):
        self.ship.changeFuelCapacity(capacity)
        self.updatePowerStats()
        self.updateMainStats()

    def updatePowerStats(self):
        self.powerVolumeLineEdit.setText("%0.2f" % self.ship.getVolume("power"))
        self.powerCostLineEdit.setText("%d" % self.ship.getCost("power"))
        if self.__powerDialog is not None:
            self.__powerDialog.updateTable(self.ship.getPowerDict())
    
    def updateSublightTable(self):
        sdtDict = self.ship.getSublightDriveTypesDict()
        line = 0
        for rating, data in sdtDict.items():
            (volume, cost) = self.ship.getSublightDriveCost(rating)
            item4 = QtGui.QTableWidgetItem()
            item4.setText("%0.2f" % volume)
            self.sublightDriveTableWidget.setItem(line, 3, item4)
            item5 = QtGui.QTableWidgetItem()
            item5.setText("%d" % cost)
            self.sublightDriveTableWidget.setItem(line, 4, item5)
            line += 1
    
    def updateTranslightTable(self):
        tdtDict = self.ship.getTranslightDriveTypesDict()
        line = 0
        for rating, data in tdtDict.items():
            (volume, cost) = self.ship.getTranslightDriveCost(rating)
            item4 = QtGui.QTableWidgetItem()
            item4.setText("%0.2f" % volume)
            self.translightDriveTableWidget.setItem(line, 2, item4)
            item5 = QtGui.QTableWidgetItem()
            item5.setText("%d" % cost)
            self.translightDriveTableWidget.setItem(line, 3, item5)
            line += 1     

#------------------------------------------------------------------------------
# SYSTEMS Tab

    def landingGearChanged(self):
        lgState = self.landingGearCheckBox.isChecked()
        self.ship.changeLandingGear(lgState)
        self.landingGearVolumeLineEdit.setText(self.ship.getLandingGearVolume())
        self.landingGearCostLineEdit.setText(self.ship.getLandingGearCost())
        self.updateMainStats()
    
    @QtCore.pyqtSignature("int")
    def on_deflectorRatingSpinBox_valueChanged(self,value):
        self.ship.updateDeflectorScreen(value)
        self.deflectorBonusLineEdit.setText("+%d" % self.ship.getDeflectorScreenBonus())
        self.deflectorVolumeLineEdit.setText("%0.2f" % self.ship.getVolume("deflector"))
        self.deflectorCostLineEdit.setText("%d" % self.ship.getCost("deflector"))
        self.updatePowerStats()
        self.updateMainStats()

    def updateControlPointStats(self):
        self.controlPointsLineEdit.setText("%0.1f" % self.ship.getTotalControlPoints())
        if self.__controlPointDialog is not None:
            self.__controlPointDialog.updateTable(self.ship.getControlPointDict())
        self.updateMinComputerMk()
        self.updateControlPointsLeft()

    def updateControlPointsLeft(self):
        cptleft = self.ship.getControlPointsLeft()
        if cptleft < 0.0:
            self.controlPointsLeftLabel.setText("<font color=red><b>%0.1f</b></font>" % cptleft)
        else:
            self.controlPointsLeftLabel.setText("%0.1f" % cptleft)

    @QtCore.pyqtSignature("")
    def on_controlPointDetailsPushButton_clicked(self):
        if self.__controlPointDialog is None:
            self.__controlPointDialog = ControlPointDetailsDialog(self.ship.getControlPointDict())
        self.__controlPointDialog.show()
        self.__controlPointDialog.raise_()

    @QtCore.pyqtSignature("int")
    def on_crewSpinBox_valueChanged(self, crew):
        (volume, cost) = self.ship.changeCrew(crew)
        self.controlAreasVolumeLineEdit.setText("%d" % volume)
        self.controlAreasCostLineEdit.setText("%d" % cost)
        self.controlPointsCrewLineEdit.setText("%d" % crew)
        self.updateControlPointsLeft()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_computerMkSpinBox_valueChanged(self, cMk):
        (volume, cost) = self.ship.changeComputerMk(cMk)
        self.computerVolumeLineEdit.setText(u"%0.2f" % volume)
        self.computerCostLineEdit.setText(u"%d" % cost)
        self.controlPointsComputerLineEdit.setText("%d" % cMk)
        self.updateControlPointsLeft()        
        self.updateMainStats()

    def updateMinComputerMk(self):
        minMk = self.ship.getMinComputerMk()
        oldMin = self.computerMkSpinBox.minimum()
        cvalue = self.computerMkSpinBox.value()
        if cvalue < minMk:
            self.computerMkSpinBox.setValue(minMk)
        if oldMin != minMk:
            self.computerMkSpinBox.setMinimum(minMk)

#------------------------------------------------------------------------------
# ARMAMENTS Tab

    @QtCore.pyqtSignature("int")
    def on_cannonTypeComboBox_currentIndexChanged(self, index):
        cannonType = self.cannonTypeComboBox.itemText(index)
        try:
            data = self.ship.getCannonTypeDict()[cannonType]
        except KeyError:
            print "ERROR can't find cannon type %s" % cannonType
            return
        
        # Update Mk ComboBox
        self.cannonMkComboBox.blockSignals(True)    # Prevent signal loop
        mkIndex = self.cannonMkComboBox.currentIndex()
        self.cannonMkComboBox.clear() # Empty all Mk
        for mk in range(data[3], data[4] + 1):  # MinMk, MaxMk
            self.cannonMkComboBox.addItem(u"%d" % mk)
        if mkIndex != -1:
            self.cannonMkComboBox.setCurrentIndex (mkIndex)
        self.cannonMkComboBox.blockSignals(False)
        
        # Update Magazine widgets
        if data[5] is None:
            self.cannonMagazineLabel.hide()
            self.cannonMagazineSpinBox.hide()
        else:
            self.cannonMagazineLabel.show()
            self.cannonMagazineSpinBox.show()
        self.updateCannonCost()
    
    def updateCannonCost(self):
        cType = self.cannonTypeComboBox.itemText(self.cannonTypeComboBox.currentIndex())
        cMk = self.cannonMkComboBox.itemText(self.cannonMkComboBox.currentIndex())
        cMount = self.cannonMountComboBox.itemText(self.cannonMountComboBox.currentIndex())
        cMult = self.cannonMultipleComboBox.itemText(self.cannonMultipleComboBox.currentIndex())
        cHud = self.cannonHudComboBox.itemText(self.cannonHudComboBox.currentIndex())
        cMag = self.cannonMagazineSpinBox.value()
        costTup = self.ship.calculateCannonCost(cType, cMk, cMount, cMult, cHud, cMag)
        self.cannonVolumeLineEdit.setText(u"%d" % costTup[0])
        self.cannonCostLineEdit.setText(u"%d" % costTup[1])
        if costTup[0] == 0:
            self.cannonAddPushButton.setEnabled(False)
        else:
            self.cannonAddPushButton.setEnabled(True)

    @QtCore.pyqtSignature("")
    def on_cannonAddPushButton_clicked(self):
        cType = self.cannonTypeComboBox.itemText(self.cannonTypeComboBox.currentIndex())
        cMk = self.cannonMkComboBox.itemText(self.cannonMkComboBox.currentIndex())
        cMount = self.cannonMountComboBox.itemText(self.cannonMountComboBox.currentIndex())
        cMult = self.cannonMultipleComboBox.itemText(self.cannonMultipleComboBox.currentIndex())
        cHud = self.cannonHudComboBox.itemText(self.cannonHudComboBox.currentIndex())
        cMag = self.cannonMagazineSpinBox.value()
        (volume, cost) = self.ship.addCannon(cType, cMk, cMount, cMult, cHud, cMag)
        
        line = self.armamentsTableWidget.rowCount()
        self.armamentsTableWidget.setRowCount(line + 1)        
        item1 = QtGui.QTableWidgetItem()
        item1.setText(cType)
        self.armamentsTableWidget.setItem(line, 0, item1)
        item2 = QtGui.QTableWidgetItem()
        item2.setText("Mk.%s %s" % (cMk, cMult))
        self.armamentsTableWidget.setItem(line, 1, item2)
        item3 = QtGui.QTableWidgetItem()
        item3.setText(cMount)
        self.armamentsTableWidget.setItem(line, 2, item3)
        item4 = QtGui.QTableWidgetItem()
        item4.setText(cHud)
        self.armamentsTableWidget.setItem(line, 3, item4)
        item5 = QtGui.QTableWidgetItem()
        item5.setText("%d" % volume)
        self.armamentsTableWidget.setItem(line, 4, item5)
        item6 = QtGui.QTableWidgetItem()
        item6.setText("%d" % cost)
        self.armamentsTableWidget.setItem(line, 5, item6)
        
        self.updatePowerStats()
        self.updateControlPointStats()
        self.updateMainStats()


#------------------------------------------------------------------------------
# FACILITIES Tab

    @QtCore.pyqtSignature("int")
    def on_accommodationCrewSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_crew", value)
        self.accommodationsCrewCostLineEdit.setText("%d" % self.ship.getCost("acc_crew"))
        self.accommodationsCrewVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_crew"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationFirstSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_first", value)
        self.accommodationsFirstCostLineEdit.setText("%d" % self.ship.getCost("acc_first"))
        self.accommodationsFirstVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_first"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationStandardSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_standard", value)
        self.accommodationsStandardCostLineEdit.setText("%d" % self.ship.getCost("acc_standard"))
        self.accommodationsStandardVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_standard"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationLowSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_low", value)
        self.accommodationsLowCostLineEdit.setText("%d" % self.ship.getCost("acc_low"))
        self.accommodationsLowVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_low"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationCryogenicSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_cryo", value)
        self.accommodationsCryogenicCostLineEdit.setText("%d" % self.ship.getCost("acc_cryo"))
        self.accommodationsCryogenicVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_cryo"))
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationSeatingSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_seating", value)
        self.accommodationsSeatingCostLineEdit.setText("%d" % self.ship.getCost("acc_seating"))
        self.accommodationsSeatingVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_seating"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()
    
    def updateRecreationalLifeSupport(self):
        self.recreationalNumberLineEdit.setText("%d" % self.ship.getRecreational())
        self.recreationalCostLineEdit.setText("%d" % self.ship.getCost("recreational"))
        self.recreationalVolumeLineEdit.setText("%d" % self.ship.getVolume("recreational"))
        self.lifeSupportNumberLineEdit.setText("%d" % self.ship.getLifeSupport())
        self.lifeSupportCostLineEdit.setText("%d" % self.ship.getCost("lifesupport"))
        self.lifeSupportVolumeLineEdit.setText("%d" % self.ship.getVolume("lifesupport"))
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    smsd = SMSDForm()
    smsd.show()
    sys.exit(app.exec_())
