import sys
from PyQt4 import QtCore, QtGui

from ui_main_smsd import Ui_SMSD_Form
from powerDialog import PowerDetailsDialog
from ship import Ship

__version__ = 0.1

class SMSDForm(QtGui.QMainWindow, Ui_SMSD_Form):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.__powerDialog = None

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
        
        # Armaments Tab
        for name in self.ship.getCannonTypeDict():
            self.cannonTypeComboBox.addItem(name)
        for name in self.ship.getWeaponMountDict():
            self.cannonMountComboBox.addItem(name)
        for name in self.ship.getMultipleFMDict():
            self.cannonMultipleComboBox.addItem(name)
            
        self.on_massSpinBox_valueChanged(1)

    def updateMainStats(self):
        percentage = (self.ship.getTotalVolume() - self.ship.getVolumeUsed()) * 100.0 / self.ship.getTotalVolume()
        if percentage >= 0:
            self.volumeProgressBar.setValue(percentage)
            self.availableVolumeLabel.setText ("%0.2f of %d" % \
             (self.ship.getTotalVolume() - self.ship.getVolumeUsed(), self.ship.getTotalVolume()))
        else:
            self.volumeProgressBar.setValue(0)
            self.availableVolumeLabel.setText ("<font color=red><b>%0.2f of %d</b></font>" % \
            (self.ship.getTotalVolume() - self.ship.getVolumeUsed(), self.ship.getTotalVolume()))
        self.costLineEdit.setText ("%d" % self.ship.getTotalCost())
        self.classTableWidget.selectRow(self.ship.category - 1)  #TODO find the correct row

    @QtCore.pyqtSignature("int")
    def on_massSpinBox_valueChanged(self, mass):
        self.ship.setMass (mass)
        self.volumeSpinBox.setValue (self.ship.getTotalVolume())
        
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
            if  cat is not None:
                self.ship.changeHull(cat)
            else:
                print "No Valid hull!"      # TODO real error message
        self.landingGearChanged()
        self.streamlinedChanged()
        self.updatePowerStats()
        self.updateMainStats()

    def updateHullTable(self):
        hullTypeDict = self.ship.getHullTypeDict()
        line = 0
        for cat in hullTypeDict:
            self.hullTableWidget.item(line, 3).setText("%0.2f" % (self.ship.getTotalVolume() * hullTypeDict[cat][1]))  # Volume
            self.hullTableWidget.item(line, 5).setText("%d" % (self.ship.getTotalVolume() * hullTypeDict[cat][2]))  # Cost
            line += 1

    def updatePowerStats(self):
        self.powerVolumeLineEdit.setText("%0.2f" % self.ship.getVolume("power"))
        self.powerCostLineEdit.setText("%d" % self.ship.getCost("power"))
        if self.__powerDialog is not None:
            self.__powerDialog.updateTable(self.ship.getPowerDict())
            
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

    @QtCore.pyqtSignature("")
    def on_powerDetailsPushButton_clicked(self):
        if self.__powerDialog is None:
            self.__powerDialog = PowerDetailsDialog(self.ship.getPowerDict())
        self.__powerDialog.show()
        self.__powerDialog.raise_()

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

    def fuelStorageChanged(self, capacity):
        self.ship.changeFuelCapacity(capacity)
        self.updatePowerStats()
        self.updateMainStats()

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
    app = QtGui.QApplication (sys.argv)
    smsd = SMSDForm ()
    smsd.show ()
    sys.exit (app.exec_())
