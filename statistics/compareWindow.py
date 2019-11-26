#!/usr/bin/python3
import sys, os, importlib, json
from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from statistics.comparisonView import ComparisonView
import fetchData
from graph.graphView import GraphView
from parameterView.formView import InputType

class CompareWindow(QWidget):
    def __init__(self, historical, bot_1, bot_2, data1, data2, coin, botManager):
        super().__init__()
        self.resize(700, 750)
        self.setWindowTitle(coin + ': ' + bot_1 + ' vs ' + bot_2)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.bot_1 = bot_1
        self.bot_2 = bot_2
        self.botManager = botManager

        # Plotly graph
        self.graph = GraphView(self, historical, coin, True)
        self.graph.addBuySellLines(data1, bot_1, 1)
        self.graph.addBuySellLines(data2, bot_2, 2)
        self.graph.addPortfolioValue(data1, bot_1, 1)
        self.graph.addPortfolioValue(data2, bot_2, 2)
        self.graph.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
        self.layout.addWidget(self.graph)
        self.graph.setMinimumWidth(500)

        # log check box
        self.logCheckBox = QCheckBox()
        self.logCheckBox.setText("Logarithmic Y-axis")
        self.logCheckBox.toggled.connect(self.graph.setLog)
        self.layout.addWidget(self.logCheckBox)

        # Get the bot objects
        bot1 = self.botManager.loadBot(self.bot_1)
        bot2 = self.botManager.loadBot(self.bot_2)

        self.table = ComparisonView(self, bot1, bot2)
        self.table.showStats(data1, data2)
        self.layout.addWidget(self.table)
