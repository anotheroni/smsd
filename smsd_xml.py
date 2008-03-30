from PyQt4.QtXml import *
from PyQt4 import QtCore
import sys

class SaxSMSDRulesHandler(QXmlDefaultHandler):
    
    def __init__(self, ship):
        super(SaxSMSDRulesHandler, self).__init__()
        self.ship = ship
        self.__text = QtCore.QString()

    def startElement(self, namespaceURI, localName, qName, attributes):
        if qName == "NAME":
            self.__text = QtCore.QString()
        elif qName == "SHIP_CLASS":
            cat = attributes.value("category").toInt()
            min = attributes.value("min_mass").toInt()
            max = attributes.value("max_mass")
            if max == "+":
                max = [sys.maxint]
            else:
                max = max.toInt()
            self.ship.addShipClass(cat[0], attributes.value("name"), min[0], max[0])
        return True
    
    def characters(self, text):
        self.__text += text
        return True
    
    def endElement(self, namespaceURI, localName, qName):
        if qName == "NAME":
            self.ship.rulesetName = self.__text.trimmed()
            print "NAME: %s" % self.__text
        return True
    
    def endDocument(self):
        return True
        
    
    def fatalError(self, exception):
        self.error = "parse error at line %d column %d: %s" % \
            (exception.lineNumber(), exception.columnNumber(), \
            exception.message())
        return False
    