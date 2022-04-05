import sys
import os
import os.path
import csv
import pandas as pd
import numpy as np
import time

from PIL import Image
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.fileName = None
        loadUi("mainWindow.ui", self)
        self.browse.clicked.connect(self.browseFiles)  # Calls the 'browseFiles' method when the 'browse' button is clicked
        self.generateBarcodes.clicked.connect(self.createBarcodeFile)  # Calls the 'createBarcodeFile' method when the 'Generate Barcode File' button is clicked


    def browseFiles(self):
        self.fileName = QFileDialog.getOpenFileName(self.browse, 'Open File', "/usr/MNIST_DS", "Images (*.png *.jpg *.jpeg *.bmp)")  # opens file browser at specified location setting the file types to images only
        self.imgPreview.setPixmap(QPixmap(self.fileName[0]))  # uploads the image to be viewed in the GUI
        self.imgPreview.setScaledContents(True)  # scales the uploaded image to fit the contents of the pre-defined box
        imageToSearchPath = self.fileName[0]

        self.imgResult.setPixmap(QPixmap(retrieveImage(generateBarcode(self.fileName[0]))))  # uploads the image to be viewed in the GUI
        self.imgResult.setScaledContents(True)  # scales the uploaded image to fit the contents of the pre-defined box

        print("ORIGINAL IMAGE", imageToSearchPath)


    def createBarcodeFile(self):
        barcodeFile = open("BARCODES.csv", "a", newline='')  # opens a csv file with the name "BARCODES" to be written in later
        imagePathFile = open("IMAGEPATH.csv", "w+", newline='')  # opens a csv file with the name "IMAGEPATH" to be written in later
        clearFile("BARCODES.csv")  # clears the file before writing in it
        clearFile("IMAGEPATH.csv")  # clears the file before writing in it
        writerB = csv.writer(barcodeFile)  # creates a new csv writer
        writerI = csv.writer(imagePathFile)  # creates a new csv writer
        writerB.writerow(generateHeader())  # writes header values
        writerI.writerow(["File Path"])  # writes header values
        rootDir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Root Folder:', "/usr/", QtWidgets.QFileDialog.ShowDirsOnly)  # opens file browser at specified location setting the selection types to folders only
        for subdir, dirs, files in os.walk(rootDir):  # walks through all sub-directories within the specified root-directory
            for file in files:
                barcodeArray = np.array(generateBarcode(os.path.join(subdir, file)))
                writerB.writerow(barcodeArray)  # writes the file barcode in the BARCODES.csv file
                writerI.writerow([os.path.join(subdir, file)]) # writes the file path in the IMAGEPATH.csv file
        barcodeFile.close()
        imagePathFile.close()


def retrieveImage(originalBarcode):
    if (os.path.exists('BARCODES.csv') and os.path.exists('IMAGEPATH.csv')):  # if the file is in read mode, then proceed
        barcodeArr = pd.read_csv("BARCODES.csv").values  # stores the contents of the "BARCODES.csv" file into a 2D array
        imagePathArr = pd.read_csv("IMAGEPATH.csv").values  # stores the contents of the "IMAGEPATH.csv" file into a 2D array

        resultImagePath = searchAlgorithm(barcodeArr, imagePathArr, originalBarcode)
        print(resultImagePath)
        return resultImagePath

    else:  # if the file is not in read mode, the program cannot find the specified file
        print("Files Not Found")  # output error message


def searchAlgorithm(barcodesArr, imagePathArr, originalBarcode):
    hammingDist = 1000  # initializes hamming distance variable
    filePath = ""
    for i in range(100):
        currentHammingDist = hammingDistance(barcodesArr[i], originalBarcode)
        if (currentHammingDist < hammingDist) and (currentHammingDist != 0):
            hammingDist = currentHammingDist
            filePath = imagePathArr[i][0]
    return filePath


def hammingDistance(currentBarcode, originalBarcode):
    hammingDist = 0  # initializes the hamming distance
    for i in range(162):  # loops through all 162 values of the barcode
        if originalBarcode[i] != currentBarcode[i]:  # if the barcode values are not the same...
            hammingDist += 1  # increase the hamming distance by 1
    return hammingDist  # return the hamming distance


def clearFile(path):
    with open(path, 'r+') as f:  # opens the file as read type, and truncates all values
        f.truncate(0)  # clears file completely


def generateHeader():
    header=[]
    for i in range(162):
        header.append(i)
    return header


def generateBarcode(imagePath):  # returns generated barcodes for each picture's file path that is passed
    image = Image.open(imagePath)  # opens the image at specified path and allows for conversion to numpy array
    imgArr = np.asarray(image.convert('L'))  # the image conver mode 'L' will only store luminance values or otherwise, greyscale

    sumOne = np.sum(imgArr, axis=1)  # computes the projection with projection angle set to 0 [Left --> Right]
    sumThree = np.sum(imgArr, axis=0)  # computes the projection with projection angle set to 90 [Top --> Down]
    sumTwo = [np.trace(imgArr, offset=i) for i in range(-np.shape(imgArr)[0] + 2, np.shape(imgArr)[1] - 1)]  # computes the projection with projection angle set to 45 [Top Left --> Bottom Right]
    sumFour = [np.trace(np.fliplr(imgArr), offset=i) for i in range(np.shape(imgArr)[1] - 2, -np.shape(imgArr)[0] + 1, -1)]  # computes the projection with projection angle set to 135 [Top Right --> Bottom Left]

    barcode = (convertSumsToBarcode(sumOne)+convertSumsToBarcode(sumTwo)+convertSumsToBarcode(sumThree)+convertSumsToBarcode(sumFour))  # concatenates all the barcodes into a single array
    return barcode


def convertSumsToBarcode(arr):
    c = []
    avg = round(np.asarray(arr).mean())
    for value in arr:
        if value > avg:
            c.append(1)
        else:
            c.append(0)
    return c


# CHANGE ROOT OF YOUR MINST_DS FOLDER
rootDir = "C:\Ontario Tech ~ Second Year\Data Structures\Final Project\Content-Based-Image-Retrieval\MNIST_DS"
for subdir, dirs, files in os.walk(rootDir):
    for file in files:
        imageToSearchPath = os.path.join(subdir, file)
        retrieveImage(generateBarcode(imageToSearchPath))
        print(imageToSearchPath)



app = QApplication(sys.argv)
mainWindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.setFixedWidth(680)
widget.setFixedHeight(460)
widget.show()
sys.exit(app.exec_())

