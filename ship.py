from PyQt4 import QtXml, QtCore
from smsd_xml import SaxSMSDRulesHandler

class Ship(object):
    def __init__(self, mass=1):
        self.rulesetName = None
                
        self.__shipClassDict = dict()        
        self.__mass = mass 
        self.__volume = mass * 3.0
        self.category = 1
        self.__volumeUsed = dict() 
        self.__cost = dict()
        self.__power = dict()
        self.__hull = 21
        self.__armorBelt = 0
        self.__sublightDriveRating = 1
        self.__translightDriveRating = 0
        self.__tractorBeams = dict()
        self.__deflectorScreen= [0, 0]  # Rating, Bonus
        self.__fuelCapacity = 1
        self.__hasLandingGear = False
        self.__isStreamlined = False
        self.__accommodations = {"acc_first":0, "acc_standard":0, "acc_low":0, "acc_crew":0, "acc_cryo":0, "acc_seating":0}
        self.__recreational = 0
        self.__lifesupport = 0
        
        fh = None
        try:
            handler = SaxSMSDRulesHandler(self)
            parser = QtXml.QXmlSimpleReader()
            parser.setContentHandler(handler)
            parser.setErrorHandler(handler)
            fh = QtCore.QFile("sm_original.xml")
            input = QtXml.QXmlInputSource(fh)
            if not parser.parse(input):
                raise ValueError, handler.error
        except (IOError, OSError, ValueError), e:
            print "Failed to import: %s" % e
        finally:
            if fh is not None:
                fh.close()
        
        if len(self.__shipClassDict) == 0:
            print "ERROR: No ship classes"
        
        # Index: (Name, Cost Constant)
        self.__armorBeltConstant = {0:("None", 0), 1:("+5 DB and +5% HP", 100), 2:("+10 DB and +10% HP",  200),  \
                                    3:("+15 DB and +15%HP", 300), 4:("+20 DB and +20% HP", 400), 5:("+25 DB and +25% HP",  500)}
        # Index: (Volume, Cost)
        self.__accommodationsConstant = {"acc_first":(30, 1000),  "acc_standard":(20, 800),  "acc_low":(10, 500), \
                                          "acc_crew":(10, 500),  "acc_cryo":(3, 1000),  "acc_seating":(3, 100)  }
        # Index (rank): Bonus
        self.__bonusTable = {0:0, 1:5, 2:10, 3:15, 4:20, 5:25, 6:30, 7:35, 8:40, 9:45, 10:50,\
                              11:52, 12:54, 13:56, 14:58, 15:60, 16:62, 17:64, 18:66, 19:68, 20:70, \
                              21:71, 22:72, 23:73, 24:74, 25:75, 26:76, 27:77, 28:78, 29:79, 30:80}

    def getShipClassDict(self):
        return self.__shipClassDict
    
    def addShipClass(self, category, name, min, max):
        self.__shipClassDict[category] = (name, min, max)

    def setMass(self, mass):
        self.__mass = mass
        self.__volume = mass * 3.0
        for cat in self.__shipClassDict:
            if mass >= self.__shipClassDict[cat][1] and \
                    (self.__shipClassDict[cat][2] == "+" or \
                     mass <= self.__shipClassDict[cat][2]):
                break
        else:
            print "ERROR unknown category"      #TODO fix real error handling
            return
        if self.category != cat:
            self.category = cat
            self.addVolume("power", self.getPowerRating() * (self.category ** 2 + self.getFuelCapacity() * 0.01))
            self.addCost("power", self.getPowerRating() * (self.category ** 2) * 500 + 50000 + \
                                                  (self.getFuelCapacity() + self.getPowerRating()) * 10)
            self.changeLandingGear(self.__hasLandingGear)
        

    def addVolume(self, part, volume):
        self.__volumeUsed[part] = volume

    def removeVolume(self, part):
        try:
            del self.__volumeUsed[part]
        except KeyError: pass
            
        
    def getTotalVolume(self):
        return self.__volume

    def getVolume(self,  part):
        try:
            return self.__volumeUsed[part]
        except KeyError: return 0

    def getVolumeUsed(self):
        usedVol = 0.0
        for vol in self.__volumeUsed.values():
            usedVol += vol
        return usedVol

    def addCost (self, part, cost):
        self.__cost[part] = cost
        
    def getCost(self, part):
        try:
            return self.__cost[part]
        except KeyError: return 0

    def removeCost (self, part):
        try:
            del self.__cost[part]
        except KeyError: pass

    def getTotalCost (self):
        totalCost = 0
        for cost in self.__cost.values():
            totalCost += cost
        return totalCost

    def addPower(self, part, power):
        self.__power[part] = power
        self.addVolume("power", self.getPowerRating() * (self.category ** 2 + self.getFuelCapacity() * 0.01))
        self.addCost("power", self.getPowerRating() * (self.category ** 2) * 500 + 50000 + \
                                                  (self.getFuelCapacity() + self.getPowerRating()) * 10)

    def removePower(self, part):
        try:
            del self.__power[part]
        except KeyError: pass
        self.addVolume("power", self.getPowerRating() * (self.category ** 2 + self.getFuelCapacity() * 0.01))
        self.addCost("power", self.getPowerRating() * (self.category ** 2) * 500 + 50000 + \
                                                  (self.getFuelCapacity() + self.getPowerRating()) * 10)

    def getPowerRating(self):
        totalPower = 0.0
        for power in self.__power.values():
            totalPower += power
        return totalPower

    def getPowerDict(self):
        return self.__power

    def getFuelCapacity(self):
        return self.__fuelCapacity
        
    def changeFuelCapacity(self,  capacity):    #TODO keep updated
        self.__fuelCapacity = capacity
        self.addCost("Fuel Storage",  (capacity + self.getPowerRating()) * 10)
        self.addVolume("Fuel Storage",  capacity * self.getPowerRating() * 0.01 )
        self.addVolume("power", self.getPowerRating() * (self.category ** 2 + self.getFuelCapacity() * 0.01))
        self.addCost("power", self.getPowerRating() * (self.category ** 2) * 500 + 50000 + \
                                                  (self.getFuelCapacity() + self.getPowerRating()) * 10)

    def updateArmorBelt(self, index):
        self.__armorBelt = index
        self.addCost("Armor Belt", self.__armorBeltConstant[index][1] * self.__mass)

    def changeLandingGear(self, lgState):
        self.__hasLandingGear = lgState
        if (lgState):
            self.addVolume("Landing Gear", (self.__volume * 0.05 * self.category))
            self.addCost("Landing Gear", (self.__mass * 5 * self.category))
        else:
            self.removeVolume("Landing Gear")
            self.removeCost("Landing Gear")

    def getLandingGearVolume(self):
        if (self.__hasLandingGear):
            return "%.2f" % self.__volumeUsed["Landing Gear"]
        else:
            return ""

    def getLandingGearCost(self):
        if (self.__hasLandingGear):
            return "%d" % self.__cost["Landing Gear"]
        else:
            return ""
    
    def updateDeflectorScreen(self, rating):
        self.__deflectorScreen[0] = rating
        self.__deflectorScreen[1] = self.__bonusTable[rating]
        self.addCost("deflector", rating * self.__mass * 20 )
        self.addVolume("deflector",  rating * self.__volume * 0.03)
        self.addPower("deflector",  rating)

    def getDeflectorScreenBonus(self):
        return self.__deflectorScreen[1]

    def streamlinedChanged(self, stState):
        self.__isStreamlined = stState
        if (stState):
            self.addCost("Streamlined", (self.__mass * 50))
        else:
            self.removeCost("Streamlined")

    def getStreamlinedCost(self):
        if (self.__isStreamlined):
            return "%d" % self.__cost["Streamlined"]
        else:
            return ""
            
    def addAccommodations(self, type, number):
        self.__accommodations[type] = number
        constants = self.__accommodationsConstant[type]
        self.__cost[type] = number * constants[1]
        self.__volumeUsed[type] = number * constants[0]
        self.updateRecreational()
        self.updateLifeSupport()
    
    def updateRecreational(self):
        self.__recreational = self.__accommodations["acc_crew"] + self.__accommodations["acc_first"] + \
                        self.__accommodations["acc_standard"] + self.__accommodations["acc_low"]
        self.addCost("recreational",  self.__recreational * 100)
        self.addVolume("recreational",  self.__recreational * 5)
    
    def getRecreational(self):
        return self.__recreational

    def updateLifeSupport(self):
        self.__lifesupport = self.__accommodations["acc_crew"] + self.__accommodations["acc_first"] + \
                        self.__accommodations["acc_standard"] + self.__accommodations["acc_low"] + \
                        self.__accommodations["acc_seating"]
        self.addCost("lifesupport",  self.__lifesupport * 500)
        self.addVolume("lifesupport",  self.__lifesupport * 10)
        
    def getLifeSupport(self):
        return self.__lifesupport
