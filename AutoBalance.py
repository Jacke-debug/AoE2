import numpy as np 
import cv2
from PIL import ImageGrab
from PIL import Image
import ctypes
from pytesseract import image_to_string
import pytesseract
import time
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import itertools

def interpertText(text):
    text = text.replace(",", "")
    text = text.replace(".", "")
    players = []
    elo = []
    for row in text.splitlines():
        if (not not row) and not (row.startswith("Close") or row.startswith("Open")):
            elo.append(int(row[1:5]))
            players.append(row[7:])
    elo = np.array(elo)
    return (players, elo)

def optimalTeams(players, elo):
    nop = len(elo)
    teamSize = int(nop/2)
    halfElo = elo.sum()/2
    prevBest = halfElo
    for combination in itertools.combinations(range(nop), teamSize):
        teamElo = 0
        for index in combination:
            teamElo = teamElo + elo[index]
    
        teamDiff = abs(halfElo-teamElo)
        if teamDiff<prevBest:
            prevBest = teamDiff
            bestTeam = combination

    team1Index = set(combination)
    team2Index = set(range(teamSize))-team1Index

    my_str = "Team 1:"
    for i in team1Index:
        my_str = my_str + "\'"+players[i] + "\' "
    
    my_str = my_str + "\nTeam 2:"
    for i in team2Index:
        my_str = my_str + "\'"+players[i] + "\' "
        
    return my_str

def getImage(location):
    # take a snapshot of lobby
    screen = ImageGrab.grab(bbox=location)
    img = np.array(screen)
    return img

def manipulateColor(img):
    # RGB representation
    greenText = np.logical_and(img[:, :,0]>180, img[:, :, 1]<20)
    redText = img[:, :, 1]>180
    allText = np.logical_or(greenText, redText)

    # create a new image with same size as original
    image = img
    image[:, :, 0] = (1-allText)*255
    image[:, :, 1] = (1-allText)*255
    image[:, :, 2] = (1-allText)*255
    #image = gaussian_filter(image, sigma=0.1)
    return image


def readText(img):
    # Read text from image
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:/Program Files (x86)/Tesseract-OCR/tesseract")
    text = pytesseract.image_to_string(img,  config='--psm 11')
    return text

def main():
    img = Image.open("testImageCut.PNG")
    location = (210, 120, 413, 370)
    img = getImage(location)
    refinedImage = manipulateColor(img)
    text = readText(refinedImage)
    print(text)
    players,elo = interpertText(text)
    result = optimalTeams(players, elo)
    print(result)

main()

# TODO: add a function to calucalte location based on screen size?
# user32 = ctypes.windll.user32
# screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)