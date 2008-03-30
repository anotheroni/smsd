import sys
from PyQt4 import QtCore, QtGui

from ui_main_smsd import Ui_SMSD_Form
from powerDialog import PowerDetailsDialog
from ship import Ship

__version__ = 0.1

class SMSDForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SMSD_Form()
        self.ui.setupUi(self)
        
        self.__powerDialog = None

        # Connect Signals
        QtCore.QObject.connect(self.ui.fuelStorageSpinBox,QtCore.SIGNAL("valueChanged(int)"), self.fuelStorageChanged)
        QtCore.QObject.connect(self.ui.streamlinedCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.streamlinedChanged)
        QtCore.QObject.connect(self.ui.landingGearCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.landingGearChanged)
        
        # Define Ship
        self.ship = Ship()
        self.ui.rulesetNameLabel.setText(u"%s" % self.ship.rulesetName)
        
        shipClassDict = self.ship.getShipClassDict()
        self.ui.classTableWidget.setRowCount(len(shipClassDict))
        line = 0
        for key in shipClassDict:
            item = QtGui.QTableWidgetItem()
            if shipClassDict[key][2] == sys.maxint:
                item.setText(u"%s+" % (shipClassDict[key][1]))
            else:
                item.setText(u"%s-%s" % (shipClassDict[key][1], shipClassDict[key][2]))
            self.ui.classTableWidget.setItem(line, 0, item)
            item1 = QtGui.QTableWidgetItem()
            item1.setText(shipClassDict[key][0])
            self.ui.classTableWidget.setItem(line, 1, item1)
            item2 = QtGui.QTableWidgetItem()
            item2.setText("%d" % key)
            self.ui.classTableWidget.setItem(line, 2, item2)
            line += 1
        
        self.on_massSpinBox_valueChanged(1)

    def updateMainStats(self):
        percentage = (self.ship.getTotalVolume() - self.ship.getVolumeUsed()) * 100.0 / self.ship.getTotalVolume()
        if percentage >= 0:
            self.ui.volumeProgressBar.setValue(percentage)
            self.ui.availableVolumeLabel.setText ("%0.2f of %d" % \
             (self.ship.getTotalVolume() - self.ship.getVolumeUsed(), self.ship.getTotalVolume()))
        else:
            self.ui.volumeProgressBar.setValue(0)
            self.ui.availableVolumeLabel.setText ("<font color=red><b>%0.2f of %d</b></font>" % \
            (self.ship.getTotalVolume() - self.ship.getVolumeUsed(), self.ship.getTotalVolume()))
        self.ui.costLineEdit.setText ("%d" % self.ship.getTotalCost())
        self.ui.classTableWidget.selectRow(self.ship.category - 1)  #TODO find the correct row

    @QtCore.pyqtSignature("int")
    def on_massSpinBox_valueChanged(self, mass):
        self.ship.setMass (mass)
        self.ui.volumeSpinBox.setValue (self.ship.getTotalVolume())
        
        # Armor Belt
        self.ship.updateArmorBelt(self.ui.armorBeltComboBox.currentIndex())
        self.ui.armorBeltCostLineEdit.setText("%d" % self.ship.getCost("Armor Belt"))        

        # Update RIF
        self.ship.addVolume ("RIF", self.ship.getTotalVolume() * 0.01)
        self.ui.rifVolumeLineEdit.setText ("%.2f" % (self.ship.getTotalVolume() * 0.01))
        self.ship.addCost ("RIF", ((mass * 100) + 10000))
        self.ui.rifCostLineEdit.setText ("%d" % ((mass * 100) + 10000))

        # Update Power
        self.ship.addPower("Base", mass * 0.01)

        self.landingGearChanged()
        self.streamlinedChanged()
        self.updatePowerStats()
        self.updateMainStats()
    
    def updatePowerStats(self):
        self.ui.powerVolumeLineEdit.setText("%0.2f" % self.ship.getVolume("power"))
        self.ui.powerCostLineEdit.setText("%d" % self.ship.getCost("power"))
        if self.__powerDialog is not None:
            self.__powerDialog.updateTable(self.ship.getPowerDict())

    @QtCore.pyqtSignature("")
    def on_powerDetailsPushButton_clicked(self):
        if self.__powerDialog is None:
            self.__powerDialog = PowerDetailsDialog(self.ship.getPowerDict())
        self.__powerDialog.show()
        self.__powerDialog.raise_()

    @QtCore.pyqtSignature("int")
    def on_armorBeltComboBox_currentIndexChanged(self,  index):
        self.ship.updateArmorBelt(index)
        self.ui.armorBeltCostLineEdit.setText("%d" % self.ship.getCost("Armor Belt"))
        self.updateMainStats()

    def streamlinedChanged(self):
        stState = self.ui.streamlinedCheckBox.isChecked()
        self.ship.streamlinedChanged(stState)
        self.ui.streamlinedCostLineEdit.setText(self.ship.getStreamlinedCost())
        self.updateMainStats()

    def fuelStorageChanged(self, capacity):
        self.ship.changeFuelCapacity(capacity)
        self.updatePowerStats()
        self.updateMainStats()

    def landingGearChanged(self):
        lgState = self.ui.landingGearCheckBox.isChecked()
        self.ship.changeLandingGear(lgState)
        self.ui.landingGearVolumeLineEdit.setText(self.ship.getLandingGearVolume())
        self.ui.landingGearCostLineEdit.setText(self.ship.getLandingGearCost())
        self.updateMainStats()
    
    @QtCore.pyqtSignature("int")
    def on_deflectorRatingSpinBox_valueChanged(self,value):
        self.ship.updateDeflectorScreen(value)
        self.ui.deflectorBonusLineEdit.setText("+%d" % self.ship.getDeflectorScreenBonus())
        self.ui.deflectorVolumeLineEdit.setText("%0.2f" % self.ship.getVolume("deflector"))
        self.ui.deflectorCostLineEdit.setText("%d" % self.ship.getCost("deflector"))
        self.updatePowerStats()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationCrewSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_crew", value)
        self.ui.accommodationsCrewCostLineEdit.setText("%d" % self.ship.getCost("acc_crew"))
        self.ui.accommodationsCrewVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_crew"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationFirstSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_first", value)
        self.ui.accommodationsFirstCostLineEdit.setText("%d" % self.ship.getCost("acc_first"))
        self.ui.accommodationsFirstVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_first"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationStandardSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_standard", value)
        self.ui.accommodationsStandardCostLineEdit.setText("%d" % self.ship.getCost("acc_standard"))
        self.ui.accommodationsStandardVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_standard"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationLowSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_low", value)
        self.ui.accommodationsLowCostLineEdit.setText("%d" % self.ship.getCost("acc_low"))
        self.ui.accommodationsLowVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_low"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationCryogenicSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_cryo", value)
        self.ui.accommodationsCryogenicCostLineEdit.setText("%d" % self.ship.getCost("acc_cryo"))
        self.ui.accommodationsCryogenicVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_cryo"))
        self.updateMainStats()

    @QtCore.pyqtSignature("int")
    def on_accommodationSeatingSpinBox_valueChanged(self, value):
        self.ship.addAccommodations("acc_seating", value)
        self.ui.accommodationsSeatingCostLineEdit.setText("%d" % self.ship.getCost("acc_seating"))
        self.ui.accommodationsSeatingVolumeLineEdit.setText("%d" % self.ship.getVolume("acc_seating"))
        self.updateRecreationalLifeSupport()
        self.updateMainStats()
    
    def updateRecreationalLifeSupport(self):
        self.ui.recreationalNumberLineEdit.setText("%d" % self.ship.getRecreational())
        self.ui.recreationalCostLineEdit.setText("%d" % self.ship.getCost("recreational"))
        self.ui.recreationalVolumeLineEdit.setText("%d" % self.ship.getVolume("recreational"))
        self.ui.lifeSupportNumberLineEdit.setText("%d" % self.ship.getLifeSupport())
        self.ui.lifeSupportCostLineEdit.setText("%d" % self.ship.getCost("lifesupport"))
        self.ui.lifeSupportVolumeLineEdit.setText("%d" % self.ship.getVolume("lifesupport"))

    
if __name__ == "__main__":
    app = QtGui.QApplication (sys.argv)
    smsd = SMSDForm ()
    smsd.show ()
    sys.exit (app.exec_())
