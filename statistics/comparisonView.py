#!/usr/bin/python3
from statistics.algorithmAnalysis import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QTableWidget, QWidget, QTableWidgetItem, QGridLayout, QTabWidget, QHeaderView
from parameterView.formView import InputType

class ComparisonView(QWidget):
    def __init__(self, parent, bot1, bot2):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.parent = parent
        self.bot1 = bot1
        self.bot2 = bot2

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(100,100)

        self.tabs.addTab(self.tab1, "Results")
        self.tabs.addTab(self.tab2, "Input Parameters")

        self.tab1.layout = QHBoxLayout()
        self.tab2.layout = QHBoxLayout()

        self.buildResultTable()
        self.buildParameterTable()

        self.tab1.layout.addWidget(self.comparisonTable)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.layout.addWidget(self.paramsTable)
        self.tab2.setLayout(self.tab2.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def buildParameterTable(self):
        self.paramsTable = QTableWidget(0,2)
        self.paramsTable.horizontalHeader().hide()
        self.paramsTable.horizontalHeader().setStretchLastSection(True)

        self.paramsTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.paramsTable.verticalHeader().setDefaultAlignment(Qt.AlignVCenter|Qt.AlignRight)

        self.paramsTable.setColumnWidth(0,180)
        self.paramsTable.setRowCount(0)

        # Collect a list of the parameters from both bots
        bot1params = self.bot1.getParameters()
        bot2params = self.bot2.getParameters()
        paramsList = []
        for p in bot1params.keys():
            paramsList.append(p)
        for p in bot2params.keys():
            if p not in paramsList:
                paramsList.append(p)

        # Add each parameter to the tables left-most column
        row = 0
        for p in paramsList:
            self.paramsTable.insertRow(row)
            widget = QTableWidgetItem(p)
            #  widget.setTextAlignment(QtCore.Qt.AlignRight)
            self.paramsTable.setVerticalHeaderItem(row, widget)
            row += 1

        bot1paramTypes = self.bot1.getParameterTypes()
        bot2paramTypes = self.bot2.getParameterTypes()
        for i in range(row):
            p = self.paramsTable.verticalHeaderItem(i).text()
            if p in bot1params:
                item = self._makeTableWidget(bot1params[p], bot1paramTypes[p])
                self.paramsTable.setItem(i, 0, item)
            if p in bot2params:
                item = self._makeTableWidget(bot2params[p], bot2paramTypes[p])
                self.paramsTable.setItem(i, 1, item)

    def _makeTableWidget(self, value, paramType):
        if (paramType == InputType.date):
            return QTableWidgetItem(str(value.strftime('%Y-%m-%d')))
        elif (paramType == InputType.float):
            return QTableWidgetItem(str(round(value, 2)))
        elif (paramType == InputType.int):
            return QTableWidgetItem(str(value))
        elif (paramType == InputType.string):
            return QTableWidgetItem(str(value))
        elif (paramType == InputType.currency):
            return QTableWidgetItem('$' + str(round(value, 2)))
        elif (paramType == InputType.percentage):
            return QTableWidgetItem(str(value) + '%')

    def buildResultTable(self):
        self.comparisonTable = QTableWidget(7, 3, None)
        #  self.comparisonTable.verticalHeader().setStretchLastSection(True)
        self.comparisonTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.comparisonTable.verticalHeader().setDefaultAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.comparisonTable.horizontalHeader().setStretchLastSection(True)

        # Column titles
        self.comparisonTable.setHorizontalHeaderItem(0, QTableWidgetItem(self.parent.bot_1))
        self.comparisonTable.setHorizontalHeaderItem(1, QTableWidgetItem(self.parent.bot_2))
        self.comparisonTable.setHorizontalHeaderItem(2, QTableWidgetItem("Difference"))

        # Row titles
        finalValue = QTableWidgetItem("Final Value:")
        finalValue.setToolTip('Final value of portfolio in USD including cash and coins')
        self.comparisonTable.setVerticalHeaderItem(0, finalValue)

        finalCash = QTableWidgetItem("Final Cash Amount (USD):")
        self.finalCashToolTip = 'Final value of cash portion'
        finalValue.setToolTip(self.finalCashToolTip)
        self.comparisonTable.setVerticalHeaderItem(1, finalCash)


        finalCoins = QTableWidgetItem("Final Coin amount:")
        self.finalCoinsToolTip = 'Final coins held'
        finalValue.setToolTip(self.finalCoinsToolTip)
        self.comparisonTable.setVerticalHeaderItem(2, finalCoins)


        self.comparisonTable.setVerticalHeaderItem(3, QTableWidgetItem("Num# Trades:"))

        gainDollars = QTableWidgetItem("Gain($):")
        gainDollars.setToolTip('Total gain in USD')
        self.comparisonTable.setVerticalHeaderItem(4, gainDollars)

        gainPct = QTableWidgetItem("Gain(%):")
        gainPct.setToolTip('Total gain in %')
        self.comparisonTable.setVerticalHeaderItem(5, gainPct)

        payback = QTableWidgetItem("Payback Period (days):")
        payback.setToolTip('Number of days to earn back initial capital')
        self.comparisonTable.setVerticalHeaderItem(6, payback)

    def insertFinalValue(self, value, col):
        self.comparisonTable.setItem(0, col, QTableWidgetItem(value))

    def insertCashAmount(self, value, col):
        widget = QTableWidgetItem(value)
        self.comparisonTable.setItem(1, col, widget)

    def insertCoinAmount(self, value, col):
        widget = QTableWidgetItem(value)
        self.comparisonTable.setItem(2, col, widget)

    def insertOverallTrades(self, value, col):
        self.comparisonTable.setItem(3, col, QTableWidgetItem(value))

    def insertOverallGainDollars(self, value, col):

        widget = QTableWidgetItem(value)
        if float(value) > 0:
            widget.setForeground(QBrush(QColor(0,255,0)))
        else:
            widget.setForeground(QBrush(QColor(255,0,0)))
        self.comparisonTable.setItem(4, col, widget)

    def insertOverallGainPercent(self, value, col):
        widget = QTableWidgetItem(value)
        if float(value) > 0:
            widget.setForeground(QBrush(QColor(0,255,0)))
        else:
            widget.setForeground(QBrush(QColor(255,0,0)))
        self.comparisonTable.setItem(5, col, widget)

    def insertPaybackPeriod(self, value, col):
        if float(value) < 0:
            value = 'Payback not earned.'
        self.comparisonTable.setItem(6, col, QTableWidgetItem(value))

    def showStats(self, backtestData_1, backtestData_2):
        analyser_1 = Analyser(backtestData_1)
        analyser_2 = Analyser(backtestData_2)

        col = 0
        for b in (backtestData_1, backtestData_2):
            finalCash = str(round(b.getFinalCashAmount(), 3))
            finalCoins = str(round(b.getFinalCointAmount(), 3))
            finalPrice = str(round(b.getFinalMarketPrice(),3))
            self.insertCashAmount(finalCash, col)
            self.insertCoinAmount(finalCoins, col)
            col += 1

        col = 0
        for analyser in (analyser_1, analyser_2):
            finalGainDollars = analyser.getGain(Period.TOTAL, False)
            finalGainPct = analyser.getGain(Period.TOTAL, True)
            payback = analyser.getPayBackPeriod()
            totalTrades = analyser.getSumTrades(Period.TOTAL)

            self.insertFinalValue(str(round(analyser.getFinalValue(),3)), col)
            self.insertOverallTrades(str(round(totalTrades,3)), col)
            self.insertOverallGainDollars(str(round(finalGainDollars,3)), col)
            self.insertOverallGainPercent(str(round(finalGainPct,3)), col)
            self.insertPaybackPeriod(str(round(payback,3)), col)
            col += 1

        # Final Value Difference
        finalValueDiff = round(abs(float(self.comparisonTable.item(0, 0).text()) - float(self.comparisonTable.item(0, 1).text())),2)
        bot1FinalVal = float(self.comparisonTable.item(0, 0).text())
        bot2FinalVal = float(self.comparisonTable.item(0, 1).text())
        if bot1FinalVal < bot2FinalVal:
            finalValStr = self.parent.bot_2 +" earned $" + str(finalValueDiff) +" more"
        elif bot1FinalVal > bot2FinalVal:
            finalValStr = self.parent.bot_1 +" earned $" + str(finalValueDiff) +" more"
        else: finalValStr = "No difference"


        #Cash Difference
        finalCash1 = backtestData_1.getFinalCashAmount()
        finalCash2 = backtestData_2.getFinalCashAmount()
        finalCashDiff = round(abs(finalCash1 - finalCash2),3)
        if finalCash1 < finalCash2:
            finalCashStr = self.parent.bot_2 +" has $" + str(finalCashDiff) +" more cash"
        elif finalCash1 > finalCash2:
            finalCashStr = self.parent.bot_1 +" has $" + str(finalCashDiff) +" more cash"
        else:
            finalCashStr = "No Difference"


        #Coin Difference
        finalCoin1 = backtestData_1.getFinalCointAmount()
        finalCoin2 = backtestData_2.getFinalCointAmount()

        finalCoinDiff = round(abs(finalCoin1 - finalCoin2),3)
        if finalCoin1 < finalCoin2:
            finalCoinStr = self.parent.bot_2 +" has " + str(finalCoinDiff) +" more coins"
        elif finalCoin1 > finalCoin2:
            finalCoinStr = self.parent.bot_1 +" has " + str(finalCoinDiff) +" more coins"
        else:
            finalCoinStr = "No Difference"


        # Trade Difference
        tradesDiff = round(abs(float(self.comparisonTable.item(3, 0).text()) - float(self.comparisonTable.item(3, 1).text())),2)
        bot1TradeVal = float(self.comparisonTable.item(3, 0).text())
        bot2TradeVal = float(self.comparisonTable.item(3, 1).text())
        if bot1TradeVal < bot2TradeVal:
            tradeValStr = self.parent.bot_2 +" had " + str(tradesDiff) +" more trades"
        elif bot1TradeVal > bot2TradeVal:
            tradeValStr= self.parent.bot_1 +" had " + str(tradesDiff) +" more trades"
        else: tradeValStr = "No difference"

        # Gain in Dollars Difference
        gainDollarsDiff = round(abs(float(self.comparisonTable.item(4, 0).text()) - float(self.comparisonTable.item(4, 1).text())),2)
        bot1GainDoll = float(self.comparisonTable.item(4, 0).text())
        bot2GainDoll = float(self.comparisonTable.item(4, 1).text())
        if bot1GainDoll < bot2GainDoll:
            gainValStr = self.parent.bot_2 +" earned $" + str(gainDollarsDiff) +" more gain"
        elif bot1GainDoll > bot2GainDoll:
            gainValStr= self.parent.bot_1 +" earned $" + str(gainDollarsDiff) +" more gain"
        else: gainValStr = "No difference"

        # Gain in Percentage Difference
        gainPercentDiff = round(abs(float(self.comparisonTable.item(5, 0).text()) - float(self.comparisonTable.item(5, 1).text())),2)
        bot1GainPerc = float(self.comparisonTable.item(5, 0).text())
        bot2GainPerc = float(self.comparisonTable.item(5, 1).text())
        if bot1GainPerc < bot2GainPerc:
            gainPValStr = self.parent.bot_2 +" earned " + str(gainPercentDiff) +"% more gain"
        elif bot1GainPerc > bot2GainPerc:
            gainPValStr= self.parent.bot_1 +" earned " + str(gainPercentDiff) +"% more gain"
        else: gainPValStr = "No difference"

        # Payback Period Difference
        bot1PayBackDiff = self.comparisonTable.item(6, 0).text()
        bot2PayBackDiff = self.comparisonTable.item(6, 1).text()
        if bot1PayBackDiff != 'Payback not earned.' and bot2PayBackDiff != 'Payback not earned.':
            difference = abs(float(bot1PayBackDiff) - float(bot2PayBackDiff))
            if float(bot1PayBackDiff) == float(bot2PayBackDiff):
                paybackPeriodDiff = "No difference."
            elif float(bot1PayBackDiff) < float(bot2PayBackDiff):
                paybackPeriodDiff = self.parent.bot_1 + " reached payback " +str(difference) +" days sooner"
            else:
                paybackPeriodDiff = self.parent.bot_2 + " reached payback " +str(difference) +" days sooner"
        elif bot1PayBackDiff != 'Payback not earned.' and bot2PayBackDiff == 'Payback not earned.':
            paybackPeriodDiff = self.parent.bot_1 + " reached payback " + bot1PayBackDiff + " days sooner"
        elif bot1PayBackDiff == 'Payback not earned.' and bot2PayBackDiff != 'Payback not earned.':
            paybackPeriodDiff = self.parent.bot_2 + " reached payback " + bot2PayBackDiff + " days sooner"
        else: paybackPeriodDiff = 'Not Applicable'



        self.comparisonTable.setItem(0, 2, QTableWidgetItem(finalValStr))
        self.comparisonTable.setItem(1, 2, QTableWidgetItem(finalCashStr))
        self.comparisonTable.setItem(2, 2, QTableWidgetItem(finalCoinStr))
        self.comparisonTable.setItem(3, 2, QTableWidgetItem(tradeValStr))
        self.comparisonTable.setItem(4, 2, QTableWidgetItem(str(gainValStr)))
        self.comparisonTable.setItem(5, 2, QTableWidgetItem(str(gainPValStr)))
        self.comparisonTable.setItem(6, 2, QTableWidgetItem(str(paybackPeriodDiff)))
