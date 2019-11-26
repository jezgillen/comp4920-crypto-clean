from enum import Enum
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import math
from bots import Action

class Period(Enum):
    DAILY = 2
    WEEKLY = 3
    MONTHLY = 4
    YEARLY = 5
    TOTAL = 6


class Analyser():
    def __init__(self, bth):
        self.dailyDict = {}
        self.monthlyDict = {}
        self.backTestHistory = bth #BackTestHistory Object
        self.datalist = bth
        self.initialCapital = self.datalist.getEarliestDataPoint().getPortfolioValue()
        self.setupDict()


    def setupDict(self):
        #dailyDict returns how many days in a PERIOD that is smaller than a month
        self.dailyDict[Period.DAILY] = 1
        self.dailyDict[Period.WEEKLY] = 7
        self.dailyDict[Period.MONTHLY] = 0
        self.dailyDict[Period.YEARLY] = 0
        self.dailyDict[Period.TOTAL] = 0

        #monthly returns how many months in a PERIOD that is smaller than a year
        self.monthlyDict[Period.DAILY] = 0
        self.dailyDict[Period.WEEKLY] = 0
        self.monthlyDict[Period.MONTHLY] = 1
        self.monthlyDict[Period.YEARLY] = 0
        self.monthlyDict[Period.TOTAL] = 0

    def extractData(self):
        datalist = []

        cashHistory = self.backTestHistory.getCashBalanceHistory()
        coinAmountHistory = self.backTestHistory.getCoinAmountHistory()
        marketPriceHistory = self.backTestHistory.getMarketPriceHistory()
        actionHistory = self.backTestHistory.getActionHistory()

        if (len(cashHistory) != len(coinAmountHistory) and
            len(marketPriceHistory) != len(actionHistory) and
            len(marketPriceHistory) != len(coinAmountHistory)):
                print('Error')
        else:
            for i in range(0, len(cashHistory)):
                newTuple = [cashHistory[i][0], marketPriceHistory[i][1], coinAmountHistory[i][1], cashHistory[i][1], actionHistory[i][1]]
                datalist.append(newTuple)

        return datalist


    def getGain(self, period, isPercentage):
        """
            returns the gain or loss per period. If isPercentage is true, return percentage gain
            with respect to that period otherwise, return value in dollars
            period: enum Period.DAILY, WEEKLY, MONTHLY
            isPercentage: boolean
            retun list of tuples (datetime, gain)
        """
        if (period == Period.TOTAL):
            return self.getROI(isPercentage)
        retval = []


        initialDataPoint = self.datalist.getEarliestDataPoint()
        initialDate = initialDataPoint.getDateStamp()
        initialValue = initialDataPoint.getPortfolioValue()

        currentGain = 0
        for d in self.datalist:
            finalValue = d.getPortfolioValue()
            if d.getDateStamp() > (initialDate+relativedelta(months = self.monthlyDict[period], days=self.dailyDict[period])):
                currentGain = finalValue - initialValue
                if (isPercentage):
                    currentGain = currentGain / initialValue * 100
                value = [(initialDate+relativedelta(months = self.monthlyDict[period], days=self.dailyDict[period])), currentGain,3]
                retval.append(value)
                currentGain = 0
                initialDate = d.getDateStamp()
                initialValue = d.getPortfolioValue()

        currentGain = finalValue - initialValue
        if (isPercentage):
            currentGain = currentGain / initialValue * 100
        value = [self.datalist[-1].getDateStamp(), currentGain,3]
        retval.append(value)
        return retval


    def getROI(self, isPercentage):
        """
            returns the total gain over the whole datalist
            isPercentage: if true, return gain as a percentage, otherwise return true gain
            return: double of total gain
        """
        value = 0

        initialDataPoint = self.datalist.getEarliestDataPoint()
        initialValue = initialDataPoint.getPortfolioValue()
        finalValue = self.datalist.getLatestDataPoint().getPortfolioValue()

        value = finalValue - initialValue
        if (isPercentage):
            value = value / initialValue * 100

        return value

    def getPayBackPeriod(self):
        """
            returns number of days it took to earn back the initialCapital
            returns payback period in days. If no payback, return -1
        """
        initialDataPoint = self.datalist.getEarliestDataPoint()

        paidBack = self.initialCapital*2
        gain = 0
        for d in self.datalist:
            value = d.getPortfolioValue()
            if (value >= paidBack):
                return (d.getDateStamp() - initialDataPoint.getDateStamp()).days

        return -1


    def getNumTrades(self, period, buyOrSell):
        """
            returns number of trades per period
            period: enum Period.HOURLY, DAILY, WEEKLY, MONTHLY
            returns ordered list of tuples(datetime, numTrades)
        """
        initialDataPoint = self.datalist.getEarliestDataPoint()
        if period == Period.TOTAL:
            retval = []
            numTrades = 0
            for d in self.datalist:
                if d.getAction() == buyOrSell:
                    numTrades += 1

            value = [self.datalist.getLatestDataPoint().getDateStamp(), numTrades]
            retval.append(value)

        else:
            retval = []
            numTrades = 0
            initialDate = initialDataPoint.getDateStamp()
            endDate = (initialDate+relativedelta(months = self.monthlyDict[period], days=self.dailyDict[period]))

            for d in self.datalist:
                if (d.getDateStamp() <= endDate) and (d.getAction() == buyOrSell):
                    numTrades += 1

                #special case where exiting the market involves selling everything
                if d.getAction() == Action.EXIT and buyOrSell == Action.SELL:
                    numTrades += 1
                if (d.getDateStamp() > endDate):

                    value = [endDate, numTrades]
                    if d.getAction() == buyOrSell:
                        numTrades = 1
                    else:
                        numTrades = 0
                    initialDate = d.getDateStamp()
                    endDate = (initialDate+relativedelta(months = self.monthlyDict[period], days=self.dailyDict[period]))
                    retval.append(value)

            value = [self.datalist[-1].getDateStamp(), numTrades]
            retval.append(value)


        return retval

    def getSumTrades(self, period):
        """
            returns total number of buys and sells per time period
        """

        numBuys = self.getNumTrades(period, Action.BUY)
        numSells = self.getNumTrades(period, Action.SELL)
        numExits = self.getNumTrades(period, Action.EXIT)
        return numBuys[0][1] + numSells[0][1] + numExits[0][1]


    def getFinalValue(self):
        """
            return final value of the investment
        """
        d = self.datalist.getLatestDataPoint()
        return d.getPortfolioValue()

    def getValue(self, period):
        if (period == Period.TOTAL):
            return getFinalValue()

        retval = []
        initialDate = self.datalist.getEarliestDataPoint().getDateStamp()
        #this exposes internal implementation of BackTestHistory
        for d in self.datalist:
            if d.getDateStamp() > (initialDate+relativedelta(months = self.monthlyDict[period], days=self.dailyDict[period])):
                finalValue = d.getPortfolioValue()
                value = [(initialDate+relativedelta(months = self.monthlyDict[period], days=self.dailyDict[period])), finalValue]
                retval.append(value)

                initialDate = d.getDateStamp()
        finalValue = d.getPortfolioValue()
        value = [self.datalist[-1].getDateStamp(), finalValue]
        retval.append(value)
        return retval
