from PyQt4 import QtXml, QtCore
from math import sqrt
from smsd_xml import SaxSMSDRulesHandler

class Ship(object):
    def __init__(self, mass=1):
        self.rulesetName = None
                
        self.__shipClassDict = dict()
        self.__hullTypeDict = dict()
        self.__sublightDriveTypesDict = dict()
        self.__translightDriveTypesDict = dict()
        self.__cannonTypeDict = dict()
        self.__weaponMountDict = dict()
        self.__multipleFMDict = dict()
        self.__cannonCategoryDict = dict()
        self.__weaponHudDict = dict()
        self.__mass = mass
        self.__volume = mass * 3.0
        self.category = 1
        self.__volumeUsed = dict()
        self.__cost = dict()
        self.__power = dict()
        self.__controlPoints = dict()
        self.__hull = 21
        self.__armorBelt = 0
        self.__sublightDriveRating = 0
        self.__translightDriveRating = 0
        self.__cannonCounter = 0
        self.__cannons = dict()
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
        if len(self.__hullTypeDict) == 0:
            print "ERROR: No hull types"
        
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

#------------------------------------------------------------------------------
# SHIP CLASS Methods

    def getShipClassDict(self):
        return self.__shipClassDict
    
    # svm = Sublight Drive Volume Multiplier
    # scb = Sublight Drive Base Cost
    # tvb = Translight Drive Base Volume
    # tcm = Translight Drive Cost Multiplier
    def addShipClass(self, category, name, min, max, svm, svb, scm, scb, tvm, tvb, tcm, tcb):
        self.__shipClassDict[category] = (name, min, max, svm, svb, scm, scb, tvm, tvb, tcm, tcb)

#------------------------------------------------------------------------------
# HULL Methods

    def getHullTypeDict(self):
        return self.__hullTypeDict

    def addHullType(self, hull_cat, hull_vol, hull_cost, name, min, max):
        #print "New Hull %d %s %f %f %d" % (hull_cat, name, hull_vol, hull_cost, min)
        self.__hullTypeDict[hull_cat] = (name, hull_vol, hull_cost, min, max)

    def getHull(self):
        return self.__hull
    
    def changeHull(self, newCat):
        if self.verifyHull(newCat):
            self.__hull = newCat
            self.addVolume("Hull", self.__hullTypeDict[newCat][1] * self.__volume)
            self.addCost("Hull", self.__hullTypeDict[newCat][2] * self.__volume)
            return True
        else:
            return False

    def verifyHull(self, newCat = None):
        if newCat is None:
            newCat = self.__hull
        # Verify newCat mass requirment
        for cat in self.__hullTypeDict:
            if cat == newCat and self.__mass >= self.__hullTypeDict[cat][3] and \
                    (self.__hullTypeDict[cat][4] == "-" or self.__mass <= self.__hullTypeDict[cat][4]):
                    return True
        return False

    def findValidHull(self):
        for cat in self.__hullTypeDict:
            if self.__mass >= self.__hullTypeDict[cat][3] and \
                (self.__hullTypeDict[cat][4] == "-" or self.__mass <= self.__hullTypeDict[cat][4]):
                return cat
        return None

#------------------------------------------------------------------------------
# DRIVES Methods

    def addSublightDriveType(self, rating, acceleration, mt):
        self.__sublightDriveTypesDict[rating] = (acceleration, mt)

    def getSublightDriveTypesDict(self):
        return self.__sublightDriveTypesDict

    def getSublightDriveCost(self, rating):
        if rating == 0:
            svb = 0
            scb = 0
        else:
            svb = self.__shipClassDict[self.category][4]
            scb = self.__shipClassDict[self.category][6]
        #(name, min, max, svm, svb, scm, scb, tvm, tvb, tcm, tcb)
        volume = self.__volume * self.__shipClassDict[self.category][3] * \
                rating + svb
        cost = self.__mass * self.__shipClassDict[self.category][5] * rating + scb
        return (volume, cost)

    def changeSublightDrive(self, rating):
        self.__sublightDriveRating = rating
        (volume, cost) = self.getSublightDriveCost(rating)
        self.addVolume("Sublight Drive", volume)
        self.addCost("Sublight Drive", cost)
        self.addPower("Sublight Drive", rating)
        self.addControlPoint("Sublight Drive", rating)

    def addTranslightType(self, rating, displacement):
        self.__translightDriveTypesDict[rating] = displacement

    def getTranslightDriveTypesDict(self):
        return self.__translightDriveTypesDict

    def getTranslightDriveCost(self, rating):
        if rating == 0:
            tvb = 0
            tcb = 0
        else:
            tvb = self.__shipClassDict[self.category][8]
            tcb = self.__shipClassDict[self.category][10]
        #(name, min, max, svm, svb, scm, scb, tvm, tvb, tcm, tcb)
        volume = self.__volume * self.__shipClassDict[self.category][7] * \
                rating + tvb
        cost = self.__mass * self.__shipClassDict[self.category][9] * rating + tcb
        return (volume, cost)
    
    def changeTranslightDrive(self, rating):
        self.__translightDriveRating = rating
        (volume, cost) = self.getTranslightDriveCost(rating)
        self.addVolume("Translight Drive", volume)
        self.addCost("Translight Drive", cost)
        self.addControlPoint("Translight Drive", rating)

#------------------------------------------------------------------------------
# ARMAMENTS Methods

    def getCannonTypeDict(self):
        return self.__cannonTypeDict

    def addCannonType(self, name, volume, basecost, costmul, minmk, maxmk, magazine):
        self.__cannonTypeDict[name] = (volume, basecost, costmul, minmk, maxmk, magazine)

    def getWeaponMountDict(self):
        return self.__weaponMountDict

    def addWeaponMount(self, name, category, volume, basecost):
        self.__weaponMountDict[name] = (category, volume, basecost)

    def getMultipleFMDict(self):
        return self.__multipleFMDict

    def addMultipleFM(self, name, volume, cost):
        self.__multipleFMDict[name] = (volume, cost)

    def addCannonCategory(self, name, costmultiplier, minmk, maxmk):
        self.__cannonCategoryDict[name] = (costmultiplier, minmk, maxmk)

    def addWeaponHud(self, name, cost):
        self.__weaponHudDict[name] = cost
    
    def getWeaponHudDict(self):
        return self.__weaponHudDict

    def calculateCannonCost(self, cType, cMk, cMount, cMult, cHud, cMag):
        cost = 0
        volume = 0
        mk = cMk.toInt()[0]
        for name, data in self.__cannonCategoryDict.items():
            if mk >= data[1] and mk <= data[2]: # minMk and maxMk
                catMul = data[0]
                break
        else:
            print "ERROR: no matching category" # TODO
            catMul = 1000.0
        
        try:
            volMul = self.__cannonTypeDict[cType][0]
            baseCost = self.__cannonTypeDict[cType][1]
            costMul = self.__cannonTypeDict[cType][2]
            magazine = self.__cannonTypeDict[cType][5]
        except KeyError:
            print "ERROR: CannonType key %s doesn't exist" % cType  # TODO
            return (0, 0)
        
        try:
            mountVolMul = self.__weaponMountDict[cMount][1]
            mountBaseCost = self.__weaponMountDict[cMount][2]
        except KeyError:
            print "ERROR: MountType key %s doesn't exist" % cMount  # TODO
            return (0, 0)
        
        try:
            multiVolMul = self.__multipleFMDict[cMult][0]
            multiCostMul = self.__multipleFMDict[cMult][1]
        except KeyError:
            print "ERROR: MultipleMP key %s doesn't exist" % cMult  # TODO
            return (0, 0)
        
        try:
            hudCost = self.__weaponHudDict[cHud]
        except KeyError:
            print "ERROR: HUD key %s doesn't exist" % cHud  # TODO
            return (0, 0)
        
        cost = ((mk * costMul + baseCost) * catMul + mountBaseCost) * multiCostMul + hudCost
        volume = mk * catMul * volMul * mountVolMul * multiVolMul
        
        return (volume, cost)
    
    def addCannon(self, cType, cMk, cMount, cMult, cHud, cMag):
        self.__cannonCounter += 1
        self.__cannons[self.__cannonCounter] = (cType, cMk, cMount, cMult, cHud, cMag)
        (volume, cost) = self.calculateCannonCost(cType, cMk, cMount, cMult, cHud, cMag)
        self.addVolume("Cannon_%d" % self.__cannonCounter, volume)
        self.addCost("Cannon_%d" % self.__cannonCounter, cost)
        self.addPower("Cannon_%d" % self.__cannonCounter, cMk.toInt()[0])
        self.addControlPoint("Weapon Mounts", len(self.__cannons))
        return (volume, cost)

#------------------------------------------------------------------------------
# MASS Methods

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
        self.addControlPoint("Base", self.__mass * 0.01) 
        self.changeLandingGear(self.__hasLandingGear)

    def getMass(self):
        return self.__mass

#------------------------------------------------------------------------------
# VOLUME Methods

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

#------------------------------------------------------------------------------
# COST Methods

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

#------------------------------------------------------------------------------
# POWER Methods

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

#------------------------------------------------------------------------------
# CONTROL POINTS Methods

    def addControlPoint(self, part, points):
        self.__controlPoints[part] = points

    def removeControlPoint(self, part):
        try:
            del self.__controlPoints[part]
        except KeyError: pass
    
    def getControlPointDict(self):
        return self.__controlPoints

    def getTotalControlPoints(self):
        total = 0
        for name, points in self.__controlPoints.items():
            total += points
        return sqrt(total)

#------------------------------------------------------------------------------
# MISC Methods

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

#------------------------------------------------------------------------------
# FACILITIES Methods

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
