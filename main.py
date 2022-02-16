import sys
import os

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

import numpy as np
from PIL import Image


class MainMenu(QDialog):
    def __init__(self):
        super().__init__()
        self.fileName = None
        loadUi("MainMenu.ui", self)
        self.imgUpload.clicked.connect(self.uploadImage)
        self.searchBtn.clicked.connect(self.searchImage)

    def uploadImage(self):
        self.fileName = QFileDialog.getOpenFileName(self.imgUpload, 'Open File', "/usr/tmp", "Images (*.png *.jpg *.jpeg)")
        self.imgPreview.setPixmap(QPixmap(self.fileName[0]))

    def searchImage(self):
        print(self.fileName)
        resultsPage = ResultsPage(self.fileName[0])
        widget.addWidget(resultsPage)
        widget.setCurrentIndex(widget.currentIndex()+1)


class ResultsPage(QDialog):
    def __init__(self, filePath):
        super().__init__()
        loadUi("ResultsPage.ui", self)
        self.filePath = filePath
        self.searchAlgorithm()

    def searchAlgorithm(self):
        searchBarcode = self.generateBarcode(self.filePath)
        hammingDist = 100000
        closestMatch = ""

        cwd = os.getcwd()
        MNIST_path = os.path.join(cwd, 'MNIST_DS')
        classes = os.listdir(MNIST_path)
        for img_folder in classes:
            images_path = os.path.join(MNIST_path, img_folder)
            image_files = os.listdir(images_path)
            for image in image_files:
                image_path = os.path.join(images_path, image)
                print(image_path)
                currHammingDist = self.hammingDistance(searchBarcode, self.generateBarcode(image_path))
                if currHammingDist < hammingDist:
                    hammingDist = currHammingDist
                    closestMatch = image_path
        print(closestMatch)
        self.imgPreview.setPixmap(QPixmap(closestMatch))
        self.image_path.setText(closestMatch)


    def hammingDistance(self, searchBarcode, currentBarcode):
        hammingDist = 0
        print(searchBarcode)
        print(currentBarcode)
        for i in range(len(searchBarcode)):
            if searchBarcode[i] != currentBarcode[i]:
                hammingDist+=1
        return hammingDist



    def generateBarcode(self, filePath):
        barcode = []
        print(filePath)
        # Proccess image into numpy array
        image = Image.open(filePath)
        imgArr = np.asarray(image.convert('L'))
        flippedImgArr = np.fliplr(imgArr)

        diagTopLeftToBtmRight = []
        diagTopRightToBtmLeft = []

        rowSums = []
        columnSums = []

        for i in range(-26, 27):
            diagTopLeftToBtmRight.append(sum(np.diagonal(imgArr, i, 0, 1)))
            diagTopRightToBtmLeft.append(sum(np.diagonal(flippedImgArr, i, 0, 1)))

        for i in range(27):
            rowSums.append(sum(imgArr[i, :]))
            columnSums.append(sum(imgArr[:, i]))

        barcode = self.convertSumsToBarcode(rowSums) + \
                  self.convertSumsToBarcode(columnSums) + \
                  self.convertSumsToBarcode(diagTopLeftToBtmRight) + \
                  self.convertSumsToBarcode(diagTopRightToBtmLeft)
        return barcode


    def arrAverage(self, arr):
        a = np.asarray(arr)
        return round(a.mean())

    def convertSumsToBarcode(self, arr):
        c = []
        avg = self.arrAverage(arr)
        for item in arr:
            if item > avg:
                c.append(1)
            else:
                c.append(0)
        return c

app = QApplication(sys.argv)
mainWindow = MainMenu()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.show()
widget.setFixedWidth(500)
widget.setFixedHeight(500)

app.exec_()