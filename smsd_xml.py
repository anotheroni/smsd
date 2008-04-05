from PyQt4.QtXml import *
from PyQt4 import QtCore
import sys

class SaxSMSDRulesHandler(QXmlDefaultHandler):
    
    def __init__(self, ship):
        super(SaxSMSDRulesHandler, self).__init__()
        self.ship = ship
        self.__mode = None
        self.__text = QtCore.QString()
        self.__hull_cat = None
        self.__hull_vol = None
        self.__hull_cost = None
        self.__hull_name = None
        self.__hull_max = None
        self.__hull_min = None
        self.__cannon_name = None
        self.__cannon_volume = None
        self.__cannon_basecost = None
        self.__cannon_costmul = None
        self.__cannon_minmx = None
        self.__cannon_maxmx = None
        self.__magazine = None
        
        self.__mode = None

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
        elif qName =="HULL":
            self.__mode = "hull"
        elif qName == "HULL_TYPE":
            if self.__mode != "hull":
                print "HULL_TYPE outside of HULL tag"   #TODO better error handling
            else:
                self.__hull_cat = attributes.value("cat").toInt()
                self.__hull_vol = attributes.value("volume").toFloat()
                self.__hull_cost = attributes.value("cost").toFloat()
                self.__hull_name = attributes.value("name")
        elif qName == "MIN_LIMIT":
            self.__text = QtCore.QString()
        elif qName == "MAX_LIMIT":
            self.__text = QtCore.QString()
        elif qName == "CANNON":
            self.__mode = "cannon"
            self.__magazine = None
            self.__cannon_name = attributes.value("name")
            self.__cannon_volume = attributes.value("volume").toFloat()
            self.__cannon_basecost = attributes.value("basecost").toInt()
            self.__cannon_costmul = attributes.value("costmultiplier").toInt()
            self.__cannon_minmk = attributes.value("minmk").toInt()
            self.__cannon_maxmk = attributes.value("maxmk").toInt()
            if self.__cannon_maxmk < self.__cannon_minmk:
                print "ERROR: MinMK > MaxMK"    #TODO
        elif qName == "MAGAZINE":
            if self.__mode != "cannon":
                print "MAGAZINE outside of CANNON tag"  #TODO better error handling
            else:
                self.__magazine = {"name":attributes.value("name"), \
                    "basecost":attributes.value("basecost").toFloat(), \
                    "costmultiplier":attributes.value("costmultiplier").toFloat()}
        elif qName == "WEAPON_MOUNT":
            self.ship.addWeaponMount(attributes.value("name"), attributes.value("category").toInt())
        elif qName == "MULTIPLE_FM":
            self.ship.addMultipleFM(attributes.value("name"), \
                attributes.value("volume").toFloat(), attributes.value("cost").toFloat())
                
        return True
    
    def characters(self, text):
        self.__text += text
        return True
    
    def endElement(self, namespaceURI, localName, qName):
        if qName == "NAME":
            if self.__mode == None:            
                self.ship.rulesetName = self.__text.trimmed()
        elif qName == "HULL":
            mode = None
        elif qName == "HULL_TYPE":
            self.ship.addHullType(self.__hull_cat[0], self.__hull_vol[0], \
                self.__hull_cost[0], self.__hull_name, self.__hull_min, \
                self.__hull_max)
            self.__hull_cat = None
            self.__hull_vol = None
            self.__hull_cost = None
            self.__hull_name = None
            self.__hull_max = None
            self.__hull_min = None                
        elif qName == "MIN_LIMIT":
            if self.__hull_cat is None:
                print "ERROR MIN_LIMIT outside of HULL_TYPE tag"
            else:
                min = self.__text.toInt()
                self.__hull_min = min[0]
        elif qName == "MAX_LIMIT":
            if self.__hull_cat is None:
                print "ERROR MAX_LIMIT outside of HULL_TYPE tag"
            else:
                max = self.__text.toInt()
                self.__hull_max = max[0]
        elif qName == "CANNON":
            self.ship.addCannonType(self.__cannon_name, self.__cannon_volume, \
                self.__cannon_basecost, self.__cannon_costmul, \
                self.__cannon_minmk, self.__cannon_maxmk, self.__magazine)
            self.__cannon_name = None
            self.__cannon_volume = None
            self.__cannon_basecost = None
            self.__cannon_costmul = None
            self.__cannon_minmk = None
            self.__cannon_maxmk = None
            self.__magazine = None
            self.__mode = None
            
        return True
    
    def endDocument(self):
        return True
        
    
    def fatalError(self, exception):
        self.error = "parse error at line %d column %d: %s" % \
            (exception.lineNumber(), exception.columnNumber(), \
            exception.message())
        return False
    