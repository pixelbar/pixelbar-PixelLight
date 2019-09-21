import requests
import json
import pygame
import os
import socket
import psutil
import datetime
#import RPi.GPIO as GPIO
from random import randint

pygame.init()

lights = []
buttons = []
sliders = []
connError = False
unicorn = False
iwab = False
mode = 0
stateRGB = 1
valRGB = 0
speed = 15
speedCur = 1
speedCnt = 1
selZone = [0, 0, 0, 0]
selZoneHand = [0, 0, 0, 0]
manOverride = [0, 0, 0, 0]
spaceState = False
spaceArr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
spaceCtr = 0
testMode = False
errCnt = 0
master = 0
tempReadEn = True
spaceTemp = 0
deg_sym = '°'
timeNow = 0
timeLast = 0

"""
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.OUT) # relais 1 FrontDoor
GPIO.setup(23, GPIO.OUT) # relais 2 PixelDoor
GPIO.setup(24, GPIO.OUT) # relais 3 DockLight
GPIO.setup(25, GPIO.OUT) # relais 4
GPIO.output(22, GPIO.HIGH)
GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.HIGH)
GPIO.output(25, GPIO.HIGH)
"""

frontDoorTrig = False
frontDoorTimer = 5000
frontDoorTime = 0
pixelDoorTrig = False
pixelDoorTimer = 5000
pixelDoorTime = 0

x = 0
y = 0

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DRKGREEN = (0, 100, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

PI = 3.141592653

buttonX = 30
buttonY = 510
lightX = 40
lightY = 75

displayInfo = pygame.display.Info()
windowSizeX = displayInfo.current_w
windowSizeY = displayInfo.current_h

size = [windowSizeX, windowSizeY]
screen = pygame.display.set_mode(size, pygame.NOFRAME)
pygame.display.flip()
my_clock = pygame.time.Clock()
pygame.display.set_caption("PixelbarManagementSystem")
#pygame.mouse.set_visible(False)

font = pygame.font.SysFont('Arial', 50, False, False)

class light(object):
    def __init__(self, id, zone, red, green, blue, white, tarRed, tarGreen, tarBlue, tarWhite, tarTempRed, tarTempGreen, tarTempBlue, tarTempWhite, x, y):
        self.id = id
        self.zone = zone
        self.red = red
        self.green = green
        self.blue = blue
        self.white = white
        self.tarRed = tarRed
        self.tarGreen = tarGreen
        self.tarBlue = tarBlue
        self.tarWhite = tarWhite
        self.tarTempRed = tarTempRed
        self.tarTempGreen = tarTempGreen
        self.tarTempBlue = tarTempBlue
        self.tarTempWhite = tarTempWhite
        self.x = x
        self.y = y

class button(object):
    def __init__(self, id, text, x, y, width, height, state):
        self.id = id
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state

def createLights():
    lights.append(light(0, 'Door', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lightX + 0 * 250, lightY))
    lights.append(light(1, 'Kitchen', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lightX + 1 * 250, lightY))
    lights.append(light(2, 'Stairs', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lightX + 2 * 250, lightY))
    lights.append(light(3, 'Beamer', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lightX + 3 * 250, lightY))

def createButtons():
    varX = 200
    varY = 80
    buttons.append(button(0, 'Pim', buttonX + 0 * varX, buttonY + 0 * varY, 190, 70, False))
    buttons.append(button(1, 'Courtisane', buttonX + 0 * varX, buttonY + 1 * varY, 190, 70, False))
    buttons.append(button(2, 'Off', buttonX + 0 * varX, buttonY + 2 * varY, 190, 70, False))
    buttons.append(button(3, 'Deselect all', buttonX + 1 * varX, buttonY + 0 * varY, 190, 70, False))
    buttons.append(button(4, 'Unicorn', buttonX + 1 * varX, buttonY + 1 * varY, 190, 70, False))
    buttons.append(button(5, 'Random', buttonX + 2 * varX, buttonY + 1 * varY, 190, 70, False))
    buttons.append(button(6, 'TestMode', buttonX + 0 * varX, buttonY + 6 * varY, 190, 70, True))
    buttons.append(button(7, '0.0.0.0', lights[0].x - 10, lightY + 330, 192, 60, False))
    buttons.append(button(8, '0.0.0.0', lights[1].x - 10, lightY + 330, 192, 60, False))
    buttons.append(button(9, '0.0.0.0', lights[2].x - 10, lightY + 330, 192, 60, False))
    buttons.append(button(10, '0.0.0.0', lights[3].x - 10, lightY + 330, 192, 60, False))
    buttons.append(button(11, 'Spare', 100, 5000, 190, 70, False))
    buttons.append(button(12, 'Door', lights[0].x - 10, lightY, 192, 60, False))
    buttons.append(button(13, 'Kitchen', lights[1].x - 10, lightY, 192, 60, False))
    buttons.append(button(14, 'Stairs', lights[2].x - 10, lightY, 192, 60, False))
    buttons.append(button(15, 'Beamer', lights[3].x - 10, lightY, 192, 60, False))
    buttons.append(button(16, 'FrontDoor', 1030, 865, 190, 70, False))
    buttons.append(button(17, 'PixelDoor', 280, 540, 190, 70, False))

def drawFunctions():
    global spaceState

    varX = 35
    varY = 10
    font = pygame.font.SysFont('Arial', 35, False, False)
    text = font.render("Light control", False, GREEN)
    screen.blit(text, [varX, varY])

    pygame.draw.line(screen, GREEN, [0, varY + 45], [varX - 10, varY + 45], 1)
    pygame.draw.line(screen, GREEN, [varX - 10, varY + 45], [varX - 10, 5], 1)
    pygame.draw.line(screen, GREEN, [varX - 10, varY + 45], [varX - 10, 5], 1)
    pygame.draw.line(screen, GREEN, [varX - 10, 5], [varX + text.get_rect().width + 10, 5], 1)
    pygame.draw.line(screen, GREEN, [varX + text.get_rect().width + 10, 5],
                     [varX + text.get_rect().width + 10, varY + 45], 1)
    if master == 0:
        pygame.draw.line(screen, GREEN, [varX + text.get_rect().width + 10, varY + 45], [windowSizeX, varY + 45], 1)
    else:
        pygame.draw.line(screen, GREEN, [varX - 10, varY + 45], [varX + text.get_rect().width + 25, varY + 45], 1)

    text = font.render("Access control", False, GREEN)
    divX = 225
    screen.blit(text, [varX + divX, varY])
    pygame.draw.line(screen, GREEN, [varX + divX - 10, 5], [varX + divX + text.get_rect().width + 10, 5], 1)
    pygame.draw.line(screen, GREEN, [varX + divX + text.get_rect().width + 10, 5],
                     [varX + divX + text.get_rect().width + 10, varY + 45], 1)
    pygame.draw.line(screen, GREEN, [varX + divX - 10, 5], [varX + divX - 10, varY + 45], 1)
    if master == 1:
        pygame.draw.line(screen, GREEN, [0, varY + 45], [varX + divX - 10, varY + 45], 1)
        pygame.draw.line(screen, GREEN, [varX + divX + text.get_rect().width + 10, varY + 45], [windowSizeX, varY + 45],
                         1)
    else:
        pygame.draw.line(screen, GREEN, [varX + divX - 26, varY + 45], [varX + divX + 252, varY + 45], 1)

    text = font.render("Settings", False, GREEN)
    divX = 487
    screen.blit(text, [varX + divX, varY])
    pygame.draw.line(screen, GREEN, [varX + divX - 10, 5], [varX + divX + text.get_rect().width + 10, 5], 1)
    pygame.draw.line(screen, GREEN, [varX + divX + text.get_rect().width + 10, 5],
                     [varX + divX + text.get_rect().width + 10, varY + 45], 1)
    pygame.draw.line(screen, GREEN, [varX + divX - 10, 5], [varX + divX - 10, varY + 45], 1)
    if master == 2:
        pygame.draw.line(screen, GREEN, [0, varY + 45], [varX + divX - 10, varY + 45], 1)
    else:
        pygame.draw.line(screen, GREEN, [varX + divX - 26, varY + 45], [varX + divX + 252, varY + 45], 1)
    pygame.draw.line(screen, GREEN, [varX + divX + text.get_rect().width + 10, varY + 45], [windowSizeX, varY + 45], 1)

    text = font.render("Exit", False, GREEN)
    screen.blit(text, [varX + 1700, varY])
    pygame.draw.line(screen, GREEN, [varX + 1700 - 10, 5], [varX + 1700 - 10, varY + 45], 1)
    pygame.draw.line(screen, GREEN, [varX + 1700 - 10, 5], [varX + 1700 + text.get_rect().width + 10, 5], 1)
    pygame.draw.line(screen, GREEN, [varX + 1700 + text.get_rect().width + 10, 5],
                     [varX + 1700 + text.get_rect().width + 10, varY + 45], 1)

    if spaceState:
        text = font.render("Space is Open", False, GREEN)
    else:
        text = font.render("Space is Closed", False, RED)
    screen.blit(text, [varX + 750, varY])

def drawLights():
    for i in range(len(lights)):
        varTop = 60
        varLength = varTop + 200 + 39 - 20

        pygame.draw.line(screen, GREEN, [lights[i].x + 10, lights[i].y + varTop + 20],
                         [lights[i].x + 10, lights[i].y + varLength + 10], 1)
        pygame.draw.line(screen, GREEN, [lights[i].x + 60, lights[i].y + varTop + 20],
                         [lights[i].x + 60, lights[i].y + varLength + 10], 1)
        pygame.draw.line(screen, GREEN, [lights[i].x + 110, lights[i].y + varTop + 20],
                         [lights[i].x + 110, lights[i].y + varLength + 10], 1)
        pygame.draw.line(screen, GREEN, [lights[i].x + 160, lights[i].y + varTop + 20],
                         [lights[i].x + 160, lights[i].y + varLength + 10], 1)
        pygame.draw.rect(screen, BLACK, [lights[i].x - 10, lights[i].y + varLength - lights[i].tarRed * 2, 41, 15])
        pygame.draw.rect(screen, BLACK, [lights[i].x + 40, lights[i].y + varLength - lights[i].tarGreen * 2, 41, 15])
        pygame.draw.rect(screen, BLACK, [lights[i].x + 90, lights[i].y + varLength - lights[i].tarBlue * 2, 41, 15])
        pygame.draw.rect(screen, BLACK, [lights[i].x + 140, lights[i].y + varLength - lights[i].tarWhite * 2, 41, 15])
        pygame.draw.rect(screen, GREEN, [lights[i].x - 10, lights[i].y + varLength - lights[i].tarRed * 2, 41, 15], 1)
        pygame.draw.rect(screen, GREEN, [lights[i].x + 40, lights[i].y + varLength - lights[i].tarGreen * 2, 41, 15], 1)
        pygame.draw.rect(screen, GREEN, [lights[i].x + 90, lights[i].y + varLength - lights[i].tarBlue * 2, 41, 15], 1)
        pygame.draw.rect(screen, GREEN, [lights[i].x + 140, lights[i].y + varLength - lights[i].tarWhite * 2, 41, 15],
                         1)
        pygame.draw.rect(screen, RED, [lights[i].x - 10, lights[i].y + varLength - lights[i].red * 2, 41, 15], 1)
        pygame.draw.rect(screen, RED, [lights[i].x + 40, lights[i].y + varLength - lights[i].green * 2, 41, 15], 1)
        pygame.draw.rect(screen, RED, [lights[i].x + 90, lights[i].y + varLength - lights[i].blue * 2, 41, 15], 1)
        pygame.draw.rect(screen, RED, [lights[i].x + 140, lights[i].y + varLength - lights[i].white * 2, 41, 15], 1)

        font = pygame.font.SysFont('Arial', 25, False, False)
        if selZone[i] == 1 or selZone[i] == 2:
            buttons[i + 12].state = True
        else:
            buttons[i + 12].state = False

        font = pygame.font.SysFont('Arial', 20, False, False)
        text = font.render("R", False, GREEN)
        screen.blit(text, [lights[i].x - text.get_rect().width / 2 + 10, lights[i].y + 300])
        text = font.render("G", False, GREEN)
        screen.blit(text, [lights[i].x - text.get_rect().width / 2 + 60, lights[i].y + 300])
        text = font.render("B", False, GREEN)
        screen.blit(text, [lights[i].x - text.get_rect().width / 2 + 110, lights[i].y + 300])
        text = font.render("W", False, GREEN)
        screen.blit(text, [lights[i].x - text.get_rect().width / 2 + 160, lights[i].y + 300])

    #
    # Draw buttons
    #
    font = pygame.font.SysFont('Arial', 30, False, False)
    for i in range(0, 16):
        if buttons[i].state == False:
            pygame.draw.rect(screen, GREEN, [buttons[i].x, buttons[i].y, buttons[i].width, buttons[i].height], 1)
            text = font.render(buttons[i].text, False, GREEN)
        else:
            pygame.draw.rect(screen, GREEN, [buttons[i].x, buttons[i].y, buttons[i].width, buttons[i].height])
            text = font.render(buttons[i].text, False, BLACK)
        screen.blit(text, [buttons[i].x + round(buttons[i].width / 2) - text.get_rect().width / 2,
                           buttons[i].y + round(buttons[i].height / 2) - text.get_rect().height / 2])

    if iwab:
        text = font.render("Smart-Ass mode activated", False, RED)
        screen.blit(text, [((buttonX + windowSizeX - (2 * buttonX)) / 2) - (text.get_rect().width / 2), buttonY + 85])

    text = font.render("Speed", False, GREEN)
    screen.blit(text, [buttonX + 95 - text.get_rect().width / 2, buttonY + 280])
    pygame.draw.line(screen, GREEN, [buttonX, buttonY + 350], [buttonX + 209, buttonY + 350], 1)
    pygame.draw.rect(screen, BLACK, [buttonX + (speedCur * 2), buttonY + 330, 15, 40])
    pygame.draw.rect(screen, GREEN, [buttonX + (speedCur * 2), buttonY + 330, 15, 40], 1)

def drawDoor():
    global spaceTemp
    #
    # Draw buttons
    #
    font = pygame.font.SysFont('Arial', 30, False, False)
    for i in range(16, 18):
        if buttons[i].state == False:
            pygame.draw.rect(screen, GREEN, [buttons[i].x, buttons[i].y, buttons[i].width, buttons[i].height], 1)
            text = font.render(buttons[i].text, False, GREEN)
        else:
            pygame.draw.rect(screen, GREEN, [buttons[i].x, buttons[i].y, buttons[i].width, buttons[i].height])
            text = font.render(buttons[i].text, False, BLACK)
        screen.blit(text, [buttons[i].x + round(buttons[i].width / 2) - text.get_rect().width / 2,
                           buttons[i].y + round(buttons[i].height / 2) - text.get_rect().height / 2])

    #
    # Draw map
    #
    x = 500
    y = 250
    pygame.draw.line(screen, GREEN, [x + 500, y - 150], [x + 500, y - 175], 1)
    pygame.draw.line(screen, GREEN, [x + 490, y - 150], [x + 510, y - 150], 1)
    pygame.draw.line(screen, GREEN, [x + 475, y - 75], [x + 525, y - 125], 1)
    pygame.draw.line(screen, GREEN, [x + 475, y - 125], [x + 525, y - 75], 1)
    pygame.draw.line(screen, GREEN, [x + 490, y - 50], [x + 510, y - 50], 1)
    pygame.draw.line(screen, GREEN, [x + 500, y], [x + 500, y - 50], 1)
    pygame.draw.line(screen, GREEN, [x + 500, y], [x + 250, y], 1)
    pygame.draw.line(screen, GREEN, [x + 250, y], [x + 250, y + 250], 1)
    pygame.draw.line(screen, GREEN, [x + 250, y + 250], [x, y + 250], 1)
    pygame.draw.line(screen, GREEN, [x, y + 250], [x, y + 275], 1)
    pygame.draw.line(screen, GREEN, [x - 10, y + 275], [x + 10, y + 275], 1)
    pygame.draw.line(screen, GREEN, [x - 10, y + 375], [x + 10, y + 375], 1)
    pygame.draw.line(screen, GREEN, [x, y + 375], [x, y + 550], 1)
    pygame.draw.line(screen, GREEN, [x, y + 550], [x + 500, y + 550], 1)
    pygame.draw.line(screen, GREEN, [x + 500, y + 550], [x + 500, y + 600], 1)
    pygame.draw.line(screen, GREEN, [x + 490, y + 600], [x + 510, y + 600], 1)
    pygame.draw.line(screen, GREEN, [x + 490, y + 700], [x + 510, y + 700], 1)
    pygame.draw.line(screen, GREEN, [x + 500, y + 700], [x + 500, y + 800], 1)
    pygame.draw.line(screen, GREEN, [x + 500, y], [x + 500, y + 600], 1)
    font = pygame.font.SysFont('Arial', 35, True, False)
    text = font.render("Pixelbar", False, GREEN)
    screen.blit(text, [x + 200, y + 350])

    #5
    # Draw temperature
    #

    text = font.render(str(spaceTemp) + " " + deg_sym + "C", False, GREEN)
    screen.blit(text, [x + 200, y + 400])

def getLightValues():
    global connError

    if not testMode and not mouseDown:
        connError = False
        URLget = "http://172.30.101.101:1234/api/serial"
        try:
            r = requests.get(URLget, timeout=0.5)

        except: # requests.exceptions.Timeout:
            connError = True

        if not connError:
            connError = False
            response = r.json()
            lights[0].red = response['door']['red']
            lights[0].green = response['door']['green']
            lights[0].blue = response['door']['blue']
            lights[0].white = response['door']['white']
            lights[1].red = response['kitchen']['red']
            lights[1].green = response['kitchen']['green']
            lights[1].blue = response['kitchen']['blue']
            lights[1].white = response['kitchen']['white']
            lights[2].red = response['stairs']['red']
            lights[2].green = response['stairs']['green']
            lights[2].blue = response['stairs']['blue']
            lights[2].white = response['stairs']['white']
            lights[3].red = response['beamer']['red']
            lights[3].green = response['beamer']['green']
            lights[3].blue = response['beamer']['blue']
            lights[3].white = response['beamer']['white']

        if connError:
            font = pygame.font.SysFont('Arial', 30, False, False)
            text = font.render(str("Geen verbinding met de server"), False, RED)
            screen.blit(text, [510, 515])

def getSpaceState():
    global spaceState
    global spaceCtr
    global door

    connError2 = False

    URL2get = "https://spacestate.pixelbar.nl/spacestate.php"

    try:
        r2 = requests.get(URL2get, timeout=0.5)

    except: # requests.exceptions.Timeout: # except:  #
        connError2 = True
        door = 0

    if not connError2:
        responseState = r2.json()

        spaceCtr += 1
        if spaceCtr > 9:
            spaceCtr = 0

        if responseState['state'] == 'open':
            spaceArr[spaceCtr] = 1
        else:
            spaceArr[spaceCtr] = 0

    tempState = 0
    for i in range(len(spaceArr)):
        if spaceArr[i] == 1:
            tempState += 1

    if tempState > 8:
        spaceState = True
    else:
        spaceState = False

def getSpaceTemp():
    global tempReadEn
    global spaceTemp

    tempReadEn = False
    connError3 = False
    URL3get = "http://172.30.101.2:8080/temp.json"

    try:
        r3 = requests.get(URL3get, timeout=0.5)

    except: # requests.exceptions.Timeout:  # except:  #
        connError3 = True

    if not connError3:
        jsonCont = r3.json()

    spaceTemp = jsonCont['AccelTemp']

    print("spaceTemp uitgelezen")

def controlOutputs():
    global frontDoorTrig
    global pixelDoorTrig
    global spaceState
    """
    # 
    # Control doors
    #
    if frontDoorTrig:
        if pygame.time.get_ticks() < frontDoorTime + frontDoorTimer:
            buttons[16].state = True
            GPIO.output(22, GPIO.LOW)
        else:
            frontDoorTrig = False
            buttons[16].state = False
    else: 
        GPIO.output(22, GPIO.HIGH)

    if pixelDoorTrig:
        if pygame.time.get_ticks() < pixelDoorTime + pixelDoorTimer:
            buttons[17].state = True
            GPIO.output(23, GPIO.LOW)
        else:
            pixelDoorTrig = False
            buttons[17].state = False
    else: 
        GPIO.output(23, GPIO.HIGH)
    """
    """
    # 
    # Control DockLight
    #
    if spaceState:
        GPIO.output(24, GPIO.LOW)
    else:
        GPIO.output(24, GPIO.HIGH)
    """

def sendLightValue():
    global testMode
    global connError

    if not testMode and not connError:
        if mode == 4 or mode == 5:
            URLset = "http://172.30.101.101:1234/api/set"
            HEAD = {'content-type': 'application/json'}
            DATA = {'door': {'red': lights[0].tarRed, 'green': lights[0].tarGreen, 'blue': lights[0].tarBlue, 'white': lights[0].tarWhite},
                    'stairs': {'red': lights[2].tarRed, 'green': lights[2].tarGreen, 'blue': lights[2].tarBlue, 'white': lights[2].tarWhite},
                    'beamer': {'red': lights[3].tarRed, 'green': lights[3].tarGreen, 'blue': lights[3].tarBlue, 'white': lights[3].tarWhite},
                    'kitchen': {'red': lights[1].tarRed, 'green': lights[1].tarGreen, 'blue': lights[1].tarBlue, 'white': lights[1].tarWhite},}

            r = requests.post(URLset, data=json.dumps(DATA), headers=HEAD)
        else:
            if mouseDown:
                URLset = "http://172.30.101.101:1234/api/set"
                HEAD = {'content-type': 'application/json'}
                DATA = {'door': {'red': lights[0].tarRed, 'green': lights[0].tarGreen, 'blue': lights[0].tarBlue, 'white': lights[0].tarWhite},
                        'stairs': {'red': lights[2].tarRed, 'green': lights[2].tarGreen, 'blue': lights[2].tarBlue, 'white': lights[2].tarWhite},
                        'beamer': {'red': lights[3].tarRed, 'green': lights[3].tarGreen, 'blue': lights[3].tarBlue, 'white': lights[3].tarWhite},
                        'kitchen': {'red': lights[1].tarRed, 'green': lights[1].tarGreen, 'blue': lights[1].tarBlue, 'white': lights[1].tarWhite}, }

                r = requests.post(URLset, data=json.dumps(DATA), headers=HEAD)

def getPiInfo():
    global ip_address

    cpuUse = 0
    cpuClk = 0
    memUse1 = 0
    memUse2 = 0
    sdCard1 = 0
    sdCard2 = 0
    cpuTemp = 'temp'

    font = pygame.font.SysFont('Arial', 30, False, False)
    # get IP
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()

    # get CPU en mem usage
    if pygame.time.get_ticks() % 100 == 0:
        cpuUse = psutil.cpu_percent(interval=0.5)
        memUse1 = psutil.virtual_memory().percent
        memUse2 = (psutil.virtual_memory().total - psutil.virtual_memory().available) / 1048567
        sdCard1 = psutil.disk_usage('/').percent
        sdCard2 = psutil.disk_usage('/').used / 1073741824
        temp = os.popen('vcgencmd measure_temp').readline()
        cpuTemp = temp.replace("temp=", "").replace("'C\n", "")
        cpuClk = psutil.cpu_freq().current

    varX = 35
    varY = 75
    text = font.render("IP-adres: " + str(ip_address), False, GREEN)
    screen.blit(text, [varX, varY + 0 * 35])
    text = font.render("CPU-usage: " + str(cpuUse) + "%", False, GREEN)
    screen.blit(text, [varX, varY + 1 * 35])
    text = font.render("CPU-clock: " + str(cpuClk) + " MHz", False, GREEN)
    screen.blit(text, [varX, varY + 2 * 35])
    text = font.render("CPU temp: " + str(cpuTemp) + " 'C", False, GREEN)
    screen.blit(text, [varX, varY + 3 * 35])
    text = font.render("mem-usage: " + str(memUse1) + "% (" + str(round(memUse2, 2)) + " Mb)", False, GREEN)
    screen.blit(text, [varX, varY + 4 * 35])
    text = font.render("SD-card: " + str(sdCard1) + "% (" + str(round(sdCard2, 2)) + " Gb)", False, GREEN)
    screen.blit(text, [varX, varY + 5 * 35])

createLights()

createButtons()

done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()

                if master == 0:
                    for i in range(0, 16):
                        if pos[0] > buttons[i].x and pos[0] < buttons[i].x + buttons[i].width:
                            if pos[1] > buttons[i].y and pos[1] < buttons[i].y + buttons[i].height:
                                if buttons[i].id == 3:      # Deselect all
                                    selZone = [0, 0, 0, 0]
                                elif buttons[i].id == 6:    # TestMode
                                    if testMode:
                                        testMode = False
                                    else:
                                        testMode = True
                                elif buttons[i].id == 7:    # Door off
                                    if manOverride[0] == 1:
                                        manOverride[0] = 0
                                    else:
                                        manOverride[0] = 1
                                elif buttons[i].id == 8:    # Kitchen off
                                    if manOverride[1] == 1:
                                        manOverride[1] = 0
                                    else:
                                        manOverride[1] = 1
                                elif buttons[i].id == 9:    # Stairs off
                                    if manOverride[2] == 1:
                                        manOverride[2] = 0
                                    else:
                                        manOverride[2] = 1
                                elif buttons[i].id == 10:    # Beamer off
                                    if manOverride[3] == 1:
                                        manOverride[3] = 0
                                    else:
                                        manOverride[3] = 1
                                elif buttons[i].id == 12 or buttons[i].id == 13 or buttons[i].id == 14 or buttons[i].id == 15:
                                    selZoneAdj = False
                                    if selZone[i - 12] == 1:
                                        selZone[i - 12] = 0
                                    else:
                                        selZone[i - 12] = 1
                                else:                       # Other button
                                    mode = buttons[i].id
                                    if mode == 4:
                                        speedCur = 100
                                    elif mode == 5:
                                        speedCur = 1
                elif master == 1:
                    for i in range(16, 18):
                        if pos[0] > buttons[i].x and pos[0] < buttons[i].x + buttons[i].width:
                            if pos[1] > buttons[i].y and pos[1] < buttons[i].y + buttons[i].height:
                                if i == 16:
                                    frontDoorTrig = True
                                    frontDoorTime = pygame.time.get_ticks()
                                elif i == 17:
                                    pixelDoorTrig = True
                                    pixelDoorTime = pygame.time.get_ticks()

    screen.fill(BLACK)

    getSpaceState()

    #
    # If a mousebutton is pressed check is an action is required
    #
    if pygame.mouse.get_pressed()[0]:
        mouseDown = True
        mouseCurX = pygame.mouse.get_pos()[0]
        mouseCurY = pygame.mouse.get_pos()[1]
        
        #text = font.render("X," + str(mouseCurX) + " Y, " + str(mouseCurY), False, BLUE)
        #screen.blit(text, [500, 500])
        
        if mouseCurY > 5 and mouseCurY < 55:
            if mouseCurX > 1725 and mouseCurX < 1802:
                done = True
            elif mouseCurX > 25 and mouseCurX < 235:
                master = 0
            elif mouseCurX > 250 and mouseCurX < 495:
                master = 1
            elif mouseCurX > 500 and mouseCurX < 665:
                master = 2
        
        if master == 0:
            for i in range(len(lights)):
                if mouseCurX > lights[i].x - 10 and mouseCurX < lights[i].x + 31:
                    if mouseCurY > lights[i].y + 80 and mouseCurY < lights[i].y + 80 + 200:
                        mode = 3
                        selZoneHand[i] = 1
                        selZone[i] = 2
                        newVar = round(-1 * (mouseCurY - (lights[i].y + 80 + 200)) / 2)
                        if newVar > 100:
                            newVar = 100
                        if newVar < 0:
                            newVar = 0
                        lights[i].tarTempRed = newVar
                elif mouseCurX > lights[i].x + 40 and mouseCurX < lights[i].x + 81:
                    if mouseCurY > lights[i].y + 80 and mouseCurY < lights[i].y + 80 + 200:
                        mode = 3
                        selZoneHand[i] = 1
                        selZone[i] = 2
                        newVar = round(-1 * (mouseCurY - (lights[i].y + 80 + 200)) / 2)
                        if newVar > 100:
                            newVar = 100
                        if newVar < 0:
                            newVar = 0
                        lights[i].tarTempGreen = newVar
                elif mouseCurX > lights[i].x + 90 and mouseCurX < lights[i].x + 131:
                    if mouseCurY > lights[i].y + 80 and mouseCurY < lights[i].y + 80 + 200:
                        mode = 3
                        selZoneHand[i] = 1
                        selZone[i] = 2
                        newVar = round(-1 * (mouseCurY - (lights[i].y + 80 + 200)) / 2)
                        if newVar > 100:
                            newVar = 100
                        if newVar < 0:
                            newVar = 0
                        lights[i].tarTempBlue = newVar
                elif mouseCurX > lights[i].x + 140 and mouseCurX < lights[i].x + 181:
                    if mouseCurY > lights[i].y + 80 and mouseCurY < lights[i].y + 80 + 200:
                        mode = 3
                        selZoneHand[i] = 1
                        selZone[i] = 2
                        newVar = round(-1 * (mouseCurY - (lights[i].y + 80 + 200)) / 2)
                        if newVar > 100:
                            newVar = 100
                        if newVar < 0:
                            newVar = 0
                        lights[i].tarTempWhite = newVar
            if mouseCurX > 30 and mouseCurX < 227:
                if mouseCurY > 840 and mouseCurY < 880:
                    newVar = round((mouseCurX - 30) / 2)
                    if newVar > 100:
                        newVar = 100
                    if newVar < 0:
                        newVar = 0
                    speedCur = newVar
    else:
        mouseDown = False
        if master == 0:
            for i in range(len(selZone)):
                if selZone[i] == 2:
                    selZone[i] = 0

    #
    # Set relais to control the doors
    #

    getLightValues()

    #
    # calculate animation speed
    #
    speed = 15 - round((speedCur * 15) / 100)
    if speed < 1: speed = 1

    #
    # Depending on mode, calculate new target values
    #
    for i in range(0, 16):
        buttons[i].state = False

    buttons[6].state = testMode

    if mode == 0: # Default 1
        buttons[0].state = True
        unicorn = False
        iwab = False
        for i in range(len(lights)):
            lights[i].tarTempRed = 100
            lights[i].tarTempGreen = 20
            lights[i].tarTempBlue = 0
            lights[i].tarTempWhite = 100
    elif mode == 1: # Courtisane 2
        buttons[1].state = True
        unicorn = False
        iwab = False
        for i in range(len(lights)):
            lights[i].tarTempRed = 100
            lights[i].tarTempGreen = 0
            lights[i].tarTempBlue = 0
            lights[i].tarTempWhite = 0
    elif mode == 2:   # Off 0
        buttons[2].state = True
        unicorn = False
        for i in range(len(lights)):
            lights[i].tarTempRed = 0
            lights[i].tarTempGreen = 0
            lights[i].tarTempBlue = 0
            lights[i].tarTempWhite = 0
    elif mode == 3: # Smart ass 4
        iwab = True
        unicorn = False
    elif mode == 4: # Unicorn 3
        buttons[4].state = True
        unicorn = True
        iwab = False

        speedCnt += 1
        if speedCnt > 100:
            speedCnt = 1

        if speedCnt % speed == 0:
            for i in range(len(lights)):
                lights[i].tarTempWhite = 0
            if stateRGB == 0:
                for i in range(len(lights)):
                    lights[i].tarTempGreen = 0
                    lights[i].tarTempBlue = 0
                valRGB += 1
                for i in range(len(lights)):
                    lights[i].tarTempRed = valRGB
                if valRGB > 100:
                    stateRGB = 1
                    valRGB = 0
            elif stateRGB == 1:
                for i in range(len(lights)):
                    lights[i].tarTempRed = 100
                    lights[i].tarTempBlue = 0
                valRGB += 1
                for i in range(len(lights)):
                    lights[i].tarTempGreen = valRGB
                if valRGB > 100:
                    stateRGB = 2
            elif stateRGB == 2:
                for i in range(len(lights)):
                    lights[i].tarTempGreen = 100
                    lights[i].tarTempBlue = 0
                valRGB -= 1
                for i in range(len(lights)):
                    lights[i].tarTempRed = valRGB
                if valRGB < 0:
                    stateRGB = 3
            elif stateRGB == 3:
                for i in range(len(lights)):
                    lights[i].tarTempGreen = 100
                    lights[i].tarTempRed = 0
                valRGB += 1
                for i in range(len(lights)):
                    lights[i].tarTempBlue = valRGB
                if valRGB > 100:
                    stateRGB = 4
            elif stateRGB == 4:
                for i in range(len(lights)):
                    lights[i].tarTempBlue = 100
                    lights[i].tarTempRed = 0
                valRGB -= 1
                for i in range(len(lights)):
                    lights[i].tarTempGreen = valRGB
                if valRGB < 0:
                    stateRGB = 5
            elif stateRGB == 5:
                for i in range(len(lights)):
                    lights[i].tarTempBlue = 100
                    lights[i].tarTempGreen = 0
                valRGB += 1
                for i in range(len(lights)):
                    lights[i].tarTempRed = valRGB
                if valRGB > 100:
                    stateRGB = 6
            elif stateRGB == 6:
                for i in range(len(lights)):
                    lights[i].tarTempRed = 100
                    lights[i].tarTempGreen = 0
                valRGB -= 1
                for i in range(len(lights)):
                    lights[i].tarTempBlue = valRGB
                if valRGB < 0:
                    stateRGB = 1
    elif mode == 5: # Random 5
        buttons[5].state = True
        iwab = False
        unicorn = False

        speedCnt += 1
        if speedCnt > 100:
            speedCnt = 1

        if speedCnt % speed == 0:
            for i in range(len(lights)):
                lights[i].tarTempRed = randint(1, 100)
                lights[i].tarTempGreen = randint(1, 100)
                lights[i].tarTempBlue = randint(1, 100)
                lights[i].tarTempWhite = randint(1, 50)

    #
    # Change buttonstate from override switches
    #
    for i in range(len(manOverride)):
        if manOverride[i] == 1:
            buttons[i + 7].state = True
        else:
            buttons[i + 7].state = False

    #
    # Put new values depending on choices
    #
    if mode == 3: # 4
        zoneSet = False
        for i in range(len(selZone)):
            if selZone[i] == 1:
                if selZoneHand[i] != 1:
                    selZoneHand[i] = 2
        for i in range(len(selZoneHand)):
            if selZoneHand[i] == 1:
                zoneSet = True
                tempRed = lights[i].tarTempRed
                tempGreen =lights[i].tarTempGreen
                tempBlue = lights[i].tarTempBlue
                tempWhite = lights[i].tarTempWhite
        if zoneSet:
            for i in range(len(selZoneHand)):
                if selZoneHand[i] == 1 or selZoneHand[i] == 2:
                    lights[i].tarRed = tempRed
                    lights[i].tarGreen = tempGreen
                    lights[i].tarBlue = tempBlue
                    lights[i].tarWhite = tempWhite
        selZoneHand = [0,0,0,0]
    else:
        for i in range(len(lights)):
            if not manOverride[i] == 1:
                lights[i].tarRed = lights[i].tarTempRed
                lights[i].tarGreen = lights[i].tarTempGreen
                lights[i].tarBlue = lights[i].tarTempBlue
                lights[i].tarWhite = lights[i].tarTempWhite
            else:
                lights[i].tarRed = 0
                lights[i].tarGreen = 0
                lights[i].tarBlue = 0
                lights[i].tarWhite = 0

    #
    # Draw screen
    #
    if master == 0:
        drawLights()
    
    elif master == 1:
        drawDoor()

        timeNow = datetime.datetime.now().minute
        if round(datetime.datetime.now().minute % 10) == 0:
            if timeNow != timeLast:
                timeLast = timeNow
                tempReadEn = True

        if tempReadEn:
            getSpaceTemp()
        
    elif master == 2:
        getPiInfo()
        
    drawFunctions()

    sendLightValue()

    pygame.display.flip()
    my_clock.tick(30)

# on exit
"""
GPIO.output(22, GPIO.HIGH)
GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.HIGH)
GPIO.output(25, GPIO.HIGH)
"""
pygame.quit()