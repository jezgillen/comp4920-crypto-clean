#!/usr/bin/python3
import sys
import qdarkstyle
from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QGroupBox, QVBoxLayout, QWidget, QPushButton, QGridLayout, QLabel, QComboBox, QScrollArea, QInputDialog, QCheckBox, QMessageBox,QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDir, QUrl
from PyQt5 import QtGui

from tkinter import messagebox

import plotly
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd

import bots
import fetchData
import exceptions

from parameterView import formView
from statistics.statisticsView import StatisticsView
from statistics.algorithmAnalysis import Analyser, Period
from botManager.botManager import BotManager
from botManager.botManagerView import BotManagerView
from graph.graphView import GraphView


# Class for running simulations of bots on data, which then uses the graph to plot the data

class simulator():
    def __init__(self, graph, formView, statsView, historicalData, parentWindow, dropdown=None):
        self.formView = formView
        self.graph = graph
        self.statsView = statsView
        self.dropdown = dropdown
        self.data = historicalData
        self.parentWindow = parentWindow

    def setHistoricalData(self, data):
        self.data = data

    def run(self):
        self.parentWindow.removeMessage()

        if not self._setup():
            return

        try:
            buySellData = self.bot.processHistoricalData(self.data)
            self.graph.clearFig()
            self.graph.addBuySellLines(buySellData)
            self.statsView.showStats(buySellData)
            self.graph.addPortfolioValue(buySellData)

            self.statsView.setTabGeneral()
            self.statsView.showHistory(buySellData)
        except IndexError as IE:
            self.parentWindow.displayMessage('Invalid Dates - Please select an appropriate date range', 'red')


    def _setup(self):
        self.setupBot(self.bot)
        try:
            self.bot.checkParameters()
            return True
        except exceptions.InvalidStartEndDates as NE:
            self.parentWindow.displayMessage('Invalid Input - Please give appropriate start and end dates', 'red')
        except exceptions.InvalidMovingAvgs as II:
            self.parentWindow.displayMessage('Invalid Input - Please give appropriate moving day averages', 'red')
        except exceptions.InvalidDays as ID:
            self.parentWindow.displayMessage('Invalid input - Please give a positive number of consecutive days', 'red')
        except exceptions.InvalidIntervals as IV:
            self.parentWindow.displayMessage('Invalid input - Please give appropriate interval values', 'red')
        except exceptions.InvalidThresholds as IT:
            self.parentWindow.displayMessage('Invalid Input - Please give appropriate threshold values', 'red')
        return False

    def setupBot(self, bot):
        paramNames = bot.getParameterNames()
        for p in paramNames:
            value = self.formView.getWidgetValue(p)
            bot.changeParam(p, value)

    def getBot(self):
        return self.bot

    def setBot(self, bot):
        self.bot = bot


# UI of application,, QWidget passed through as blank canvas
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.grid_layout = QGridLayout()
        self.setWindowTitle('Coinye')

        # wrapper groupbox to add all components to, and create scroll area
        wrapper = QGroupBox()
        wrapper.setLayout(self.grid_layout)

        scroll = QScrollArea(self)
        scroll.setWidget(wrapper)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header area i.e. title + description
        title = QLabel()
        title.setTextFormat(QtCore.Qt.RichText)
        title.setAlignment(QtCore.Qt.AlignLeft)
        title.resize(title.sizeHint())
        title.setWordWrap(True)
        title.setText('''
            <div style="font-size: 20px; font-weight: bold; align-items: center;">Coinye</div>
            <div style="font-size: 14px; text-align: justify; margin-top: 10px; margin-bottom:10px;">
                Coinye is a cryptocurrency backtesting tool.
            </div>
            <hr>
        ''')
        self.grid_layout.addWidget(title, 0, 0, 1, 2)

        # Plotly graph
        firstCoin = 'ETH'
        self.exchange = "Gemini"
        historicalData = fetchData.getData(self.exchange, "day", firstCoin)
        self.graph = GraphView(self, historicalData, firstCoin)
        self.graph.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
        self.grid_layout.addWidget(self.graph, 0, 2, 3, 4)
        self.graph.setMinimumWidth(400)

        # Error message section
        self.error_msg = QLabel()
        self.error_msg.setWordWrap(True)
        self.error_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.error_msg.setMaximumHeight(50)
        self.error_msg.setMinimumHeight(20)
        self.error_msg.hide()
        self.grid_layout.addWidget(self.error_msg, 1, 0, 1, 2)

        self.form = formView.FormView(self)
        self.grid_layout.addWidget(self.form, 2, 0, 1, 2)
        self.grid_layout.setRowStretch(2, 2)

        self.form.setMinimumWidth(310)
        _maxWidth = 480
        self.form.setMaximumWidth(_maxWidth)
        self.grid_layout.setColumnStretch(1, 2)


        # Reset button
        self.grid_layout.setRowStretch(3, 1)
        self.resetButton = QPushButton('Reset Parameters')
        self.resetButton.clicked.connect(self.resetPressed)
        self.resetButton.setEnabled(False)
        self.grid_layout.addWidget(self.resetButton, 3, 1, 1, 1)
        self.resetButton.setMaximumWidth(_maxWidth-170)

        # Run button
        self.grid_layout.setRowStretch(4, 1)
        self.runButton = QPushButton('Run Simulation')
        self.runButton.clicked.connect(self.buttonPressed)
        self.runButton.setEnabled(False)
        self.grid_layout.addWidget(self.runButton, 4, 1, 1, 1)
        self.runButton.setMaximumWidth(_maxWidth-170)

        #Load Button
        self.loadButton = QPushButton('Import Bot')
        self.loadButton.setEnabled(True)
        self.loadButton.clicked.connect(self.loadPressed)
        self.grid_layout.addWidget(self.loadButton, 3, 0, 1, 1)

        #Save Button
        self.saveButton = QPushButton('Save Bot')
        self.saveButton.setEnabled(False)
        self.saveButton.clicked.connect(self.savePressed)
        self.grid_layout.addWidget(self.saveButton, 4, 0, 1, 1)

        # Initialise a list of bots, one for each type
        self.listOfBots = [b() for b in bots.Bot.__subclasses__()]

        # Dropdown
        self.dropdown = QComboBox()
        self.dropdown.addItem("--Select a Bot--")
        self.setStyleSheet('''
            QComboBox::item:checked {
                font-weight: bold;
                height: 16px;
            }
        ''')
        for bot in self.listOfBots:
            self.dropdown.addItem(bot.getName())
        self.dropdown.currentIndexChanged.connect(self.selectionchange)

        # Get list of coins
        self.coinList = ["BTC", "ETH", "LTC", "ZEC"]

        # Dropdown
        self.coinDropdown = QComboBox()
        self.coinDropdown.addItem("--Select a Coin--")

        for coin in self.coinList:
            self.coinDropdown.addItem(coin)
        self.coinDropdown.currentIndexChanged.connect(self.loadHistoricalData)

        # log check box
        self.logCheckBox = QCheckBox()
        self.logCheckBox.setText("Logarithmic Y-axis")
        self.logCheckBox.toggled.connect(self.graph.setLog)

        # manage layout of dropdowns
        self.dropdown.setMaximumWidth(200)
        self.coinDropdown.setMaximumWidth(200)
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(2)
        horizontal_layout.addWidget(self.dropdown)
        horizontal_layout.addWidget(self.coinDropdown)
        horizontal_layout.addWidget(self.logCheckBox)
        horizontal_layout.addStretch(2)
        self.grid_layout.addLayout(horizontal_layout, 4, 3, 1, 1)
        self.grid_layout.setColumnStretch(2, 0)
        self.grid_layout.setColumnStretch(3, 4)
        self.grid_layout.setColumnStretch(4, 0)

        #bot manager
        self.botManager = BotManager(self)
        botlist = self.botManager.getBotNames()

        self.botManagerView = BotManagerView(self, botlist)
        self.botManagerView.setMaximumWidth(_maxWidth)
        self.grid_layout.addWidget(self.botManagerView, 5, 0, 1, 2)

        # Stats Table
        #  self.grid_layout.setRowStretch(4, 3)
        self.statsView = StatisticsView(self)
        self.grid_layout.addWidget(self.statsView, 5, 2, 1, 4)

        # Link view with bot
        self.sim = simulator(self.graph, self.form, self.statsView, historicalData, self)

        # data source label
        self.data_source = QLabel()
        self.data_source.setAlignment(QtCore.Qt.AlignRight)
        self.grid_layout.addWidget(self.data_source, 6, 0, 1, 4)
        self.data_source.setTextFormat(1)
        self.data_source.setOpenExternalLinks(True)
        font = QtGui.QFont()
        font.setWeight(2)
        font.setPointSize(8)
        self.data_source.setFont(font)
        self.data_source.setText(f"Data Source: <a href='https://www.cryptodatadownload.com'>cryptodatadownload.com</a>  &nbsp;&nbsp;&nbsp;    Exchange: {self.exchange}")

        #set dropdown to the first coin selected by default
        idx = self.coinDropdown.findText(firstCoin)
        if idx >= 0:
            self.coinDropdown.setCurrentIndex(idx)


    def displayMessage(self, msg, colour='black'):
        self.error_msg.setText(msg)
        self.error_msg.setStyleSheet('color: ' + colour)
        self.error_msg.show()

    def removeMessage(self):
        self.error_msg.setText('')
        self.error_msg.setStyleSheet('color: black')
        self.error_msg.hide()

    def loadHistoricalData(self, coin):
        if(coin == 0):
            pass
        else:
            historicalData = fetchData.getData(self.exchange, "day", self.coinList[coin-1])
            self.graph.addHistoricalData(historicalData, self.coinList[coin-1])
            self.sim.setHistoricalData(historicalData)

    # Adding dropdown selection change function
    def selectionchange(self,i):
        if(i == 0):
            self.runButton.setEnabled(False)
            self.saveButton.setEnabled(False)
            self.statsView.setDescription(self.statsView.getDefaultDescription())
        else:
            bot = self.listOfBots[i-1]
            self.loadBot(bot)
            self.resetButton.setEnabled(True)


    def loadBot(self, bot):
        if bot is not None:
            self.sim.setBot(bot)
            self.graph.clearGraph()
            self.runButton.setEnabled(True)
            self.saveButton.setEnabled(True)
            bot.load()
            self._loadFormView(bot)


    def _loadFormView(self, bot):
        params = bot.getParameters()
        paramType = bot.getParameterTypes()
        paramHelpString = bot.getParameterHelpStrings()
        self.form.clear()
        for p in params:
            self.form.addParameter(p, paramType[p],  paramHelpString[p],params[p])
        self.form.createForm()
        self.statsView.setDescription(bot.getDescription())
        self.statsView.setTabDescription()



    def loadSavedBot(self, alias):
        bot = self.botManager.loadBot(alias)
        if bot is not None:
            self.loadBot(bot)
            self.statsView.setDescription(bot.getDescription())
            self.statsView.setTabDescription()
            self.resetButton.setEnabled(True)

    def setupBot(self, bot):
        self.sim.setupBot(bot)

    def deleteBot(self, alias):
        self.botManager.deleteBot(alias)

    def buttonPressed(self):
        if self.sim is not None:
            self.sim.run()

    def savePressed(self):
        placeholder = self.botManagerView.getSelected()
        text, ok = QInputDialog.getText(self, 'Name your bot', 'Enter a name:', text=placeholder)
        if ok:
            bot = self.sim.getBot()
            self.botManager.saveBot(text, bot)
            self.botManagerView.addBot(text)

    def loadPressed(self):
        loadedBotAlias = self.botManager.loadBotFromFile()
        if loadedBotAlias is not None:
            self.botManagerView.addBot(loadedBotAlias)
            self.botManagerView.refresh()
            self.botManagerView.setSelection(loadedBotAlias)
            self.botManagerView.loadBot()

    def resetPressed(self):
        result = QMessageBox.question(self, "Reset Bot", "Are you sure you want to reset this bot to default parameters?", QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            if self.sim is not None:
                bot = self.sim.getBot()
                if bot is not None:
                    bot.resetBotToDefault()
                    self._loadFormView(bot)




    def getSimulator(self):
        return self.sim

if __name__ == '__main__':
    sys.argv.append("--disable-web-security")

    #  If you face the error <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]
    #  Then uncomment the following 2 lines to fix it
    #  import ssl
    #  ssl._create_default_https_context = ssl._create_unverified_context

    app = QApplication(sys.argv)
    window = MainWindow()
    # set stylesheet
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)
    window.showMaximized()
    sys.exit(app.exec_())
