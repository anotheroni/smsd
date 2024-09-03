import sys
from PyQt5 import QtCore, QtWidgets, uic

class PowerDetailsDialog(QtWidgets.QDialog):

    def __init__(self, pwrDict):
        super().__init__()

        # import ui from Qt file
        uic.loadUi('table_dialog.ui', self)

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["System", "Rating"])
        
        self.updateTable(pwrDict)
        
        self.setWindowTitle("Power Usage")

    def updateTable(self, pwrDict):
        self.tableWidget.setRowCount(len(pwrDict))
        
        for line, (key, value) in enumerate(pwrDict.items()):
            self.tableWidget.setItem(line, 0, QtWidgets.QTableWidgetItem(key))
            self.tableWidget.setItem(line, 1, QtWidgets.QTableWidgetItem(f"{value:.2f}"))
