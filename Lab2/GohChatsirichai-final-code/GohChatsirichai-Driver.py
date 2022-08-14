from enum import auto
from os import sep
import sys
import numpy as np
import random
import copy
from pip import main
from pyswip import Prolog
prolog = Prolog()
prolog.consult("GohChatsirichai-Agent.pl")
print(bool(list(prolog.query("reborn"))))


directions = ["north", "east", "south", "west"]
rdirections = ["rnorth", "reast", "rsouth", "rwest"]


class MapCell:
    def __init__(self) -> None:
        self.indicators = [[".", ".", "."],
                           [" ", "?", " "],
                           [".", ".", "."]]
        self.elements = {
            "glitter": False,
            "wumpus": False,
            "stench": False,
            "confounded": False,
            "portal": False,
            "tingle": False,
            "bump": False,
            "scream": False,
            'wall': False,
        }

    def printCell(self, row):
        print(" ".join(self.indicators[row]), end="  ")

    def performSet(self, element, boolean):
        if element == "stench":
            if boolean:
                self.setStench()
            else:
                self.clearStench()
        elif element == "tingle":
            if boolean:
                self.setTingle()

    def setWall(self):
        for i in range(3):
            for j in range(3):
                self.indicators[i][j] = "#"
        self.elements['wall'] = True

    def setWumpus(self):
        self.indicators[1][0] = "-"
        if self.indicators[1][1] == "O":
            self.indicators[1][1] = "U"
        else:
            self.indicators[1][1] = "W"
        self.indicators[1][2] = "-"
        self.elements['wumpus'] = True

    def clearWumpus(self):
        self.indicators[1] = [" ", "s", " "]

    def setPortal(self):
        self.indicators[1][0] = "-"
        if self.indicators[1][1] == "W":
            self.indicators[1][1] = "U"
        else:
            self.indicators[1][1] = "O"
        self.indicators[1][2] = "-"
        self.elements['portal'] = True

    def setConfounded(self):
        self.indicators[0][0] = "%"

    def setCoin(self):
        self.indicators[2][0] = "*"
        self.elements['glitter'] = True

    def setVisited(self):
        self.indicators[1][1] = "S"

    def clearCoin(self):
        self.indicators[2][0] = "."
        self.elements['glitter'] = False

    def setTingle(self):
        self.indicators[0][2] = "T"
        self.elements['tingle'] = True

    def setStench(self):
        self.indicators[0][1] = "="
        self.elements["stench"] = True

    def clearStench(self):
        self.elements["stench"] = False
        self.indicators[0][1] = "."

    def setScream(self):
        self.elements['scream'] = True
        self.indicators[2][2] = "@"

    def setSafe(self):
        if self.indicators[1][1] == "#" or self.indicators[1][1] == "S":
            return
        else:
            self.indicators[1] = [" ", "s", " "]

    def setBump(self):
        self.indicators[2][1] = "B"
        self.elements["bump"] = True

    def setAgent(self, direction):
        if direction == "north" or direction == "rnorth":
            self.indicators[1][1] = "^"
        elif direction == "east" or direction == "reast":
            self.indicators[1][1] = ">"
        elif direction == "south" or direction == "rsouth":
            self.indicators[1][1] = "V"
        elif direction == "west" or direction == "rwest":
            self.indicators[1][1] = "<"
        self.indicators[1][0] = "-"
        self.indicators[1][2] = "-"

    def clearAgent(self):
        self.indicators[1] = [" ", ".", " "]

    def clearTempPercepts(self):  # Scream and Bump are transitory
        self.indicators[2][1] = "."
        self.indicators[2][2] = "."
        self.elements["bump"] = False
        self.elements["scream"] = False

    def getPercepts(self):
        percepts = ['C', 'S', 'T', 'G', 'B', 'S']
        if self.elements['confounded']:
            percepts[0] = "Confounded"
        if self.elements['stench']:
            percepts[1] = "Stench"
        if self.elements['tingle']:
            percepts[2] = "Tingle"
        if self.elements["glitter"]:
            percepts[3] = "Glitter"
        if self.elements["bump"]:
            percepts[4] = "Bump"
        if self.elements["scream"]:
            percepts[5] = "Scream"
        return percepts


class Map:
    def __init__(self, row, col, Agent) -> None:
        self.row = row
        self.col = col
        self.map = [[MapCell() for i in range(row)] for j in range(col)]
        self.relativeMap = [[MapCell() for i in range(3)] for j in range(3)]
        self.agent = Agent
        self.reborn(self.agent.x, self.agent.y,
                    self.agent.direction)
        self.setBoundaries()
        self.wumpus = None

    def reborn(self, x, y, direction):
        self.relocateAgent(x, y, direction)
        self.agent.reset()

    def relocateAgent(self, x, y, direction):
        self.map[x][y].setAgent(direction)
        self.agent.x = x
        self.agent.y = y
        self.agent.direction = direction

    def doAction(self, action):
        self.map[self.agent.x][self.agent.y].clearTempPercepts()

        if action == "moveforward":
            self.moveAgentForward()
        elif action == "turnleft":
            self.turnAgentLeft()
        elif action == "turnright":
            self.turnAgentRight()
        elif action == "pickup":
            self.pickupCoin()
        elif action == "shoot":
            self.shootArrow()
        elif action == "perceive":  # no particular action just take in the senses
            pass

        percepts = self.map[self.agent.x][self.agent.y].getPercepts()

        if self.checkIfTeleported():
            percepts = self.map[self.agent.x][self.agent.y].getPercepts()
            percepts[0] = "Confounded"

        self.agent.knowledge.updateKnowledge(
            percepts, self.getSurroundingCoords(self.agent.rx, self.agent.ry), [self.agent.rx, self.agent.ry], self.agent.getForwardCoord()[1])
        self.checkIfEaten()

        return percepts

    def printMap(self):
        for i in range(self.col):
            for j in range(3):
                for k in range(self.row):
                    self.map[i][k].printCell(j)
                print()
            print()

    def setCell(self, x, y, type, boolean):
        if type == "wall":
            self.map[x][y].setWall()
        elif type == "wumpus":
            self.map[x][y].setWumpus()
            self.wumpus = (x, y)
            self.setAdjacentCells(x, y, "stench", boolean)
        elif type == "portal":
            self.map[x][y].setPortal()
            self.setAdjacentCells(x, y, "tingle", boolean)
        elif type == "coin":
            if boolean:
                self.map[x][y].setCoin()
            else:
                self.map[x][y].clearCoin()
        elif type == "safe":
            self.setSafeAroundCell(x, y)
        elif type == "visited":
            self.map[x][y].setVisited()

    def clearNPC(self, x, y, type):
        if type == "wumpus":
            self.map[x][y].setSafe()
            self.setAdjacentCells(x, y, "stench", False)
        elif type == "coin":
            self.map[x][y].clearCoin()

    def setBoundaries(self):  # only for absolute map
        for i in range(self.row):
            self.map[0][i].setWall()
            self.map[-1][i].setWall()
        for j in range(self.col):
            self.map[j][0].setWall()
            self.map[j][-1].setWall()

    def setSafeAroundCell(self, x, y):
        self.map[x+1][y].setSafe()
        self.map[x-1][y].setSafe()
        self.map[x][y+1].setSafe()
        self.map[x][y-1].setSafe()

    def setAdjacentCells(self, x, y, element, boolean):
        if not self.map[x+1][y].elements["wall"]:
            self.map[x+1][y].performSet(element, boolean)
        if not self.map[x-1][y].elements["wall"]:
            self.map[x-1][y].performSet(element, boolean)
        if not self.map[x][y+1].elements["wall"]:
            self.map[x][y+1].performSet(element, boolean)
        if not self.map[x][y-1].elements["wall"]:
            self.map[x][y-1].performSet(element, boolean)

    def moveAgentForward(self):
        forwardCoord, relativeCoord = self.agent.getForwardCoord()
        if self.map[forwardCoord[0]][forwardCoord[1]].elements["wall"]:
            # do BUMP shit
            print("Agent Bumped into the wall")
            self.map[self.agent.x][self.agent.y].setBump()

        else:
            self.map[self.agent.x][self.agent.y].clearAgent()
            self.setCell(self.agent.x, self.agent.y, "visited", True)
            print("Agent Moving Forward")
            self.relocateAgent(
                forwardCoord[0], forwardCoord[1], self.agent.getDirection())
            self.agent.rx = relativeCoord[0]
            self.agent.ry = relativeCoord[1]
            self.agent.updateDistanceTravelled()
            print(f"Relative Agent is at: {self.agent.rx},{self.agent.ry}")

    def turnAgentRight(self):
        newDirection = self.agent.getRightDirection()
        print(f"Agent turning right, now facing {newDirection}")
        self.agent.relativeDirection = rdirections[directions.index(
            newDirection)]
        self.relocateAgent(self.agent.x, self.agent.y, newDirection)

    def turnAgentLeft(self):
        newDirection = self.agent.getLeftDirection()
        print(f"Agent turning left, now facing {newDirection}")
        self.agent.relativeDirection = rdirections[directions.index(
            newDirection)]
        self.relocateAgent(self.agent.x, self.agent.y, newDirection)

    def pickupCoin(self):
        if self.map[self.agent.x][self.agent.y].indicators[2][0] != "*":
            print("No coin here, picked up nothing")
        else:
            self.agent.coins += 1
            self.map[self.agent.x][self.agent.y].clearCoin()
            print("Picked up a coin!")
            print(f"Current coins: {self.agent.coins}")

    def shootArrow(self):
        if not self.agent.arrows:
            print("No more arrows!")
            return

        else:
            if self.agent.direction == "north":
                if self.wumpus[0] < self.agent.x and self.wumpus[1] == self.agent.y:
                    self.map[self.agent.x][self.agent.y].setScream()
                    self.clearNPC(self.wumpus[0], self.wumpus[1], "wumpus")
                    self.wumpus = False
                    self.agent.knowledge.clearStench()
                    self.agent.knowledge.clearWumpus()
            elif self.agent.direction == "east":
                if self.wumpus[0] == self.agent.x and self.wumpus[1] > self.agent.y:
                    self.map[self.agent.x][self.agent.y].setScream()
                    self.clearNPC(self.wumpus[0], self.wumpus[1], "wumpus")
                    self.wumpus = False
                    self.agent.knowledge.clearStench()
                    self.agent.knowledge.clearWumpus()
            elif self.agent.direction == "south":
                if self.wumpus[0] > self.agent.x and self.wumpus[1] == self.agent.y:
                    self.map[self.agent.x][self.agent.y].setScream()
                    self.clearNPC(self.wumpus[0], self.wumpus[1], "wumpus")
                    self.wumpus = False
                    self.agent.knowledge.clearStench()
                    self.agent.knowledge.clearWumpus()
            elif self.agent.direction == "west":
                if self.wumpus[0] == self.agent.x and self.wumpus[1] < self.agent.y:
                    self.map[self.agent.x][self.agent.y].setScream()
                    self.clearNPC(self.wumpus[0], self.wumpus[1], "wumpus")
                    self.wumpus = False
                    self.agent.knowledge.clearStench()
                    self.agent.knowledge.clearWumpus()

        self.agent.arrows -= 1

    def checkIfEaten(self):  # if agent walks into the wumpus cell:
        if self.wumpus:
            if self.agent.x == self.wumpus[0] and self.agent.y == self.wumpus[1]:
                print("Agent has been killed by the wumpus.")
                print("Restarting game")
                self.map[self.agent.x][self.agent.y].clearAgent()
                self.reborn(self.agent.INITIAL_X,
                            self.agent.INITIAL_Y, self.agent.INITIAL_DIRECTION)
                global gameOver
                gameOver = True

    def getSurroundingCoords(self, x, y):  # RELATIVE COORDS [N E S W]
        return [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]

    def checkIfTeleported(self):
        if self.map[self.agent.x][self.agent.y].elements["portal"]:
            self.teleportRandom()
            return True

    def teleportRandom(self):
        newX, newY = (random.randint(1, 5), random.randint(1, 4))
        while (self.map[newX][newY].elements["wall"]) or self.map[newX][newY].elements["portal"]:
            newX, newY = (random.randint(1, 5), random.randint(1, 4))

        self.map[self.agent.x][self.agent.y].clearAgent()
        self.map[self.agent.x][self.agent.y].setPortal()
        self.reborn(newX, newY, self.agent.direction)
        self.agent.knowledge.confounded.add((0, 0))
        print(f"Agent Teleported to {newX}, {newY}")


class Agent:
    def __init__(self, x, y, direction) -> None:
        self.coins = 0
        self.arrows = 1
        self.x = x  # Actual coordinates (In the array)
        self.y = y  # Actual coordinates (In the array)
        self.knowledge = Knowledge()
        self.reset()
        self.direction = direction
        self.max_x = 0  # Furthest travelled in one direction
        self.max_y = 0
        self.INITIAL_X = x
        self.INITIAL_Y = y
        self.INITIAL_DIRECTION = direction

    def reset(self):
        self.rx = 0  # relative Coords
        self.ry = 0
        self.relativeDirection = "rnorth"
        self.max_x = 0
        self.max_y = 0
        del self.knowledge
        self.knowledge = Knowledge()

    def getDirection(self):
        return self.direction

    def updateDistanceTravelled(self):
        self.max_x = max(self.max_x, abs(self.rx))
        self.max_y = max(self.max_y, abs(self.ry))

    def getForwardCoord(self):
        toMoveX = self.x
        toMoveY = self.y
        toMoveRelativeY = self.ry
        toMoveRelativeX = self.rx
        if self.direction == "north":
            toMoveX = self.x - 1
            toMoveRelativeY = self.ry + 1
        elif self.direction == "east":
            toMoveY = self.y + 1
            toMoveRelativeX = self.rx + 1
        elif self.direction == "south":
            toMoveX = self.x + 1
            toMoveRelativeY = self.ry - 1
        elif self.direction == "west":
            toMoveY = self.y - 1
            toMoveRelativeX = self.rx - 1

        return (toMoveX, toMoveY), (toMoveRelativeX, toMoveRelativeY)

    def getRightDirection(self):
        return directions[(directions.index(self.direction) + 1) % len(directions)]

    def getLeftDirection(self):
        return directions[directions.index(self.direction) - 1]


class RelativeMap(Map):
    def __init__(self, agent) -> None:
        self.agent = copy.copy(agent)
        self.rows = 3 + agent.max_y * 2
        self.cols = 3 + agent.max_x * 2
        self.origin_x = (3 + agent.max_y * 2) // 2
        self.origin_y = (3 + agent.max_x * 2) // 2
        self.origin = (self.origin_x, self.origin_y)

        self.map = [[MapCell() for i in range(self.cols)]
                    for j in range(self.rows)]
        self.buildMap()

    def buildMap(self):
        for wall in self.agent.knowledge.walls:  # relativeCoord
            toMove = self.mapRelativeToAbsolute(wall)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setWall()

        for wumpus in self.agent.knowledge.wumpus:  # relativeCoord
            toMove = self.mapRelativeToAbsolute(wumpus)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setWumpus()

        for portal in self.agent.knowledge.portal:  # relativeCoord
            toMove = self.mapRelativeToAbsolute(portal)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setPortal()

        for stench in self.agent.knowledge.stench:  # relativeCoord
            toMove = self.mapRelativeToAbsolute(stench)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setStench()

        for tingle in self.agent.knowledge.tingle:
            toMove = self.mapRelativeToAbsolute(tingle)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setTingle()

        for safe in self.agent.knowledge.safe:
            toMove = self.mapRelativeToAbsolute(safe)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setSafe()

        for visited in self.agent.knowledge.visited:
            toMove = self.mapRelativeToAbsolute(visited)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setVisited()

        for confounded in self.agent.knowledge.confounded:
            toMove = self.mapRelativeToAbsolute(confounded)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setConfounded()

        for glitter in self.agent.knowledge.glitter:
            toMove = self.mapRelativeToAbsolute(glitter)
            actualCoord = (self.origin[0] + toMove[0],
                           self.origin[1] + toMove[1])
            self.map[actualCoord[0]][actualCoord[1]].setCoin()

        # Plant agent
        toMove = self.mapRelativeToAbsolute((self.agent.rx, self.agent.ry))
        actualCoord = (self.origin[0] + toMove[0], self.origin[1] + toMove[1])
        self.map[actualCoord[0]][actualCoord[1]].setAgent(
            self.agent.relativeDirection)
        if self.agent.knowledge.bump:
            self.map[actualCoord[0]][actualCoord[1]].setBump()
        if self.agent.knowledge.scream:
            self.map[actualCoord[0]][actualCoord[1]].setScream()

    def mapRelativeToAbsolute(self, relativeCoord):
        moveX = -(relativeCoord[1])
        moveY = relativeCoord[0]
        return (moveX, moveY)

    def getCoordForRelative(self, toMove):
        return (self.origin[0] + toMove[0], self.origin[1] + toMove[1])

    def printMap(self):
        for i in range(self.rows):
            for j in range(3):
                for k in range(self.cols):
                    self.map[i][k].printCell(j)
                print()
            print()


class Knowledge():
    def __init__(self) -> None:
        self.walls = set()
        self.safe = set()
        self.tingle = set()
        self.wumpus = set()  # Where the wumpus may be
        self.portal = set()
        self.stench = set()
        self.visited = set()
        self.glitter = set()
        self.confounded = set()
        self.bump = False
        self.scream = False

    def clearStench(self):
        del self.stench
        self.stench = set()

    def clearWumpus(self):
        del self.wumpus
        self.wumpus = set()

    def updateKnowledge(self, percepts, surroundCoord, Coord, forwardCoord):
        self.bump = False
        self.scream = False
        binaryPercepts = [1 if len(i) > 1 else 0 for i in percepts]
        self.visited.add((Coord[0], Coord[1]))
        if (Coord[0], Coord[1]) in self.wumpus:
            self.wumpus.remove((Coord[0], Coord[1]))
        if (Coord[0], Coord[1]) in self.portal:
            self.portal.remove((Coord[0], Coord[1]))

        if binaryPercepts[0]:  # Confounded, wipe knowledge
            self.confounded.add((Coord[0], Coord[1]))

        # not stench and not tingling == All around safe
        if sum(binaryPercepts[1:3]) == 0:
            for i in surroundCoord:
                if i not in self.visited and i not in self.walls:
                    self.safe.add(i)

        if binaryPercepts[1]:  # Danger of wumpus
            self.stench.add((Coord[0], Coord[1]))
            for i in surroundCoord:
                if i not in self.visited and i not in self.walls and i not in self.safe:
                    self.wumpus.add(i)

        if binaryPercepts[2]:  # Tingling
            self.tingle.add((Coord[0], Coord[1]))
            for i in surroundCoord:
                if i not in self.safe and i not in self.visited and i not in self.walls:
                    self.portal.add(i)

        if binaryPercepts[3]:  # Glitter
            self.glitter.add((Coord[0], Coord[1]))

        if binaryPercepts[4]:  # Bumped into wall
            self.walls.add((forwardCoord[0], forwardCoord[1]))
            if (forwardCoord[0], forwardCoord[1]) in self.safe:
                self.safe.remove((forwardCoord[0], forwardCoord[1]))
            if (forwardCoord[0], forwardCoord[1]) in self.wumpus:
                self.wumpus.remove((forwardCoord[0], forwardCoord[1]))
            if (forwardCoord[0], forwardCoord[1]) in self.portal:
                self.portal.remove((forwardCoord[0], forwardCoord[1]))
            self.bump = True

        if binaryPercepts[5]:
            self.scream = True

    def printKnowledge(self):
        print()
        print("------CURRENT KNOWLEDGE------")
        print("Walls: " + str(self.walls))
        print("Safe: " + str(self.safe))
        print("Tingle: " + str(self.tingle))
        print("Coins: " + str(self.glitter))
        print("Stench: " + str(self.stench))
        print("Wumpus: " + str(self.wumpus))
        print("Visited: " + str(self.visited))
        print("Portals: " + str(self.portal))
        print("Confounded: " + str(self.confounded))

# MESSED UP FROM HERE DELETE OR CHANGE ACCORDINGLY


def performAction(a):
    global game
    if a == "moveforward":
        percepts = game.doAction("moveforward")
        print(percepts)
        percepts = ["on" if len(i) > 1 else "off" for i in percepts]
        (bool(list(prolog.query(
            "move(moveforward,[{},{},{},{},{},{}])".format(*percepts)))))

    elif a == "turnleft":
        percepts = game.doAction("turnleft")
        print(percepts)
        percepts = ["on" if len(i) > 1 else "off" for i in percepts]
        (bool(list(prolog.query(
            "move(turnleft,[{},{},{},{},{},{}])".format(*percepts)))))

    elif a == "turnright":
        percepts = game.doAction("turnright")
        print(percepts)
        percepts = ["on" if len(i) > 1 else "off" for i in percepts]
        (bool(list(prolog.query(
            "move(turnright,[{},{},{},{},{},{}])".format(*percepts)))))

    elif a == "pickup":
        percepts = game.doAction("perceive")
        print(percepts)
        percepts = ["on" if len(i) > 1 else "off" for i in percepts]
        print(
            bool(list(prolog.query("move(pickup,[{},{},{},{},{},{}])".format(*percepts)))))
        game.doAction("pickup")

    elif a == "shoot":
        percepts = game.doAction("shoot")
        print(percepts)
        percepts = ["on" if len(i) > 1 else "off" for i in percepts]
        print(
            bool(list(prolog.query("move(shoot,[{},{},{},{},{},{}])".format(*percepts)))))


def spawnPortals():
    global game
    x, y = random.randint(1, 4), random.randint(1, 5)
    while game.map[x][y].elements['glitter'] or game.map[x][y].elements['portal'] or (x == game.agent.x and y == game.agent.y or y == game.agent.x + 1):
        x, y = random.randint(1, 4), random.randint(1, 5)

    game.setCell(x, y, "portal", True)


def spawnWumpus():
    x, y = random.randint(1, 4), random.randint(1, 5)
    while game.map[x][y].elements['portal'] or (x == game.agent.x and y == game.agent.y):
        x, y = random.randint(1, 4), random.randint(1, 5)
    game.setCell(x, y, "wumpus", True)


def spawnCoin():
    x, y = random.randint(1, 4), random.randint(1, 5)
    while game.map[x][y].elements['wumpus'] or game.map[x][y].elements['portal'] or (x == game.agent.x and y == game.agent.y):
        x, y = random.randint(1, 4), random.randint(1, 5)
    game.setCell(x, y, "coin", True)


def setupWorld():
    """ for i in range(2):
        spawnPortals()
    spawnWumpus()
    for i in range(3):
        spawnCoin() """

    global game
    game.setCell(1, 1, "portal", True)
    game.setCell(2, 1, "portal", True)
    game.setCell(2, 5, "portal", True)
    game.setCell(4, 4, "wumpus", True)
    game.setCell(4, 3, "coin", True)


def autopilot():
    print("Agent now exploring with explore(L):")
    move = 0
    while True:
        move += 1
        print(f"======== Move: {move} ========")
        if bool(list(prolog.query("explore(L)"))) is True:
            temp = list(prolog.query("explore(L)"))
            if len(temp) > 0:
                actions = temp[0].get('L')
                print(f"actions: {actions}")
                for action in actions:
                    performAction(action)

                newRmap = RelativeMap(game.agent)
                newRmap.printMap()
                game.printMap()
            #input("Press Enter to continue:")
            print()
        else:
            print("no available safe actions.")
            break


def showActions():
    print("Options: ")
    print("1: explore(L)")
    print("2: moveforward")
    print("3: turnleft")
    print("4: turnright")
    print("5: shoot")
    print("6: pickup")
    print("7: Exit Program")


if __name__ == "__main__":
    gameOver = False
    game = Map(7, 6, Agent(4, 1, "north"))
    setupWorld()
    spawn_percepts = game.doAction("perceive")
    print("Initial layout:")
    game.printMap()
    print(spawn_percepts)
    spawn_percepts = ["on" if len(i) > 1 else "off" for i in spawn_percepts]
    spawn_percepts[0] = "on"
    (list(prolog.query(
        "reposition([{},{},{},{},{},{}])".format(*spawn_percepts))))
    newRmap = RelativeMap(game.agent)
    newRmap.printMap()

    while not gameOver:
        showActions()
        choice = input()
        if choice == "1":
            autopilot()
            continue
        elif choice == "2":
            performAction("moveforward")
        elif choice == "3":
            performAction("turnleft")
        elif choice == "4":
            performAction("turnright")
        elif choice == "5":
            performAction("shoot")
        elif choice == "6":
            performAction("pickup")
        elif choice == "7":
            break
        else:
            print("Enter a valid choice")
            continue
        newRmap = RelativeMap(game.agent)
        newRmap.printMap()
        game.printMap()

    print("Game has ended.")
    print(
        f"Agent has: {game.agent.arrows} arrows and {game.agent.coins} coins.")
