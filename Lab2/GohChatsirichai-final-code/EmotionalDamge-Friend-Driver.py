from math import floor
import random
import sys
from pyswip import Prolog
prolog = Prolog()
prolog.consult("GohChatsirichai-Agent.pl")
print(bool(list(prolog.query("reborn"))))

# coordinate translation
# examples
# 1 c,1 r = 29
# 0 c,1 r = 28
# 0 c,0 r = 35
# 6 c,0 r = 41
# 0 c,5 r = 0

# (grid_x * grid_y) - (grix_x + (r x grid_x)) + c = index

# relative coordinate translation
# examples
# 3x3, 4
# 5x5, 12
# 7x7, 24
# 9x9, 40
# center = (x**2 - 1 ) / 2


GRID_X = 7
GRID_Y = 6
CONTENT_SIZE = 3

relativeSize = 1

directions = ["north", "east", "south", "west"]
# orientation is the index of directions
orientation = 0
currentCell = 35
prevNPC = "s"
gameOver = False

# Confounded, Stench, Tingle, Glitter, Bump, Scream.
currentSenses = ["on", "off", "off", "off", "off", "off"]

cells = [["s" for i in range(CONTENT_SIZE * CONTENT_SIZE)]
         for j in range(GRID_X * GRID_Y)]

for elem in cells[0]:
    elem += "1"


def test():
    for i in range(len(cells)):
        for j in range(len(cells[0])):
            cells[i][j] = i


def test2():
    for i in range(len(cells)):
        for j in range(len(cells[0])):
            cells[i][j] = "{}({})".format(i, j)


def displayGrid():

    grid = ""

    for l in range(GRID_Y):
        for j in range(CONTENT_SIZE):
            for i in range(GRID_X):
                grid += ((" {} ").format(cells[i][0]) + (" {} ").format(
                    cells[i][1]) + (" {} ").format(cells[i][2]) + "|")
            grid += "\n"

        for k in range(GRID_X):
            for times in range(CONTENT_SIZE):
                grid += "---"
            grid += "+"
        grid += "\n"

    print(grid)


def displayGridDynamic():

    grid = ""

    for y in range(GRID_Y):

        for size in range(CONTENT_SIZE):
            for x in range(GRID_X):
                grid += (("{} ").format(cells[y*GRID_Y + x + y][size * CONTENT_SIZE]) + ("{} ").format(
                    cells[y*GRID_Y + x + y][size * CONTENT_SIZE + 1]) + ("{}").format(cells[y*GRID_Y + x + y][size * CONTENT_SIZE + 2]) + "   ")
            grid += "\n"

        grid += "\n"
        # for k in range(GRID_X):
        #    for times in range(CONTENT_SIZE):
        #        grid += "---"
        #    grid += "+"
        #grid += "\n"

    print(grid)


def displayRelativeGrid():

    global relativeSize

    visited = list(prolog.query("visited(X,Y)"))
    for coord in visited:
        x = coord.get('X')
        y = coord.get('Y')
        if abs(x) > (relativeSize-1)/2 or abs(y) > (relativeSize-1)/2:
            relativeSize += 2
            return displayRelativeGrid()

    grid = [["?" for i in range(CONTENT_SIZE * CONTENT_SIZE)]
            for j in range(relativeSize * relativeSize)]
    origin = (relativeSize*relativeSize - 1) / 2
    print()

    for i in range(len(grid)):
        coord = getCoordForRelativeCell(i)
        x = coord[0]
        y = coord[1]

        if bool(list(prolog.query("wall({},{})".format(x, y)))) is True:
            for j in range(len(grid[i])):
                grid[i][j] = "#"

            continue

        agentRelativePos = (list(prolog.query("current(X,Y,D)"))[0].get(
            'X'), list(prolog.query("current(X,Y,D)"))[0].get('Y'))

        grid[i][0] = "%" if bool(
            list(prolog.query("confundus({},{})".format(x, y)))) else "."
        grid[i][1] = '=' if bool(
            list(prolog.query("stench({},{})".format(x, y)))) else "."
        grid[i][2] = "T" if bool(
            list(prolog.query("tingle({},{})".format(x, y)))) else "."
        grid[i][3] = '-' if len(list(prolog.query("current({},{},D)".format(x, y)))
                                ) > 0 or bool(list(prolog.query("wumpus({},{})".format(x, y)))) else "."

        temp = " "
        if len(list(prolog.query("current({},{},D)".format(x, y)))) > 0:
            direction = list(prolog.query("current({},{},D)".format(x, y)))[
                0].get('D')
            if direction == "rnorth":
                direction = "^"
            elif direction == "rsouth":
                direction = "v"
            elif direction == "reast":
                direction = ">"
            elif direction == "rwest":
                direction = "<"

            temp = direction
        elif bool(list(prolog.query("wumpus({},{})".format(x, y)))) and bool(list(prolog.query("confundus({},{})".format(x, y)))):
            temp = "U"
        elif bool(list(prolog.query("wumpus({},{})".format(x, y)))):
            temp = "W"
        elif bool(list(prolog.query("confundus({},{})".format(x, y)))):
            temp = "O"
        elif bool(list(prolog.query("safe({},{})".format(x, y)))) and not bool(list(prolog.query("visited({},{})".format(x, y)))):
            temp = "s"
        elif bool(list(prolog.query("safe({},{})".format(x, y)))) and bool(list(prolog.query("visited({},{})".format(x, y)))):
            temp = "S"
        else:
            temp = "?"

        grid[i][4] = temp
        grid[i][5] = '-' if len(list(prolog.query("current({},{},D)".format(x, y)))
                                ) > 0 or bool(list(prolog.query("wumpus({},{})".format(x, y)))) else "."
        grid[i][6] = '*' if bool(
            list(prolog.query("glitter({},{})".format(x, y)))) else "."
        grid[i][7] = 'B' if currentSenses[4] == "on" and x == agentRelativePos[0] and y == agentRelativePos[1] else "."
        grid[i][8] = '@' if currentSenses[5] == "on" and x == agentRelativePos[0] and y == agentRelativePos[1] else "."

    rgrid = ""

    for i in range(relativeSize):
        for j in range(relativeSize):
            rgrid += ("{} {} {}   ".format(grid[i * relativeSize + j][0],
                      grid[i * relativeSize + j][1], grid[i * relativeSize + j][2]))
        rgrid += "\n"
        for j in range(relativeSize):
            rgrid += ("{} {} {}   ".format(grid[i * relativeSize + j][3],
                      grid[i * relativeSize + j][4], grid[i * relativeSize + j][5]))
        rgrid += "\n"
        for j in range(relativeSize):
            rgrid += ("{} {} {}   ".format(grid[i * relativeSize + j][6],
                      grid[i * relativeSize + j][7], grid[i * relativeSize + j][8]))
        rgrid += "\n\n"

    print(rgrid)


def printCoordsForRelativeGrid():
    # offset from center
    offset = (((relativeSize-1)/2))
    # max x or y allowed
    #cutoff = (((relativeSize-1)/2)+offset)
    cutoff = (relativeSize + 1) / 2

    for i in range(relativeSize * relativeSize):

        # 00 10 20 30 40
        # 01 11 21 31 41
        # 02 12 22 32 42
        # 03 13 23 33 43
        # 04 14 24 34 44

        x = int((floor(i % relativeSize) - offset))
        y = int((floor(i/relativeSize) - offset)) * -1

        print("x = ",  x)
        print("y = ",  y)
        print()


def getCoordForRelativeCell2(i):
    # offset from center
    offset = (((relativeSize-1)/2))
    # max x or y allowed
    #cutoff = (((relativeSize-1)/2)+offset)
    cutoff = (relativeSize+1) / 2

    x = int((floor(i % relativeSize) + offset) % cutoff) * \
        (-1 if (floor(i % relativeSize) + offset) < cutoff else 1)
    y = int((floor(i/relativeSize) + offset) % cutoff) * \
        (-1 if (floor(i/relativeSize) + offset) > cutoff else 1)

    return (x, y)


def getCoordForRelativeCell(i):
    # offset from center
    offset = (((relativeSize-1)/2))

    x = int((floor(i % relativeSize) - offset))
    y = int((floor(i/relativeSize) - offset)) * -1

    return (x, y)


def getPointer(o):
    if o == "north":
        return "^"
    if o == "south":
        return "v"
    if o == "east":
        return ">"
    if o == "west":
        return "<"


def move():

    global prevNPC
    global relativeSize
    global currentCell
    prevCell = currentCell

    facing = directions[orientation]

    if facing == "north":
        if currentCell - GRID_X > -1:
            currentCell -= GRID_X
        else:
            print("what are you doing?")

    if facing == "south":
        if currentCell + GRID_X < (GRID_X * GRID_Y):
            currentCell += GRID_X
        else:
            print("what are you doing?")

    if facing == "east":
        if (currentCell) % GRID_X is not GRID_X-1:
            currentCell += 1
        else:
            print("what are you doing?")

    if facing == "west":
        if (currentCell) % GRID_X is not 0:
            currentCell -= 1
        else:
            print("what are you doing?")

    if cells[currentCell][0] == "#":
        currentCell = prevCell
        sense()
        currentSenses[4] = "on"
    elif cells[currentCell][4] == "W":
        print("Agent killed by wumpus.")
        print(bool(list(prolog.query("reborn"))))
        relativeSize = 1
        setupWorld()
        resetSenses()
    elif cells[currentCell][4] == "O":
        print("Stepped into portal.")
        print("teleporting...")
        cells[prevCell][4] = "O"
        relativeSize = 1
        spawnAgent()
        resetSenses()
        sense()
        currentSenses[0] = "on"
    else:
        cells[prevCell][4] = prevNPC
        if prevNPC != "W" and prevNPC != "O":
            cells[prevCell][3] = " "
            cells[prevCell][5] = " "

        prevNPC = ""+cells[currentCell][4]
        cells[currentCell][4] = getPointer(directions[orientation])
        surroundAgentSymbol()
        sense()


def surroundAgentSymbol():
    cells[currentCell][3] = '-'
    cells[currentCell][5] = '-'


def turn(x):
    global orientation
    if orientation + x >= len(directions):
        orientation = 0
    elif orientation + x < 0:
        orientation = len(directions)-1
    else:
        orientation += x

    cells[currentCell][4] = getPointer(directions[orientation])
    # turn bump(if it was on) off after turning
    currentSenses[4] = "off"


def sense():
    # Confounded, Stench, Tingle, Glitter, Bump, Scream.
    current = cells[currentCell]
    currentSenses[0] = "off"
    currentSenses[1] = "on" if current[1] == "=" else "off"
    currentSenses[2] = "on" if current[2] == "T" else "off"
    currentSenses[3] = "on" if current[6] == "*" else "off"
    currentSenses[4] = "off"
    currentSenses[5] = "off"


def printSenses():
    a = "Confounded" if currentSenses[0] == "on" else "C"
    b = "Stench" if currentSenses[1] == "on" else "S"
    c = "Tingle" if currentSenses[2] == "on" else "T"
    d = "Glitter" if currentSenses[3] == "on" else "G"
    e = "Bump" if currentSenses[4] == "on" else "B"
    f = "Scream" if currentSenses[5] == "on" else "S"

    print("[{}-{}-{}-{}-{}-{}]".format(a, b, c, d, e, f))


def grabCoin():
    global cells
    print(bool(list(prolog.query("move(pickup,[{},{},{},{},{},{}])".format(
        currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))
    if cells[currentCell][6] == "*":
        cells[currentCell][6] = "."


def shoot():
    global cells
    global currentSenses

    fly = 1

    if orientation == 0:
        fly = -GRID_X
    elif orientation == 1:
        fly = 1
    elif orientation == 2:
        fly = GRID_X
    elif orientation == 3:
        fly = -1

    nextCell = currentCell + fly

    while nextCell >= 0 and nextCell < (GRID_X * GRID_Y):
        if cells[nextCell][4] == "W":
            currentSenses[5] = "on"
            cells[nextCell][4] = "S"

            x = nextCell

            if(x+1 >= 0 and x+1 < GRID_X*GRID_Y and cells[x+1][1] != '#'):
                cells[x+1][1] = '.'

            if(x-1 >= 0 and x-1 < GRID_X*GRID_Y and cells[x-1][1] != '#'):
                cells[x-1][1] = '.'

            if(x+GRID_X >= 0 and x+GRID_X < GRID_X*GRID_Y and cells[x+GRID_X][1] != '#'):
                cells[x+GRID_X][1] = '.'

            if(x-GRID_X >= 0 and x-GRID_X < GRID_X*GRID_Y and cells[x-GRID_X][1] != '#'):
                cells[x-GRID_X][1] = '.'

            break

        nextCell += fly


def requestInput():
    print("Enter input:")
    print("1) explore(L)")
    print("2) pickup")
    print("3) moveforward")
    print("4) turnleft")
    print("5) turnright")
    print("6) shoot")


def handleInput(input):
    global orientation
    global gameOver

    if input == "1":
        while True:
            if bool(list(prolog.query("explore(L)"))) is True:
                temp = list(prolog.query("explore(L)"))
                if len(temp) > 0:
                    actions = temp[0].get('L')
                    for a in actions:
                        print("Agent: ", a)
                        handleAction(a)
                    displayGridDynamic()
                    displayRelativeGrid()
            else:
                print("no available safe actions.")
                break
    if input == "2":
        grabCoin()
        sense()

    if input == "3":
        move()
        bool(list(prolog.query("move(moveforward,[{},{},{},{},{},{}])".format(
            currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5]))))

    if input == "4":
        turn(-1)
        (bool(list(prolog.query("move(turnleft,[{},{},{},{},{},{}])".format(
            currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))

    if input == "5":
        turn(1)
        (bool(list(prolog.query("move(turnright,[{},{},{},{},{},{}])".format(
            currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))

    if input == "6":
        if bool(list(prolog.query("hasarrow"))):
            shoot()
            (bool(list(prolog.query("move(shoot,[{},{},{},{},{},{}])".format(
                currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))

    if input == "t":
        print(bool(list(prolog.query("unexplored(0,1)"))))
        print(bool(list(prolog.query("unexplored(0,-1)"))))

    if input == "end":
        gameOver = True


def handleAction(a):
    if a == "pickup":
        grabCoin()
        sense()
    elif a == "moveforward":
        move()
        (bool(list(prolog.query("move(moveforward,[{},{},{},{},{},{}])".format(
            currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))
    elif a == "turnleft":
        turn(-1)
        (bool(list(prolog.query("move(turnleft,[{},{},{},{},{},{}])".format(
            currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))
    elif a == "turnright":
        turn(1)
        (bool(list(prolog.query("move(turnright,[{},{},{},{},{},{}])".format(
            currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))
    elif a == "shoot":
        if bool(list(prolog.query("hasarrow"))):
            shoot()
            (bool(list(prolog.query("move(shoot,[{},{},{},{},{},{}])".format(
                currentSenses[0], currentSenses[1], currentSenses[2], currentSenses[3], currentSenses[4], currentSenses[5])))))


def initializeCellData():

    global cells

    for i in range(len(cells)):
        cells[i][0] = "."
        cells[i][1] = "."
        cells[i][2] = "."
        cells[i][3] = " "
        cells[i][4] = "s"
        cells[i][5] = " "
        cells[i][6] = "."
        cells[i][7] = "."
        cells[i][8] = "."


def spawnCoin():
    x = 31  # random.randint(0, (GRID_X*GRID_Y)-1)
    if cells[x][6] != '.' or cells[x][4] == 'W' or cells[x][4] == 'O':
        return spawnCoin()
    cells[x][6] = '*'


def spawnConfundus(x):
    #x = random.randint(0, (GRID_X*GRID_Y)-1)
    if cells[x][4] != 's':
        return spawnConfundus()

    cells[x][4] = 'O'
    cells[x][3] = '-'
    cells[x][5] = '-'

    if(x+1 >= 0 and x+1 < GRID_X*GRID_Y and cells[x+1][1] != "#"):
        cells[x+1][2] = 'T'

    if(x-1 >= 0 and x-1 < GRID_X*GRID_Y and cells[x-1][1] != "#"):
        cells[x-1][2] = 'T'

    if(x+GRID_X >= 0 and x+GRID_X < GRID_X*GRID_Y and cells[x+GRID_X][1] != "#"):
        cells[x+GRID_X][2] = 'T'

    if(x-GRID_X >= 0 and x-GRID_X < GRID_X*GRID_Y) and cells[x-GRID_X][1] != "#":
        cells[x-GRID_X][2] = 'T'


def spawnWumpus():
    x = 32  # random.randint(0, (GRID_X*GRID_Y)-1)
    if cells[x][4] != 's':
        return spawnWumpus()

    cells[x][4] = 'W'
    cells[x][3] = '-'
    cells[x][5] = '-'

    if(x+1 >= 0 and x+1 < GRID_X*GRID_Y and cells[x+1][1] != '#'):
        cells[x+1][1] = '='

    if(x-1 >= 0 and x-1 < GRID_X*GRID_Y and cells[x-1][1] != '#'):
        cells[x-1][1] = '='

    if(x+GRID_X >= 0 and x+GRID_X < GRID_X*GRID_Y and cells[x+GRID_X][1] != '#'):
        cells[x+GRID_X][1] = '='

    if(x-GRID_X >= 0 and x-GRID_X < GRID_X*GRID_Y and cells[x-GRID_X][1] != '#'):
        cells[x-GRID_X][1] = '='


def spawnAgent():
    global currentCell
    x = 29  # random.randint(0, (GRID_X*GRID_Y)-1)
    if cells[x][4] != 's' or cells[x][2] != '.' or cells[x][1] != '.':
        spawnAgent()
    else:
        cells[x][4] = getPointer(directions[orientation])
        currentCell = x
        surroundAgentSymbol()


def setWalls():
    for n in range(0, GRID_X):
        for i in range(len(cells[n])):
            cells[n][i] = '#'

    for s in range((GRID_X * GRID_Y) - GRID_X, GRID_X * GRID_Y):
        for i in range(len(cells[s])):
            cells[s][i] = '#'

    for e in range((GRID_X - 1), GRID_X*GRID_Y, GRID_X):
        for i in range(len(cells[e])):
            cells[e][i] = '#'

    for w in range(0, ((GRID_Y * GRID_X) - GRID_X), GRID_X):
        for i in range(len(cells[w])):
            cells[w][i] = '#'


def resetSenses():
    global currentSenses
    for i in range(len(currentSenses)):
        currentSenses[i] = "off"

    currentSenses[0] = "on"


def resetAgent():
    global orientation
    orientation = 0


def setupWorld():
    initializeCellData()
    setWalls()
    # for i in range(3):
    spawnConfundus(8)
    spawnConfundus(15)
    spawnConfundus(19)

    spawnWumpus()
    spawnCoin()
    spawnAgent()
    resetAgent()
    resetSenses()
    sense()
    currentSenses[0] = "on"


if __name__ == '__main__':
    # test2()
    setupWorld()

    while gameOver is False:
        displayGridDynamic()
        displayRelativeGrid()
        print(currentSenses)
        printSenses()

        requestInput()
        temp = input()
        handleInput(temp)
