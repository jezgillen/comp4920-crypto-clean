#!/usr/bin/python3
from statistics.algorithmAnalysis import *
from PyQt5.QtWidgets import QApplication, QTableWidget, QLabel, QWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QPushButton, QDialog, QTabWidget, QSizePolicy, QHeaderView
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, Qt
from bots import Action
from datetime import datetime

class StatisticsView(QWidget):
    def __init__(self, parent):

        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        #  self.tabs.resize(100,100)
        self.tabs.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

        self._styleDescription()

        scroll = QScrollArea(self)
        scroll.setWidget(self.tabDescription)
        scroll.setWidgetResizable(True)

        self.tabs.addTab(scroll, "Description")
        self.tabs.addTab(self.tab1, "Bot Performance Statistics")
        self.tabs.addTab(self.tab2, "30-day Breakdown")
        self.tabs.addTab(self.tab3, "Trading History")

        self.tab1.layout = QHBoxLayout()
        self.tab2.layout = QHBoxLayout()
        self.tab3.layout = QHBoxLayout()

        self.buildTableGeneral()
        self.buildTableMonthly()
        self.buildTableHistory()

        #putting table into tab
        self.tab3.layout.addWidget(self.tableHistory)
        self.tab3.setLayout(self.tab3.layout)
        self.tab1.layout.addWidget(self.tableGeneral)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.layout.addWidget(self.tableMonthly)
        self.tab2.setLayout(self.tab2.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


    def buildTableHistory(self):
        self.tableHistory = QTableWidget(1, 5)
        self.tableHistory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.tableHistory.setHorizontalHeaderItem(0, QTableWidgetItem("Date"))
        self.tableHistory.setHorizontalHeaderItem(1, QTableWidgetItem("Unit Price (USD)"))
        self.tableHistory.setHorizontalHeaderItem(2, QTableWidgetItem("Coins Traded"))
        self.tableHistory.setHorizontalHeaderItem(3, QTableWidgetItem("Portfolio Value"))
        self.tableHistory.setHorizontalHeaderItem(4, QTableWidgetItem("Action"))

    def setTabDescription(self):
        self.tabs.setCurrentIndex(0)

    def setTabGeneral(self):
        self.tabs.setCurrentIndex(1)

    def getDefaultDescription(self):
        return "Describes what the selected bot does"

    def _styleDescription(self):
        self.tabDescription = QLabel(self.getDefaultDescription(), self)
        self.tabDescription.move(150,150)
        self.tabDescription.setAlignment(Qt.AlignTop)
        self.tabDescription.setTextFormat(1)
        self.tabDescription.setOpenExternalLinks(True)
        font = QFont()
        font.setWeight(25)
        font.setPointSize(13)
        self.tabDescription.setFont(font)
        self.tabDescription.setWordWrap(True)
        self.tabDescription.setText('Describes what the bot does')

    def setDescription(self, description):
        description = description.replace('\n','<br>')
        self.tabDescription.setText(description)

    def buildTableGeneral(self):
        self.tableGeneral = QTableWidget(7, 1,None)
        self.tableGeneral.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableGeneral.verticalHeader().setDefaultAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.tableGeneral.horizontalHeader().setStretchLastSection(True)

        self.tableGeneral.horizontalHeader().hide()


        #row titles
        finalValue = QTableWidgetItem("Final Value (USD):")
        self.finalValueToolTip = 'Final value of portfolio in USD including cash and coins'
        finalValue.setToolTip(self.finalValueToolTip)
        self.tableGeneral.setVerticalHeaderItem(0, finalValue)


        finalCash = QTableWidgetItem("Final Cash Amount (USD):")
        self.finalCashToolTip = 'Final value of cash portion'
        finalValue.setToolTip(self.finalCashToolTip)
        self.tableGeneral.setVerticalHeaderItem(1, finalCash)


        finalCoins = QTableWidgetItem("Final Coin amount:")
        self.finalCoinsToolTip = 'Final coins held'
        finalValue.setToolTip(self.finalCoinsToolTip)
        self.tableGeneral.setVerticalHeaderItem(2, finalCoins)

        numTrades = QTableWidgetItem("Number of Trades:")
        self.numTradesToolTip = "Overall number of trades the bot did, within the specified time period"
        numTrades.setToolTip(self.numTradesToolTip)
        self.tableGeneral.setVerticalHeaderItem(3, numTrades)

        gainDollars = QTableWidgetItem("Gain($):")
        self.gainDollarsToolTip = 'Total gain in USD'
        gainDollars.setToolTip(self.gainDollarsToolTip)
        self.tableGeneral.setVerticalHeaderItem(4, gainDollars)

        gainPct = QTableWidgetItem("Gain(%):")
        self.gainPctToolTip = 'Total gain in %'
        gainPct.setToolTip(self.gainPctToolTip)
        self.tableGeneral.setVerticalHeaderItem(5, gainPct)

        payback = QTableWidgetItem("Payback Period (days):")
        self.paybackToolTip = 'Number of days to earn back initial capital'
        payback.setToolTip(self.paybackToolTip)
        self.tableGeneral.setVerticalHeaderItem(6, payback)


    def buildTableMonthly(self):
        #building tab 2
        numMonths = 0
        self.tableMonthly = QTableWidget(6,numMonths, None)
        self.tableMonthly.verticalHeader().setStretchLastSection(False)
        self.tableMonthly.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableMonthly.verticalHeader().setDefaultAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.tableMonthly.horizontalHeader().hide()
        self.tableMonthly.horizontalHeader().setStretchLastSection(True)


        #row titles
        dateEnding = QTableWidgetItem("Date Ending:")
        dateEnding.setToolTip('Data at each column is for the month ending at this date')
        self.tableMonthly.setVerticalHeaderItem(0, dateEnding)

        value = QTableWidgetItem("Value ($):")
        value.setToolTip('Value of the portfolio in USD at date ending. Includes casha nd coins')
        self.tableMonthly.setVerticalHeaderItem(1, value)

        gainDollars = QTableWidgetItem("Gain ($):")
        gainDollars.setToolTip('Monthly gain in USD')
        self.tableMonthly.setVerticalHeaderItem(2, gainDollars)

        gainPct = QTableWidgetItem("Gain (%):")
        gainPct.setToolTip('Monthly gain in percentage')
        self.tableMonthly.setVerticalHeaderItem(3, gainPct)

        numBuys = QTableWidgetItem("#Buys:")
        numBuys.setToolTip('Number of buy actions in this month')
        self.tableMonthly.setVerticalHeaderItem(4, numBuys)

        numSells = QTableWidgetItem("#Sells:")
        numSells.setToolTip('Number of sell actions in this month')
        self.tableMonthly.setVerticalHeaderItem(5, numSells)


    def showHistory(self, backtestHistory):
        row = 0
        prevCoinsHeld = 0
        self.tableHistory.setRowCount(0)
        for d in backtestHistory:
            if d.getAction() is not Action.NOACTION:
                self.tableHistory.insertRow(row)
                date = datetime.strftime(d.getDateStamp(), '%d/%m/%Y')
                coinsTraded = "{0:,.3f}".format(d.getCoinAmount() - prevCoinsHeld)

                self.tableHistory.setItem(row, 0, QTableWidgetItem(date))
                self.tableHistory.setItem(row, 1, QTableWidgetItem(str("{0:,.3f}".format(d.getMarketPrice()))))
                self.tableHistory.setItem(row, 2, QTableWidgetItem(str(coinsTraded)))
                self.tableHistory.setItem(row, 3, QTableWidgetItem(str("{0:,.3f}".format(d.getPortfolioValue()))))
                self.tableHistory.setItem(row, 4, QTableWidgetItem(d.getAction().name))
                row += 1
            prevCoinsHeld = d.getCoinAmount()

    def updateMonthlyColCount(self, newCount):
        colPosition = self.tableMonthly.columnCount()
        if (newCount > colPosition - 1):
            self.tableMonthly.setColumnCount(newCount+1)


    def updateMonthlyDate(self, colNum, data):
        self.updateMonthlyColCount(colNum)
        self.tableMonthly.setItem(0, colNum, QTableWidgetItem(data))

    def updateMonthlyValue(self, colNum, data):
        self.updateMonthlyColCount(colNum)
        self.tableMonthly.setItem(1, colNum, QTableWidgetItem(data))

    def updateMonthlyGainDollars(self, colNum, data):
        self.updateMonthlyColCount(colNum)
        widget = QTableWidgetItem(data)
        if float(data.replace(',', '')) > 0:
            widget.setForeground(QBrush(QColor(0,255,0)))
        else:
            widget.setForeground(QBrush(QColor(255,0,0)))
        self.tableMonthly.setItem(2, colNum, widget)

    def updateMonthlyGainPct(self, colNum, data):
        self.updateMonthlyColCount(colNum)
        widget = QTableWidgetItem(data)
        if float(data.replace(',', '')) > 0:
            widget.setForeground(QBrush(QColor(0,255,0)))
        else:
            widget.setForeground(QBrush(QColor(255,0,0)))
        self.tableMonthly.setItem(3, colNum, widget)

    def updateMonthlyBuys(self, colNum, data):
        self.updateMonthlyColCount(colNum)
        widget = QTableWidgetItem(data)
        self.tableMonthly.setItem(4, colNum, widget)

    def updateMonthlySells(self, colNum, data):
        self.updateMonthlyColCount(colNum)
        widget = QTableWidgetItem(data)
        self.tableMonthly.setItem(5, colNum, widget)



    def updatePaybackPeriod(self, value):
        '''takes a string. Updates relevant portion in table'''
        if float(value) < 0:
            value ='Payback not earned.'
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.paybackToolTip)
        self.tableGeneral.setItem(6, 0, widget)

    def updateOverallGainDollars(self, value):
        '''takes a string. Updates relevant portion in table'''
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.gainDollarsToolTip)

        if float(value.replace(',', '')) > 0:
            widget.setForeground(QBrush(QColor(0,255,0)))
        else:
            widget.setForeground(QBrush(QColor(255,0,0)))
        self.tableGeneral.setItem(4, 0, widget)


    def updateOverallGainPercent(self, value):
        '''takes a string. Updates relevant portion in table'''
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.gainPctToolTip)
        if float(value.replace(',', '')) > 0:
            widget.setForeground(QBrush(QColor(0,255,0)))
        else:
            widget.setForeground(QBrush(QColor(255,0,0)))
        self.tableGeneral.setItem(5, 0, widget)


    def updateCoinAmount(self, value):
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.finalCoinsToolTip)
        self.tableGeneral.setItem(2, 0, widget)

    def updateCashAmount(self, value):
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.finalCashToolTip)
        self.tableGeneral.setItem(1, 0, widget)


    def updateOverallTrades(self, value):
        '''takes a string. Updates relevant portion in table'''
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.numTradesToolTip)
        self.tableGeneral.setItem(3, 0, widget)

    def updateFinalValue(self, value):
        '''takes a string. Updates relevant portion in table'''
        widget = QTableWidgetItem(value)
        widget.setToolTip(self.finalValueToolTip)
        self.tableGeneral.setItem(0,0,widget)


    def resetTables(self):
        self.tableMonthly.setColumnCount(0)

    def showStats(self, backtestData):
        self.resetTables()
        analyser = Analyser(backtestData)
        monthlyPeriod = Period.MONTHLY

        #monthly stats
        gainData = analyser.getGain(monthlyPeriod, False)

        dates = [x[0] for x in gainData]
        gainData = ["{0:,.3f}".format(x[1]) for x in gainData]
        self.showMonthlyDates(dates)
        self.showMonthylGainDollars(gainData)

        valueData = analyser.getValue(monthlyPeriod)
        valueData = ["{0:,.3f}".format(x[1]) for x in valueData]
        self.showMonthlyValue(valueData)

        gainData = analyser.getGain(monthlyPeriod, True)
        gainData = ["{0:,.3f}".format(x[1]) for x in gainData]
        self.showMonthylGainPct(gainData)

        numBuys = analyser.getNumTrades(monthlyPeriod, Action.BUY)
        self.showMonthlyBuys([x[1] for x in numBuys])

        numSells = analyser.getNumTrades(monthlyPeriod, Action.SELL)
        self.showMonthlySells(x[1] for x in numSells)


        #general stats

        finalGainDollars = "{0:,.3f}".format(analyser.getGain(Period.TOTAL, False))
        finalGainPct = "{0:,.3f}".format(analyser.getGain(Period.TOTAL, True))
        finalValue = "{0:,.3f}".format(analyser.getFinalValue())
        finalCash = "{0:,.3f}".format(backtestData.getFinalCashAmount())
        finalCoins = "{0:,.3f}".format(backtestData.getFinalCointAmount())
        finalPrice = "{0:,.3f}".format(backtestData.getFinalMarketPrice())
        self.updateFinalValue(finalValue)
        payback = analyser.getPayBackPeriod()
        totalTrades = analyser.getSumTrades(Period.TOTAL)

        self.updateCashAmount(str(finalCash))
        self.updateCoinAmount(str(finalCoins) + ' @ $' + str(finalPrice) + 'ea.')
        self.updatePaybackPeriod(str(payback))
        self.updateOverallGainDollars(finalGainDollars)
        self.updateOverallGainPercent(finalGainPct)
        self.updateOverallTrades(str(totalTrades))


    def showMonthlyDates(self, data):
        idx = 0
        for d in data:
           self.updateMonthlyDate(idx, datetime.strftime(d, '%d/%m/%Y'))
           idx += 1

    def showMonthylGainDollars(self, gainData):
        idx = 0
        for g in gainData:
            self.updateMonthlyGainDollars(idx, g)
            idx += 1

    def showMonthylGainPct(self, gainData):
        idx = 0
        for g in gainData:
            self.updateMonthlyGainPct(idx,  g)
            idx += 1


    def showMonthlyValue(self, valueData):
        idx = 0
        for v in valueData:
            self.updateMonthlyValue(idx, v)
            idx += 1

    def showMonthlyBuys(self, data):
        idx = 0
        for d in data:
            self.updateMonthlyBuys(idx,  str(d))
            idx += 1

    def showMonthlySells(self, data):
        idx = 0
        for d in data:
            self.updateMonthlySells(idx,  str(d))
            idx += 1

