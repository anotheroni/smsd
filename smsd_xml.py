from PyQt5.QtXml import *
from PyQt5 import QtCore
import sys

class SaxSMSDRulesHandler(QXmlDefaultHandler):
    
    def __init__(self, ship):
        super().__init__()
        self.ship = ship
        self.__mode = None
        self.__text = ""
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
            self.__text = ""
        elif qName == "SHIP_CLASS":
            cat = int(attributes.value("category"))
            min = int(attributes.value("min_mass"))
            max = attributes.value("max_mass")
            if max == "+":
                max = sys.maxsize
            else:
                max = int(max)
            self.ship.addShipClass(cat, attributes.value("name"), min, max, \
                float(attributes.value("sublight_vol_mult")), \
                int(attributes.value("sublight_vol_base")), \
                int(attributes.value("sublight_cost_mult")), \
                int(attributes.value("sublight_cost_base")), \
                float(attributes.value("translight_vol_mult")), \
                int(attributes.value("translight_vol_base")), \
                int(attributes.value("translight_cost_mult")), \
                int(attributes.value("translight_cost_base")))
            
        elif qName =="HULL":
            self.__mode = "hull"
        elif qName == "HULL_TYPE":
            if self.__mode != "hull":
                print("HULL_TYPE outside of HULL tag")   #TODO better error handling
            else:
                self.__hull_cat = int(attributes.value("cat"))
                self.__hull_vol = float(attributes.value("volume"))
                self.__hull_cost = float(attributes.value("cost"))
                self.__hull_name = attributes.value("name")
        elif qName == "MIN_LIMIT":
            self.__text = ""
        elif qName == "MAX_LIMIT":
            self.__text = ""
            
        elif qName == "SUBLIGHT_DRIVE":
            self.ship.addSublightDriveType(int(attributes.value("rating")), \
                float(attributes.value("acceleration")), \
                int(attributes.value("mt")))
        
        elif qName == "TRANSLIGHT_DRIVE":
            self.ship.addTranslightType(int(attributes.value("rating")), \
                float(attributes.value("displacement")))
        
        elif qName == "SYSTEM_MK":
            self.__mode = "system_mk"
        
        elif qName == "SYSTEM_MK_ITEM":
            if self.__mode != "system_mk":
                print("SYSTEM_MK_ITEM outside of SYSTEM_MK tag") # TODO
            else:
                self.__system_mk_name = attributes.value("name")
                self.__system_mk_data = (int(attributes.value("minmk")), \
                        int(attributes.value("maxmk")), \
                        int(attributes.value("basecost")), \
                        int(attributes.value("costmultiplier")), \
                        float(attributes.value("basevolume")), \
                        float(attributes.value("volumemultiplier")))
        
        elif qName == "CANNON":
            self.__mode = "cannon"
            self.__magazine = None
            self.__cannon_name = attributes.value("name")
            self.__cannon_volume = float(attributes.value("volume"))  #TODO new function that throws an exception
            self.__cannon_basecost = int(attributes.value("basecost"))
            self.__cannon_costmul = int(attributes.value("costmultiplier"))
            self.__cannon_minmk = int(attributes.value("minmk"))
            self.__cannon_maxmk = int(attributes.value("maxmk"))
            if self.__cannon_maxmk < self.__cannon_minmk:
                print("ERROR: MinMK > MaxMK")    #TODO
        elif qName == "MAGAZINE":
            if self.__mode != "cannon":
                print("MAGAZINE outside of CANNON tag")  #TODO better error handling
            else:
                self.__magazine = {"name":attributes.value("name"), \
                    "basecost":float(attributes.value("basecost")), \
                    "costmultiplier":float(attributes.value("costmultiplier"))}
        elif qName == "WEAPON_MOUNT":
            self.ship.addWeaponMount(attributes.value("name"), \
                int(attributes.value("category")), \
                float(attributes.value("volume")), \
                int(attributes.value("basecost")))
        elif qName == "MULTIPLE_FM":
            self.ship.addMultipleFM(attributes.value("name"), \
                float(attributes.value("volume")), float(attributes.value("cost")))
        elif qName == "CANNON_CATEGORY":
            self.ship.addCannonCategory(attributes.value("name"), \
                float(attributes.value("costmultiplier")), \
                int(attributes.value("minmk")), \
                int(attributes.value("maxmk")))
        elif qName == "WEAPON_HUD":
            self.ship.addWeaponHud(attributes.value("name"), \
                int(attributes.value("cost")))
                
        return True
    
    def characters(self, text):
        self.__text += text
        return True
    
    def endElement(self, namespaceURI, localName, qName):
        if qName == "NAME":
            if self.__mode == None:            
                self.ship.rulesetName = self.__text.strip()
        elif qName == "HULL":
            mode = None
        elif qName == "HULL_TYPE":
            self.ship.addHullType(self.__hull_cat, self.__hull_vol, \
                self.__hull_cost, self.__hull_name, self.__hull_min, \
                self.__hull_max)
            self.__hull_cat = None
            self.__hull_vol = None
            self.__hull_cost = None
            self.__hull_name = None
            self.__hull_max = None
            self.__hull_min = None                
        elif qName == "MIN_LIMIT":
            if self.__hull_cat is None:
                print("ERROR MIN_LIMIT outside of HULL_TYPE tag")
            else:
                min = int(self.__text)
                self.__hull_min = min
        elif qName == "MAX_LIMIT":
            if self.__hull_cat is None:
                print("ERROR MAX_LIMIT outside of HULL_TYPE tag")
            else:
                max = int(self.__text)
                self.__hull_max = max
                
        elif qName == "SYSTEM_MK_ITEM":
            if self.__mode != "system_mk":
                print("SYSTEM_MK_ITEM end tag outside of SYSTEM_MK tag") # TODO
            elif self.__system_mk_name is None or self.__system_mk_data is None:
                print("SYSTEM_MK_ITEM missing data")
                self.__system_mk_name = None
                self.__system_mk_data = None
            else:
                self.ship.addSystemMkItem(self.__system_mk_name, self.__system_mk_data)
                self.__system_mk_name = None
                self.__system_mk_data = None
        
        elif qName == "SYSTEM_MK":
            self.__mode = None
                
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
    
