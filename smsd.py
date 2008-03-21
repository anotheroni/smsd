import sys
from PyQt4 import QtCore, QtGui

from ui_main_smsd import Ui_SMSD_Form
from ship import Ship

__version__ = 0.1

class SMSDForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SMSD_Form()
        self.ui.setupUi(self)

        # Connect Signals
        QtCore.QObject.connect(self.ui.massSpinBox,QtCore.SIGNAL("valueChanged(int)"),self.massChanged)
        QtCore.QObject.connect(self.ui.fuelStorageSpinBox,QtCore.SIGNAL("valueChanged(int)"), self.fuelStorageChanged)
        QtCore.QObject.connect(self.ui.streamlinedCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.streamlinedChanged)
        QtCore.QObject.connect(self.ui.landingGearCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.landingGearChanged)

        # Define Ship
        self.ship = Ship()
        self.massChanged(1)

    def updateMainStats(self):
        self.ui.volumeProgressBar.setValue ((self.ship.volume - self.ship.getVolumeUsed()) * 100.0 / self.ship.volume)
        self.ui.availableVolumeLabel.setText ("%0.2f of %d" % (self.ship.volume - self.ship.getVolumeUsed(), self.ship.volume))
        self.ui.costLineEdit.setText ("%d" % self.ship.getCost())

    def massChanged(self, mass):
        self.ship.setMass (mass)
        self.ui.volumeSpinBox.setValue (self.ship.volume)

        # Update RIF
        self.ship.addVolume ("RIF", self.ship.volume * 0.01)
        self.ui.rifVolumeLineEdit.setText ("%.2f" % (self.ship.volume * 0.01))
        self.ship.addCost ("RIF", ((mass * 100) + 10000))
        self.ui.rifCostLineEdit.setText ("%d" % ((mass * 100) + 10000))

        # Update Power
        self.ship.addPower("mass", mass * 0.01)
        self.ui.powerVolumeLineEdit.setText("%0.2f" % self.ship.getPowerRating() * (self.ship.category ** 2))
        self.ui.powerCostLineEdit.setText("%d" % (self.ship.getPowerRating() * (self.ship.category ** 2) * 500 + 50000))

        self.landingGearChanged()
        self.streamlinedChanged()
        self.updateMainStats()

    def streamlinedChanged(self):
        stState = self.ui.streamlinedCheckBox.isChecked()
        self.ship.streamlinedChanged(stState)
        self.ui.streamlinedCostLineEdit.setText(self.ship.getStreamlinedCost())
        self.updateMainStats()
        
    def fuelStorageChanged(self):
        pass    #TODO

    def landingGearChanged(self):
        lgState = self.ui.landingGearCheckBox.isChecked()
        self.ship.landingGearChanged(lgState)
        self.ui.landingGearVolumeLineEdit.setText(self.ship.getLandingGearVolume())
        self.ui.landingGearCostLineEdit.setText(self.ship.getLandingGearCost())
        self.updateMainStats()


if __name__ == "__main__":
    app = QtGui.QApplication (sys.argv)
    smsd = SMSDForm ()
    smsd.show ()
    sys.exit (app.exec_())
