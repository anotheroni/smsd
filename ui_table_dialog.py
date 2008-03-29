# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'table_dialog.ui'
#
# Created: Sat Mar 29 10:14:39 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TableDialog(object):
    def setupUi(self, TableDialog):
        TableDialog.setObjectName("TableDialog")
        TableDialog.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(TableDialog.minimumSizeHint()))

        self.widget = QtGui.QWidget(TableDialog)
        self.widget.setGeometry(QtCore.QRect(10,10,258,227))
        self.widget.setObjectName("widget")

        self.vboxlayout = QtGui.QVBoxLayout(self.widget)
        self.vboxlayout.setObjectName("vboxlayout")

        self.tableWidget = QtGui.QTableWidget(self.widget)
        self.tableWidget.setObjectName("tableWidget")
        self.vboxlayout.addWidget(self.tableWidget)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.closePushButton = QtGui.QPushButton(self.widget)
        self.closePushButton.setObjectName("closePushButton")
        self.hboxlayout.addWidget(self.closePushButton)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(TableDialog)
        QtCore.QObject.connect(self.closePushButton,QtCore.SIGNAL("clicked()"),TableDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(TableDialog)

    def retranslateUi(self, TableDialog):
        TableDialog.setWindowTitle(QtGui.QApplication.translate("TableDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.closePushButton.setText(QtGui.QApplication.translate("TableDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

