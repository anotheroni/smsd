
class Ship(object):
    def __init__(self, mass=1):
        self.__mass = mass 
        self.volume = mass * 3.0
        self.category = 1
        self.__volumeUsed = dict() 
        self.__cost = dict()
        self.__power = dict()
        self.__fuelCapacity = 1
        self.__hasLandingGear = False
        self.__isStreamlined = False

    def setMass(self, mass):
        self.__mass = mass
        self.volume = mass * 3.0

    def addVolume(self, part, volume):
        self.__volumeUsed[part] = volume

    def removeVolume(self, part):
        try:
            del self.__volumeUsed[part]
        except KeyError: pass

    def getVolumeUsed(self):
        usedVol = 0.0
        for vol in self.__volumeUsed.values():
            usedVol += vol
        return usedVol

    def addCost (self, part, cost):
        self.__cost[part] = cost

    def removeCost (self, part):
        try:
            del self.__cost[part]
        except KeyError: pass

    def getCost (self):
        totalCost = 0
        for cost in self.__cost.values():
            totalCost += cost
        return totalCost

    def addPower(self, part, power):
        self.__power[part] = power

    def removePower(self, part):
        try:
            del self.__power[part]
        except KeyError: pass

    def getPowerRating(self):
        totalPower = 0.0
        for power in self.__power.values():
            totalPower += power
        return totalPower

    def landingGearChanged(self, lgState):
        self.__hasLandingGear = lgState
        if (lgState):
            self.addVolume("Landing Gear", (self.volume * 0.05 * self.category))
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
