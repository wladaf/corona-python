from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import random
import math
import threading
from time import sleep
import numpy as np

global people

global sizeX
global sizeY

sizeX = 800
sizeY = 800

distanceFromHome = 100
waypointsCount = 6

chanceToDie = 7 #%
IllnessDistance = 5
illnessChance = 50 #%

peopleCount = 600

speed = 2

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def closeTo(self, otherPoint):
        return abs(self.x - otherPoint.x) <= 1 and abs(self.y - otherPoint.y) <= 1

    def distance(self, otherPoint):
        return (otherPoint.x - self.x, otherPoint.y - self.y)

class Man:
    def __init__(self, way, isIll):
        self.way = way
        self.isIll = isIll
        self.wasIll = False
        self.position = Point(way[0].x, way[0].y)
        self.nextPointIndex = 0
        self.life = 100
        self.contacts = []

    def wayLength(self):
        return len(self.way)

    def selectNextWaypoint(self):
        if self.nextPointIndex + 1 >= self.wayLength():
            self.nextPointIndex = 0
        else:
            self.nextPointIndex += 1

    def setIll(self, isIll):
        self.isIll = isIll
        if isIll:
            self.wasIll = True

def init():
    global people

    people = createPeople()

    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0.0, sizeX, 0.0, sizeY)

    thread = threading.Thread(target=startCalculationLoop)
    thread.daemon = True
    thread.start()

def randomInt(fromNumber, toNumber):
    # return np.random.randint(fromNumber, toNumber + 1)
    return random.randint(fromNumber, toNumber)

def movePeople():
    global people
    global speed

    for man in people:
        position = man.position
        #print("Position: (" + str(position.x) + ", " + str(position.y) + ")")
        nextPosition = man.way[man.nextPointIndex]
        #print("Next position at index " + str(man.nextPointIndex) + ": (" + str(nextPosition.x) + ", " + str(nextPosition.y) + ")")

        (xDistance, yDistance) = position.distance(nextPosition)

        distance = math.sqrt(xDistance * xDistance + yDistance * yDistance)
        #print("Distance: " + str(distance))

        if distance == 0:
            man.selectNextWaypoint()
            continue

        if distance > speed:
            coefficient = distance / speed
        else:
            coefficient = 1

        xDelta = xDistance / coefficient
        #print("XDelta: " + str(xDelta))
        yDelta = yDistance / coefficient
        #print("XDelta: " + str(yDelta))

        man.position.x += xDelta
        man.position.y += yDelta

        if man.position.closeTo(nextPosition):
            man.selectNextWaypoint()

def checkIllness():
    global people
    global illnessChance

    for man in people:
        if man.isIll == False:
            continue

        for otherMan in people:
            (xDistance, yDistance) = man.position.distance(otherMan.position)

            if abs(xDistance) < IllnessDistance and abs(yDistance) < IllnessDistance:
                if otherMan not in man.contacts:
                    man.contacts.append(otherMan)

                    otherManIllnessChance = illnessChance
                    if otherMan.wasIll:
                        otherManIllnessChance = illnessChance / 2

                    if randomInt(0, 100) < otherManIllnessChance:
                        otherMan.isIll = True
            else:
                if otherMan in man.contacts:
                    man.contacts.remove(otherMan)

def updateLife():
    global people

    for man in people:
        if man.isIll:
            man.life -= 0.5

            if man.life == 0:
                if randomInt(0, 100) <= chanceToDie:
                    people.remove(man)
                else:
                    man.life = 100
                    man.isIll = False

def startCalculationLoop():
    fps = 30

    while True:
        movePeople()
        checkIllness()
        updateLife()

        sleep(1 / fps)

def createPeople():
    people = []

    for index in range(0, peopleCount):
        way = createRandomWay()
        man = Man(way, False)
        if index == 0:
            man.setIll(True)
        people.append(man)

    return people


def createRandomWay():
    global sizeX
    global sizeY

    pointsCount = randomInt(1, waypointsCount)

    way = []

    home = Point(randomInt(0, sizeX),  randomInt(0, sizeY))
    way.append(home)

    for index in range(0, pointsCount):
        x = min(sizeX, max(0, home.x + randomInt(-distanceFromHome, distanceFromHome)))
        y = min(sizeY, max(0, home.y + randomInt(-distanceFromHome, distanceFromHome)))
        point = Point(x,  y)
        way.append(point)

    return way

def drawSquare(x, y):
    radius = 1

    glBegin(GL_QUADS)
    glVertex2f(x - radius, y - radius)
    glVertex2f(x - radius, y + radius)
    glVertex2f(x + radius, y + radius)
    glVertex2f(x + radius, y - radius)
    glEnd()

def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glPushMatrix()

    for man in people:
        if man.isIll:
            glColor3f(1.0, 0.0, 0.0)
        else:
            glColor3f(0.8, 0.8, 0.8)

        drawSquare(man.position.x, man.position.y)

    glPopMatrix()
    glutSwapBuffers()

def specialkeys(key, x, y):
    if key == GLUT_KEY_UP:
        exit()


glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(sizeX, sizeY)
glutInitWindowPosition(50, 50)
glutInit(sys.argv)
glutCreateWindow(b"Corona")
glutDisplayFunc(draw)
glutIdleFunc(draw)
glutSpecialFunc(specialkeys)

init()

glutMainLoop()
