import sys
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QTableWidget, QLabel, QWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QPushButton, QDialog,  QListWidget, QListWidgetItem, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
from statistics.algorithmAnalysis import *
import importlib
from statistics.statisticsView import StatisticsView
from statistics.compareWindow import CompareWindow
import qdarkstyle
from botManager.botManager import BotManager
import fetchData
from comparisonInputView import ComparisonInputDialog
import exceptions


class BotManagerView(QWidget):
    def __init__(self, parent, botlist):
        super(QWidget, self).__init__(parent)
        self.innerLayout = QVBoxLayout()
        self.groupBox = QGroupBox('Saved Bots')
        self.layout = QVBoxLayout(self)
        self.botListView = QListWidget(self)
        self.botListView.setWindowTitle('Your saved bots')
        self.botListView.itemSelectionChanged.connect(self.loadBot)
        self.botListView.itemChanged.connect(self.getSelectedBots)
        self.removeButton = QPushButton('Remove')
        self.removeButton.setEnabled(False)
        self.compareButton = QPushButton('Select 2 Bots to Compare')
        self.compareButton.setEnabled(False)
        self.botManager = BotManager(self)
        self.parent = parent

        self.botList = {}
        self.compareList = dict()
        self._setup(botlist)

        self.error_msg = QLabel()
        self.error_msg.setWordWrap(True)
        self.error_msg.setAlignment(QtCore.Qt.AlignLeft)

        self.innerLayout.addWidget(self.botListView)
        self.innerLayout.addWidget(self.removeButton)
        self.innerLayout.addWidget(self.compareButton)
        self.innerLayout.addWidget(self.error_msg)
        self.groupBox.setLayout(self.innerLayout)
        self.layout.addWidget(self.groupBox)
        self.setLayout(self.layout)

        self.windows = []


    def _setup(self, botlist):
        for b in botlist:
            self.botList[b] = b
            item = QListWidgetItem(b)
            item.setCheckState(False)
            item.setText(b)
            self.botListView.addItem(item)

        self.removeButton.clicked.connect(self.removeButtonPressed)
        self.compareButton.clicked.connect(self.compareButtonPressed)

    def refresh(self):
        self.botListView.clear()
        self.compareList.clear()
        self.compareButton.setText('Select 2 Bots to Compare')
        self.compareButton.setEnabled(False)
        self.removeButton.setEnabled(False)
        for b in self.botList:
            item = QListWidgetItem(b)
            item.setCheckState(False)
            item.setText(b)
            self.botListView.addItem(item)

    def loadBot(self):
        if self.botListView.currentItem() is None:
            return
        alias = self.botListView.currentItem().text()
        self.parent.loadSavedBot(alias)

    def addBot(self, alias):
        self.botList[alias] = alias
        self.refresh()

    def getSelected(self):
        item = self.botListView.currentItem()
        if item is not None:
            return item.text()
        return ''

    def removeButtonPressed(self):
        count = len(self.compareList)
        result = QMessageBox.question(self, "Delete Bots", "Are you sure you want to delete " +str(count) + " bots?", QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            self._removeManyBots()


    def _removeSingleBot(self):
        item = self.botListView.currentItem()
        if item is not None:
            alias = item.text()
            self.parent.deleteBot(alias)
            self.botList.pop(alias)
            self.refresh()

    def _removeManyBots(self):
        for item in self.compareList:
            self.parent.deleteBot(item)
            self.botList.pop(item)
        self.refresh()

    def setSelection(self, name):
        item = self.botListView.findItems(name, Qt.MatchExactly)
        if len(item) > 0:
            self.botListView.setCurrentItem(item[0])

    def buttonPressed(self):
        result = QMessageBox.question(self, "Delete Bot", "Are you sure you want to delete this bot?", QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            self._removeSingleBot()


    def getSelectedBots(self, item):
        alias = item.text()
        if alias not in self.compareList:
            self.compareList[alias] = alias
        elif alias in self.compareList:
            del self.compareList[alias]
        if len(self.compareList) == 2:
            self.compareButton.setText('Compare Bots')
            self.compareButton.setEnabled(True)
        else:
            self.compareButton.setText('Select 2 Bots to Compare')
            self.compareButton.setEnabled(False)
        if len(self.compareList) > 0:
            self.removeButton.setEnabled(True)
        else:
            self.removeButton.setEnabled(False)

    def displayMessage(self, msg, colour='black'):
        self.error_msg.setText(msg)
        self.error_msg.setStyleSheet('color: ' + colour)

    def removeMessage(self):
        self.error_msg.setText('')
        self.error_msg.setStyleSheet('color: black')

    def compareButtonPressed(self):
        self.removeMessage()
        if len(self.compareList) != 2:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Invalid number of bots selected - Please select 2 bots")
            msgBox.setWindowTitle("Compare Bots")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
            return


        startDate, endDate, coin, ok = ComparisonInputDialog.getUserInput(self)

        if ok:
            bot1 = list(self.compareList.keys())[0]
            bot2 = list(self.compareList.keys())[1]
            self.botOneObject = self.botManager.loadBot(bot1)
            self.botTwoObject = self.botManager.loadBot(bot2)
            self.botOneObject.changeParam('Start Trading Date', startDate)
            self.botOneObject.changeParam('End Trading Date', endDate)
            self.botTwoObject.changeParam('Start Trading Date', startDate)
            self.botTwoObject.changeParam('End Trading Date', endDate)
            if not self.checkBot(self.botOneObject):
                return
            if not self.checkBot(self.botTwoObject):
                return
            try:
                self.data = fetchData.getData(exchange="Gemini", resolution="day", coin=coin)
                buySellDataOne = self.botOneObject.processHistoricalData(self.data)
                buySellDataTwo = self.botTwoObject.processHistoricalData(self.data)
                window = CompareWindow(self.data, bot1, bot2, buySellDataOne, buySellDataTwo, coin, self.botManager)
                self.windows.append(window)
                window.show()
            except IndexError as IE:
                    self.displayMessage('Please select an appropriate date range', 'red')
    def checkBot(self, bot):
        try:
            bot.checkParameters()
            return True
        except exceptions.InvalidStartEndDates as NE:
            self.displayMessage('Invalid Input - Please give appropriate start and end dates', 'red')
        except exceptions.InvalidMovingAvgs as II:
            self.displayMessage('Invalid Input - Please give appropriate moving day averages', 'red')
        except exceptions.InvalidDays as ID:
            self.displayMessage('Invalid input - Please give a positive number of consecutive days', 'red')
        except exceptions.InvalidIntervals as IV:
            self.displayMessage('Invalid input - Please give appropriate interval values', 'red')
        except exceptions.InvalidThresholds as IT:
            self.displayMessage('Invalid Input - Please give appropriate threshold values', 'red')
        return False


