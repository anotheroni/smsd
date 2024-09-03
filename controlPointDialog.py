import sys
from PyQt5 import QtCore, QtWidgets, uic

class ControlPointDetailsDialog(QtWidgets.QDialog):

    def __init__(self, ctrlDict):
        super().__init__()

        # import ui from Qt file
        uic.loadUi('table_dialog.ui', self)
        
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["System", "Rating"])
        
        self.updateTable(ctrlDict)
        
        self.setWindowTitle("Control Points")

    def updateTable(self, cntrlDict):
        self.tableWidget.setRowCount(len(cntrlDict))
        
        for line, (key, value) in enumerate(cntrlDict.items()):
            self.tableWidget.setItem(line, 0, QtWidgets.QTableWidgetItem(key))
            self.tableWidget.setItem(line, 1, QtWidgets.QTableWidgetItem(f"{value:.2f}"))
