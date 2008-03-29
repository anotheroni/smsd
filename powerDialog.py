import sys
from PyQt4 import QtCore, QtGui

from ui_table_dialog import Ui_TableDialog

class PowerDetailsDialog(QtGui.QDialog, Ui_TableDialog):

    def __init__(self, pwrDict):
        super(PowerDetailsDialog, self).__init__()
        
        self.setupUi(self)
        
        self.tableWidget.setColumnCount(2)
        
        self.updateTable(pwrDict)
        
        self.setWindowTitle(QtGui.QApplication.translate("PowerDialog", "Power Usage", None, QtGui.QApplication.UnicodeUTF8))

    def updateTable(self,  pwrDict):
        self.tableWidget.setRowCount(len(pwrDict))
        
        line=0
        for key in pwrDict:
            item = QtGui.QTableWidgetItem()
            item.setText(QtGui.QApplication.translate("PowerDialog", key, None, QtGui.QApplication.UnicodeUTF8))
            self.tableWidget.setItem(line,0,item)
            item1 = QtGui.QTableWidgetItem()
            item1.setText(QtGui.QApplication.translate("PowerDialog", "%0.2f" % pwrDict[key], None, QtGui.QApplication.UnicodeUTF8))
            self.tableWidget.setItem(line,1,item1)
            line += 1

