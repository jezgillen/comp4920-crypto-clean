#!/usr/bin/python3
from datetime import *
import plotly.graph_objs as go
from enum import Enum
from parameterView.formView import InputType
import sys, os, json, copy
from dateutil.parser import parse
import pandas as pd
import exceptions
import inspect


class Action(Enum):
    BUY = 0
    SELL = 1
    NOACTION = 2
    EXIT = 3

class BotState:
    def __init__(self, date, cash, coin, closeMarketPrice, action):
        self.date = date
        self.cash = cash
        self.coin = coin
        self.marketPrice = closeMarketPrice #make sure this is the closing price
        self.action = action # must be a member of the Action Enum
    def getDateStamp(self):
        return self.date
    def getCashBalance(self):
        return self.cash
    def getCoinAmount(self):
        return self.coin
    def getMarketPrice(self):
        return self.marketPrice
    def getAction(self):
        return self.action
    def getPortfolioValue(self):
        return self.marketPrice*self.coin + self.cash


class BacktestHistory:
    # purpose is to hold the information
    # that is currently held by buySellData, and returned by bot.processHistoricalData()
    def __init__(self):
        self.history = []
        self.lastBuyPrice = 0
    def insertBotState(self, date, cash, coin, closeMarketPrice, action):
        state = BotState(date, cash, coin, closeMarketPrice, action)
        self.history.append(state)
        if(action == Action.BUY):
            self.lastBuyPrice = closeMarketPrice
    def getLastBuyPrice(self):
        return self.lastBuyPrice
    def getCashBalanceHistory(self):
        return [s.getCashBalance() for s in self.history]
    def getDateHistory(self):
        return [s.getDateStamp() for s in self.history]
    def getCoinHistory(self):
        return [s.getCoinAmount() for s in self.history]
    def getMarketPriceHistory(self):
        return [s.getMarketPrice() for s in self.history]

    def getPortfolioValueHistory(self):
        retval = []
        for h in self.history:
            retval.append(h.getPortfolioValue())
        return retval
    def getActionHistory(self):
        return [s.getAction() for s in self.history]
    def getEarliestDataPoint(self):
        return self.history[0]
    def getLatestDataPoint(self):
        return self.history[len(self.history)-1]
    def getNumDataPoints(self):
        return len(self.history)
    def getFinalCashAmount(self):
        return self.getLatestDataPoint().getCashBalance()
    def getFinalCointAmount(self):
        return self.getLatestDataPoint().getCoinAmount()
    def getFinalMarketPrice(self):
        return self.getLatestDataPoint().getMarketPrice()
    def __iter__(self):
        yield from self.history
    def __getitem__(self, key):
        return self.history[key]
    def __len__(self):
        return len(self.history)


class Bot:
    '''
    Each of the following methods should be overridden by a child class
    But it should maintain the same arguments and the same return type
    '''
    def __init__(self):
        '''
        Overwrite this function to create bot specific parameters, and give them a default value
        remember to use super().__init__() at the start of your version of this function
        '''
        self.parameters = {}
        self.parametersDefault = {}
        self.parameterType = {}
        self.parameterHelpString = {}
        self.savePath = os.path.abspath('savedBots/')
        self.botDescription = ""
        self.coinAmount = 0


        # All bots will have the parameters below, any specific
        # parameters should be defined in the overriding method
        self._setParam('Name', self.getName(), InputType.string, 'Name of bot')
        self._setParam("Bot Type", self.getName(),
                InputType.string, "The algorithm this bot is running")
        self._setParam("Start Trading Date", datetime(2017, 1, 1),
                InputType.date, "The date when this bot will begin trading")
        self._setParam("End Trading Date", datetime(2018, 1, 1),
                InputType.date, "The date when this bot will stop trading")
        self._setParam("Stop Loss", 50.0,
                InputType.percentage,
                "(% of coin value) If the coin value drops by x% since your last trade, immediately sell everything and stop trading")
        self._setParam("Cash Amount", 10000.0,
                InputType.currency, "(USD) This is the amount of USD the bot starts with")

        self._setParam("Fee Per Trade", 0.02,
                InputType.percentage, "This is the fee charged by the exchange, in % of buy/sell value")


        self._createSaveFolder()
        self.setDescription(inspect.getdoc(self))


    def getDescription(self):
        return self.botDescription

    def setDescription(self, description):
        self.botDescription = description

    def checkParameters(self):
        '''
        Overwrite this function
        '''
        raise NotImplementedError()


    def processHistoricalData(self, data):
        '''
        Overwrite this function
        Must return an object of type BacktestHistory
        '''
        raise NotImplementedError()

    def setParams(self, **kwargs):
        '''
        Usage:
            b = someBot()
            b.setParams(stopLoss=20, randomParameter="blah")
            print(b.stopLoss)  # will print 20

        This doesn't need to be reimplemented in each subclass, it just sets the parameters
        '''
        for key in kwargs:
            self._setParam(name=key, value=kwargs[key])

    def getParameters(self):
        '''
            returns dictionary of parameters name:value
        '''
        return self.parameters

    def getParameterNames(self):
        '''
        returns a list of parameter names
        This doesn't need to be reimplemented in each subclass
        '''
        return self.parameters.keys()

    def getParameterTypes(self):
        '''
        returns a dict of parameter types
        This doesn't need to be reimplemented in each subclass
        '''
        return self.parameterType

    def getParameterHelpStrings(self):
        '''
        returns a dict of parameter help strings
        This doesn't need to be reimplemented in each subclass
        '''
        return self.parameterHelpString

    def _setParam(self, name, value, type=InputType.default, helpString=""):
        '''
        for internal use only, during init. This function creates a parameter
        This doesn't need to be reimplemented in each subclass
        '''
        self.parameters[name] = value
        self.parametersDefault[name] = value
        self.parameterType[name] = type
        self.parameterHelpString[name] = helpString

        # Make a camel case version of that variable name
        variableName = name.replace(" ", "")
        if(variableName[0].isupper()):
            variableName = variableName[0].lower() + variableName[1:]
        setattr(self, variableName, value) #allows parameters to be accessed with self.<paramName>


    def resetBotToDefault(self):
        for p in self.parametersDefault:
            self.changeParam(p, self.parametersDefault[p])

    def getDefaultValue(self, name):
        return self.parametersDefault[name]

    def changeParam(self, name, value):
        if name not in self.parameters:
            print("Parameter " + name + " does not exist.")
        else:
            self.parameters[name] = value
            # Make a camel case version of that variable name
            variableName = name.replace(" ", "")
            if(variableName[0].isupper()):
                variableName = variableName[0].lower() + variableName[1:]
            setattr(self, variableName, value) #allows parameters to be accessed with self.<paramName>

    def save(self):
        data = copy.deepcopy(self.parameters)
        for d in data:
            if (isinstance(data[d], datetime)):
                data[d] = datetime.strftime(data[d], '%Y-%m-%d')
        path = self.getSavefilePath()
        with open(path, 'w') as f:
            json.dump(data, f)
        f.close()

    def load(self):
        path = self.getSavefilePath()
        if(os.path.isfile(path)):
            with open(path,'r') as f:
                data = json.load(f)
            f.close()

            for d in data:
                if self._isDate(data[d]):
                    data[d] = datetime.strptime(data[d], '%Y-%m-%d')
                self.changeParam(d, data[d])

    def _isDate(self, string, fuzzy=False):
        if not isinstance(string, str):
            return False
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    def setSavefilePath(self, path):
        pass
    def getSavefilePath(self):
        path = os.path.join(self.savePath,self.getAlias() + '.json')
        return path
    def getName(self):
        return self.__class__.__name__

    def _createSaveFolder(self):
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

    def setAlias(self, name):
        self.changeParam('Name', name)
        #special case where the default name of a bot is the name of that bot
        self.parametersDefault['Name'] = name

    def getAlias(self):
        return self.parameters['Name']


class ROC(Bot):
    '''
    Rate of Change(ROC).

    This bot will make a buy decision when the rate of change over Short ROC Interval is below the rate of change over Long ROC Interval for N consecutive days, where N is equal to Consecutive Day Run.
    Similarly, it will sell if the reverse is true. Generally, Short ROC Interval is 5 days, Long ROC Interval is 200 days, and N is 2 consecutive days. Short ROC Interval should be smaller than Long ROC Interval.
    '''
    def __init__(self):
        super().__init__()
        self._setParam('Short ROC Interval', 5, InputType.int, "If the this value is below the Long ROC Interval for Consecutive day run days, then buy")
        self._setParam('Long ROC Interval', 20, InputType.int, "If the Short ROC Interval is below this value  for Consecutive day run days, then buy")
        self._setParam('Consecutive Day Run', 2, InputType.int, "If Short ROC Interval is below the Long ROC Interval for this many days, then buy")
        self._setParam("Amount To Trade", 100.0, InputType.currency,  "(USD) amount to buy or sell")


    def checkParameters(self):
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        shortROC = self.getParameters().get('Short ROC Interval')
        longROC = self.getParameters().get('Long ROC Interval')
        ma = self.getParameters().get('Consecutive Day Run')
        if st >= et:
            raise exceptions.InvalidStartEndDates
        if shortROC >= longROC or shortROC == 0 or longROC == 0:
            raise exceptions.InvalidIntervals
        if ma <= 0:
            raise exceptions.InvalidDays

    def processHistoricalData(self, data):
        self.coinAmount = 0
        shortROCInterval = self.shortROCInterval
        longROCInterval = self.longROCInterval
        consecDays = self.consecutiveDayRun
        amountToTrade = self.amountToTrade


         # sort and convert data
        df = data.copy()
        df.Date = pd.to_datetime(df.Date)
        df.set_index("Date",inplace=True,drop=True,verify_integrity=True)
        df = df.sort_index()


        #check dates
        earliestDate = df.index[0]
        latestDate = df.index[-1]
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        if (earliestDate > st or latestDate < et):
            raise IndexError


        #setup
        buySellData = BacktestHistory()
        prevAction = Action.NOACTION
        closePrices = {}      #key = date, values in this dict are used to calculate long/short ROC
        numDaysToBuy = consecDays
        numDaysToSell = consecDays

        noAction = False
        for date, rows in df[:self.endTradingDate].iterrows():
            closePrices[date] = rows.Close
            #print(type(date))
            if date >= self.startTradingDate:
                value = self.cashAmount + self.coinAmount*rows.Close
                #check stoploss condition
                if(rows.Close < (1 - self.stopLoss/100)*buySellData.getLastBuyPrice()):
                    self._stopAction(buySellData, date, rows.Close)
                    break


                #calculate momentum using ROC
                shortROC = self._calculateNDayROC(rows.Close, date, closePrices, shortROCInterval)
                longROC = self._calculateNDayROC(rows.Close, date, closePrices, longROCInterval)
                if shortROC is not None and longROC is not None:
                    if shortROC < longROC:
                        numDaysToBuy -= 1
                        numDaysToSell = consecDays
                    elif shortROC > longROC:
                        numDaysToSell -= 1
                        numDaysToBuy = consecDays
                    else:
                        numDaysToSell = consecDays
                        numDaysToBuy = consecDays


                    #check buy or sell
                    if (numDaysToBuy <= 0):
                        self._buyAction(buySellData, date, rows.Close)

                    elif (numDaysToSell <= 0):
                        self._sellAction(buySellData, date, rows.Close)
                    else:
                        noAction = True
                if noAction:
                    self._noAction(buySellData, date, rows.Close)

                else:
                    numDaysToSell = consecDays
                    numDaysToBuy = consecDays
                noAction = False
        return buySellData

    def _buyAction(self, buySellData, date, closePrice):
        if (self.cashAmount >= self.amountToTrade + self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount -= self.amountToTrade
            self.coinAmount += self.amountToTrade / closePrice
            buySellData.insertBotState(date, self.cashAmount, self.coinAmount, closePrice , Action.BUY)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def  _stopAction(self, buySellData, date, closePrice):
        if (self.coinAmount > 0):
            self.cashAmount += (1-(self.feePerTrade/100))*closePrice * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(date, self.cashAmount, self.coinAmount, closePrice, Action.EXIT)

    def _sellAction(self, buySellData, date, closePrice):
        if closePrice != 0:
            coinValue = self.coinAmount * closePrice
            if (coinValue - self.amountToTrade >= 0 and self.coinAmount > self.amountToTrade*(self.feePerTrade/100)):
                self.cashAmount += self.amountToTrade
                self.coinAmount -= self.amountToTrade / closePrice
                buySellData.insertBotState(date, self.cashAmount, self.coinAmount, closePrice, Action.SELL)
                self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def _noAction(self, buySellData, date, closePrice):
        buySellData.insertBotState(date, self.cashAmount, self.coinAmount, closePrice, Action.NOACTION)

    def _calculateNDayROC(self, currentValue, currentDate, closePrices, numdays):
        pastDate = currentDate - timedelta(days=numdays)
        if pastDate in closePrices:
            return self._calculateROC(currentValue, closePrices[pastDate])
        return None
    def _calculateROC(self, valNow, valDaysAgo):
        return (valNow - valDaysAgo) / valDaysAgo * 100

class RSI(Bot):
    '''
    Relative Strength Index (RSI)

    This algorithm is based on the RSI. When the price rapidly goes up, the algorithm assumes it's about to reverse and go back to it's former average.
    It is a mean reversion style algorithm.
    The RSI is an index that fluctuates between 0 and 100. If it's closer to 100 the asset is considered "overbought", i.e. the price is higher than it should be. If it's closer to 0, the asset is considered "oversold". The Upper and Lower thresholds set the points at which the bot considers the cryptocurrency overbought or oversold.
    See here for original formulation of the RSI: <a href="https://books.mec.biz/tmp/books/218XOTBWY3FEW2CT3EVR.PDF">New Concepts in Technical Trading Systems (1978)</a> (page 65)
    '''
    def __init__(self):
        super().__init__()

        self._setParam("Upper Threshold", 70,
                InputType.int, "If the RSI gets higher than this value, sell")
        self._setParam("Lower Threshold", 30,
                InputType.int, "If the RSI gets lower than this value, buy")
        self._setParam("Moving Avg Window Size", 14,
                InputType.int, "The length of the moving average in days")
        self._setParam("Amount To Trade", 100.,
                InputType.currency, "(USD) amount to buy or sell each time the RSI crosses a threshold")

    def checkParameters(self):
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        ut = self.getParameters().get('Upper Threshold')
        lt = self.getParameters().get('Lower Threshold')
        ma = self.getParameters().get('Moving Avg Window Size')
        if st >= et:
            raise exceptions.InvalidStartEndDates
        if lt >= ut:
            raise exceptions.InvalidThresholds
        if ma == 0:
            raise exceptions.InvalidMovingAvgs

    def processHistoricalData(self, data):
        self.coinAmount = 0
        data = data.copy()
        window_size = self.movingAvgWindowSize
        amountToTrade = self.amountToTrade
        data.Date = pd.to_datetime(data.Date)

        # sort and convert data
        df = data.copy()
        df.set_index("Date",inplace=True,drop=True,verify_integrity=True)
        df = df.sort_index()


        #check dates
        earliestDate = df.index[0]
        latestDate = df.index[-1]
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        if (earliestDate > st or latestDate < et):
            raise IndexError


        # calculate daily gain
        gain = df.Close - df.Open

        # convert to separate loss and gain
        df['upClose'] = gain.clip(0, None)
        df['downClose'] = -gain.clip(None, 0)

        window = pd.Timedelta(days=window_size)

        # do rolling mean over both
        df.downClose = df.downClose.rolling(window_size).mean()
        df.upClose = df.upClose.rolling(window_size).mean()

        startDate = df.index[0]
        df.loc[startDate:startDate+window,'downClose'] = None
        df.loc[startDate:startDate+window,'upClose'] = None

        # calculate RSI
        df['RSI'] = 100 - (100/(1+df.upClose/df.downClose))
        overbought = df.RSI > self.upperThreshold
        oversold = df.RSI < self.lowerThreshold

        # initialise variables for loop
        prevOverbought = True
        prevOversold = True
        cashAmount = self.cashAmount
        coinAmount = self.coinAmount
        prevValue = cashAmount + coinAmount*df.Close[0]
        prevAction = Action.NOACTION
        buySellData = BacktestHistory()
        for date, rows in df[self.startTradingDate:self.endTradingDate].iterrows():
            if(rows.Close < (1 - self.stopLoss/100)*buySellData.getLastBuyPrice()):
                # stop and sell all coins
                cashAmount += (1-(self.feePerTrade/100))*coinAmount*rows.Close
                coinAmount = 0
                buySellData.insertBotState(date, cashAmount, coinAmount, rows.Close, Action.EXIT)
                break

            if ((not prevOverbought) and (overbought[date]) and
                    (coinAmount > amountToTrade/rows.Close) and
                    (cashAmount > self.amountToTrade*(self.feePerTrade/100)) and
                    prevAction != Action.SELL):
                #sell
                cashAmount += amountToTrade
                coinAmount -= amountToTrade/rows.Close # USD amount / price of a single coin
                buySellData.insertBotState(date, cashAmount, coinAmount, rows.Close, Action.SELL)

                self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

                # Uncomment prevAction changes to make sure it
                # doesn't buy or sell multiple times in a row
                #  prevAction = Action.SELL
            elif ((not prevOversold) and (oversold[date]) and
                    (cashAmount > amountToTrade + self.amountToTrade*(self.feePerTrade/100)) and
                    prevAction != Action.BUY):
                # buy
                cashAmount -= amountToTrade
                coinAmount += amountToTrade/rows.Close # USD amount / price of a single coin
                buySellData.insertBotState(date, cashAmount, coinAmount, rows.Close, Action.BUY)
                self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)
                #  prevAction = Action.BUY
            else:
                # no action
                buySellData.insertBotState(date, cashAmount, coinAmount, rows.Close, Action.NOACTION)

            prevOverbought = overbought[date]
            prevOversold = oversold[date]

        return buySellData

class TMA(Bot):
    '''
    Triple Moving Average (TMA)

    This algorithm makes use of three moving average values, each of which have an increasing window.
    When the short term is larger than the medium term average, and the medium term average is larger than the long term average, the algorithm sells all the coins that it holds
    When the short term average is lower than the medium term average is lower than the long term average, the algorithm buys if it has previously sold. This is also the case if the short term average is larger than the medium term average, and all other factors are the same
    The algorithm will stop and sell everything it holds if the value of the coin it holds drops buy the Stop Loss percentage.
    This is a trend following algorithm.
    '''
    def __init__(self):
        super().__init__()

        self._setParam("Short Moving Avg Days", 10,
                InputType.int, "This is the length of the first moving average")
        self._setParam("Medium Moving Avg Days", 20,
                InputType.int, "This is the length of the second moving average")
        self._setParam("Long Moving Avg Days", 40,
                InputType.int, "This is the length of the third moving average")
        self._setParam("Amount To Trade", 100.0,
                InputType.currency, "(USD) value to trade each time it wants to trade")


    def checkParameters(self):
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        sm = self.getParameters().get('Short Moving Avg Days')
        mm = self.getParameters().get('Medium Moving Avg Days')
        lm = self.getParameters().get('Long Moving Avg Days')
        if st >= et:
            raise exceptions.InvalidStartEndDates
        if sm >= mm or mm >= lm or sm == 0 or mm == 0 or lm == 0:
            raise exceptions.InvalidMovingAvgs

    def processHistoricalData(self, data):
        self.coinAmount = 0
        dates = data.Date

        # turn the high and low prices into an average for each day
        averagePrices = []
        for i in range(len(data.High)):
            averagePrices.append((datetime.strptime(dates[i], '%Y-%m-%d').date(), (data.High[i] + data.Low[i])/2))

        for i in range(len(averagePrices) - 1):
            if averagePrices[i][0] != averagePrices[i+1][0] + timedelta(1):
                tmpList = []
                avg = (averagePrices[i][1] + averagePrices[i+1][1]) / 2
                for j in range((averagePrices[i][0] - averagePrices[i+1][0]).days - 1):
                    tmpList.append((averagePrices[i][0] - timedelta(1 + j), avg))
                for j in range(len(tmpList)):
                    averagePrices.insert(j + i + 1, tmpList[j])

        # Calculate average of short moving average - keeping track of head and tail
        i = 0
        while averagePrices[i][0] > self.startTradingDate.date():
            i += 1
        s_Sum = 0
        headIndex = i
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.shortMovingAvgDays - 1)).date():
            s_Sum += averagePrices[i][1]
            i += 1
        s_Sum += averagePrices[i][1]
        s_TailIndex = i
        shortTermAvg = s_Sum / self.shortMovingAvgDays

        # Calculate averge of medium moving average - keeping track of tail
        i = headIndex
        m_Sum = 0
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.mediumMovingAvgDays - 1)).date():
            m_Sum += averagePrices[i][1]
            i += 1
        m_Sum += averagePrices[i][1]
        m_TailIndex = i
        medTermAvg = m_Sum / self.mediumMovingAvgDays

        # Calculate averge of long moving average - keeping track of tail
        i = headIndex
        l_Sum = 0
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.longMovingAvgDays - 1)).date():
            l_Sum += averagePrices[i][1]
            i += 1
        l_Sum += averagePrices[i][1]
        l_TailIndex = i
        longTermAvg = l_Sum / self.longMovingAvgDays

        # Iterate from startDate to endDate calculating averages for each day
        buySellData = None
        buySellData = BacktestHistory()
        previousAction = 'Sell'
        headDate = averagePrices[headIndex][0]

        while headDate < self.endTradingDate.date():
            if (shortTermAvg >= medTermAvg) and (medTermAvg >= longTermAvg) and previousAction is 'Sell':
                previousAction = 'Buy'
                self.buyAction(headDate, averagePrices, buySellData, headIndex)
            elif (shortTermAvg <= medTermAvg) and (medTermAvg <= longTermAvg) and previousAction is 'Buy':
                previousAction = 'Sell'
                self.sellAction(headDate, averagePrices, buySellData, headIndex)
            elif (shortTermAvg >= medTermAvg) and (medTermAvg <= longTermAvg) and previousAction is 'Buy':
                previousAction = 'Sell'
                self.sellAction(headDate, averagePrices, buySellData, headIndex)
            elif previousAction is 'Buy' and self.getLastBuy(buySellData) is not None and (self.getLastBuy(buySellData) - (self.getLastBuy(buySellData)*(self.stopLoss/100))) > averagePrices[headIndex][1]:
                print("BuySell:", self.getLastBuy(buySellData), "Av Price:", averagePrices[headIndex][1], self.stopLoss)
                previousAction = 'Stop'
                self.stopAction(headDate, averagePrices, buySellData, headIndex)
            else:
                self.noAction(headDate, averagePrices, buySellData, headIndex)

            headIndex -= 1
            s_Sum += averagePrices[headIndex][1]
            s_Sum -= averagePrices[s_TailIndex][1]
            m_Sum += averagePrices[headIndex][1]
            m_Sum -= averagePrices[s_TailIndex][1]
            l_Sum += averagePrices[headIndex][1]
            l_Sum -= averagePrices[l_TailIndex][1]

            headDate = averagePrices[headIndex][0]
            #print('Head again' + datetime.strftime(headDate, '%d-%m-%Y'))
            s_TailIndex -= 1
            m_TailIndex -=1
            l_TailIndex -= 1

            shortTermAvg = s_Sum / self.shortMovingAvgDays
            medTermAvg = m_Sum / self.mediumMovingAvgDays
            longTermAvg = l_Sum / self.longMovingAvgDays

        if shortTermAvg > longTermAvg and previousAction is 'Sell':
            self.buyAction(headDate, averagePrices, buySellData, headIndex)
        elif shortTermAvg < longTermAvg and previousAction is 'Buy':
            self.sellAction(headDate, averagePrices, buySellData, headIndex)

        else:
            self.noAction(headDate, averagePrices, buySellData, headIndex)
        return buySellData

    def getLastBuy(self, buySellData):
        buyPrice = None
        for state in buySellData:
            if state.getAction() == Action.BUY:
                buyPrice = state.getMarketPrice()
        return buyPrice

    def buyAction(self, headDate, averagePrices, buySellData, headIndex):
        if (self.cashAmount >= self.amountToTrade + self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount -= self.amountToTrade
            self.coinAmount += self.amountToTrade / averagePrices[headIndex][1]
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.BUY)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def sellAction(self, headDate, averagePrices, buySellData, headIndex):
        if (self.cashAmount > self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount += averagePrices[headIndex][1] * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.SELL)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def stopAction(self, headDate, averagePrices, buySellData, headIndex):
        # if (self.coinAmount - self.amountToTrade >= 0):
            self.cashAmount += (1-(self.feePerTrade/100))*averagePrices[headIndex][1] * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.EXIT)

    def noAction(self, headDate, averagePrices, buySellData, headIndex):
        buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.NOACTION)

    def calculateStats(self, data):

        startBalance = self.cashAmountStart
        balance = self.cashAmountStart
        buyCount = 0
        sellCount = 0
        for b in backlog:
            if b[2] is 'Buy':
                balance -= b[1]
                buyCount += 1
            elif b[2] is 'Sell':
                balance += b[1]
                sellCount += 1
        print("Start: " + str(startBalance))
        print("End:   " + str(balance))
        if balance > startBalance:
            gain = ((balance - startBalance)/startBalance) * 100
            print("Gain: " + str(round(gain, 2)) + '%')
        if balance <= startBalance:
            loss = ((startBalance - balance)/startBalance) * 100
            print("Loss: " + str(round(loss, 2)) + '%')
        print("Buy Trades:   " + str(buyCount))
        print("Sell Trades:  " + str(sellCount))
        print("Total Trades: " + str(buyCount + sellCount))

class SMA(Bot):
    '''
    Simple Moving Average (SMA)

    This algorithm uses two moving averages, with two different sized windows.
    If the short term average becomes larger than the long term average, the algorithm will sell if it had previously bought
    If the long term average becomes larger than the short term average, and it holds no coins, it will purchase coins.
    The algorithm will stop and sell everything it holds if the value of the coin it holds drops buy the Stop Loss percentage.
    This is a trend following algorithm.
    '''
    def __init__(self):
        super().__init__()

        # parameters specific to this algorithm
        self._setParam("Short Moving Avg Days", 20,
                InputType.int, "This is the length of the moving average")
        self._setParam("Long Moving Avg Days", 40,
                InputType.int, "This is the length of the second moving average")
        self._setParam("Amount To Trade", 100.0,
                InputType.currency, "(USD) value to trade each time it wants to trade")


    def checkParameters(self):
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        sm = self.getParameters().get('Short Moving Avg Days')
        lm = self.getParameters().get('Long Moving Avg Days')
        if st >= et:
            raise exceptions.InvalidStartEndDates
        if sm >= lm or sm == 0 or lm == 0:
            raise exceptions.InvalidMovingAvgs

    def processHistoricalData(self, data):
        self.coinAmount = 0
        dates = data.Date
        # turn the high and low prices into an average for each day
        averagePrices= []
        for i in range(len(data.High)):
            averagePrices.append((datetime.strptime(dates[i], '%Y-%m-%d').date(), (data.High[i] + data.Low[i])/2))

        for i in range(len(averagePrices) - 1):
            if averagePrices[i][0] != averagePrices[i+1][0] + timedelta(1):
                tmpList = []
                avg = (averagePrices[i][1] + averagePrices[i+1][1]) / 2
                for j in range((averagePrices[i][0] - averagePrices[i+1][0]).days - 1):
                    tmpList.append((averagePrices[i][0] - timedelta(1 + j), avg))
                for j in range(len(tmpList)):
                    averagePrices.insert(j + i + 1, tmpList[j])

        # Calculate average of short moving average - keeping track of head and tail
        i = 0
        while averagePrices[i][0] > self.startTradingDate.date():
            i += 1
        s_Sum = 0
        headIndex = i
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.shortMovingAvgDays - 1)).date():
            s_Sum += averagePrices[i][1]
            i += 1
        s_Sum += averagePrices[i][1]
        s_TailIndex = i
        shortTermAvg = s_Sum / self.shortMovingAvgDays

        # Calculate averge of long moving average - keeping track of tail
        i = headIndex
        l_Sum = 0
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.longMovingAvgDays - 1)).date():
            l_Sum += averagePrices[i][1]
            i += 1
        l_Sum += averagePrices[i][1]
        l_TailIndex = i
        longTermAvg = l_Sum / self.longMovingAvgDays

        # Iterate from startDate to endDate calculating averages for each day
        buySellData = None
        buySellData = BacktestHistory()
        previousAction = 'Sell'
        headDate = averagePrices[headIndex][0]

        while headDate < self.endTradingDate.date():
            if shortTermAvg > longTermAvg and previousAction is 'Sell':
                previousAction = 'Buy'

                self.buyAction(headDate, averagePrices, buySellData, headIndex)
            elif shortTermAvg < longTermAvg and previousAction is 'Buy':
                previousAction = 'Sell'
                self.sellAction(headDate, averagePrices, buySellData, headIndex)

            elif previousAction is 'Buy' and self.getLastBuy(buySellData) is not None and (self.getLastBuy(buySellData) - (self.getLastBuy(buySellData)*(self.stopLoss/100))) > averagePrices[headIndex][1]:
                print("BuySell:", self.getLastBuy(buySellData), "Av Price:", averagePrices[headIndex][1], self.stopLoss)
                previousAction = 'Stop'
                self.stopAction(headDate, averagePrices, buySellData, headIndex)

            else:
                self.noAction(headDate, averagePrices, buySellData, headIndex)


            headIndex -= 1
            s_Sum += averagePrices[headIndex][1]
            s_Sum -= averagePrices[s_TailIndex][1]
            l_Sum += averagePrices[headIndex][1]
            l_Sum -= averagePrices[l_TailIndex][1]

            headDate = averagePrices[headIndex][0]

            s_TailIndex -= 1
            l_TailIndex -= 1
            shortTermAvg = s_Sum / self.shortMovingAvgDays
            longTermAvg = l_Sum / self.longMovingAvgDays

        if shortTermAvg > longTermAvg and previousAction is 'Sell':
            self.buyAction(headDate, averagePrices, buySellData, headIndex)

        elif shortTermAvg < longTermAvg and previousAction is 'Buy':
            self.sellAction(headDate, averagePrices, buySellData, headIndex)
        else:
            self.noAction(headDate, averagePrices, buySellData, headIndex)
        return buySellData

    def getLastBuy(self, buySellData):
        buyPrice = None
        for state in buySellData:
            if state.getAction() == Action.BUY:
                buyPrice = state.getMarketPrice()
        return buyPrice

    def buyAction(self, headDate, averagePrices, buySellData, headIndex):
        if (self.cashAmount >= self.amountToTrade + self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount -= self.amountToTrade
            self.coinAmount += self.amountToTrade / averagePrices[headIndex][1]
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.BUY)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def sellAction(self, headDate, averagePrices, buySellData, headIndex):
        if (self.cashAmount > self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount += averagePrices[headIndex][1] * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.SELL)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def stopAction(self, headDate, averagePrices, buySellData, headIndex):
        # if (self.coinAmount - self.amountToTrade >= 0):
            self.cashAmount += (1-(self.feePerTrade/100))*averagePrices[headIndex][1] * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.EXIT)

    def noAction(self, headDate, averagePrices, buySellData, headIndex):
        buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.NOACTION)

    def calculateStats(self, data):
        startBalance = self.cashAmountStart
        balance = self.cashAmountStart
        buyCount = 0
        sellCount = 0
        for b in backlog:
            if b[2] is 'Buy':
                balance -= b[1]
                buyCount += 1
            elif b[2] is 'Sell':
                balance += b[1]
                sellCount += 1
        print("Start: " + str(startBalance))
        print("End:   " + str(balance))
        if balance > startBalance:
            gain = ((balance - startBalance)/startBalance) * 100
            print("Gain: " + str(round(gain, 2)) + '%')
        if balance <= startBalance:
            loss = ((startBalance - balance)/startBalance) * 100
            print("Loss: " + str(round(loss, 2)) + '%')
        print("Buy Trades:   " + str(buyCount))
        print("Sell Trades:  " + str(sellCount))
        print("Total Trades: " + str(buyCount + sellCount))

class DEMA(Bot):
    '''
    Double Exponential Moving Average (DEMA)

    This algorithm uses two exponential moving averages, with two different sized windows.
    The moving averages are calculated with weighting given the the most recent data point.
    If the short term average becomes larger than the long term average, the algorithm will sell if it had previously bought
    If the long term average becomes larger than the short term average, and it holds no coins, it will purchase coins.
    The algorithm will stop and sell everything it holds if the value of the coin it holds drops buy the Stop Loss percentage.
    This is a trend following algorithm.
    '''
    def __init__(self):
        super().__init__()

        # parameters specific to this algorithm
        self._setParam("Short Moving Avg Days", 20,
                InputType.int, "This is the length of the moving average")
        self._setParam("Long Moving Avg Days", 40,
                InputType.int, "This is the length of the second moving average")
        self._setParam("Amount To Trade", 100.0,
                InputType.currency, "(USD) value to trade each time it wants to trade")


    def checkParameters(self):
        st = self.getParameters().get('Start Trading Date')
        et = self.getParameters().get('End Trading Date')
        sm = self.getParameters().get('Short Moving Avg Days')
        lm = self.getParameters().get('Long Moving Avg Days')
        if st >= et:
            raise exceptions.InvalidStartEndDates
        if sm >= lm or sm == 0 or lm == 0:
            raise exceptions.InvalidMovingAvgs

    def processHistoricalData(self, data):
        self.coinAmount = 0
        dates = data.Date

        # turn the high and low prices into an average for each day
        averagePrices= []
        for i in range(len(data.High)):
            averagePrices.append((datetime.strptime(dates[i], '%Y-%m-%d').date(), (data.High[i] + data.Low[i])/2))

        for i in range(len(averagePrices) - 1):
            if averagePrices[i][0] != averagePrices[i+1][0] + timedelta(1):
                tmpList = []
                avg = (averagePrices[i][1] + averagePrices[i+1][1]) / 2
                for j in range((averagePrices[i][0] - averagePrices[i+1][0]).days - 1):
                    tmpList.append((averagePrices[i][0] - timedelta(1 + j), avg))
                for j in range(len(tmpList)):
                    averagePrices.insert(j + i + 1, tmpList[j])

        # Calculate average of short moving average - keeping track of head and tail
        i = 0
        while averagePrices[i][0] > self.startTradingDate.date():
            i += 1
        s_Sum = 0
        headIndex = i
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.shortMovingAvgDays - 1)).date():
            s_Sum += averagePrices[i][1]
            i += 1
        s_Sum += averagePrices[i][1]
        s_TailIndex = i
        shortTermAvg = s_Sum / self.shortMovingAvgDays

        # Calculate averge of long moving average - keeping track of tail
        i = headIndex
        l_Sum = 0
        while averagePrices[i][0] > (self.startTradingDate - timedelta(self.longMovingAvgDays - 1)).date():
            l_Sum += averagePrices[i][1]
            i += 1
        l_Sum += averagePrices[i][1]
        l_TailIndex = i
        longTermAvg = l_Sum / self.longMovingAvgDays

        # Exponential Factor = 2/(N + 1)
        shortFactor = 2/(self.shortMovingAvgDays + 1)
        longFactor = 2/(self.longMovingAvgDays + 1)

        # Iterate from startDate to endDate calculating averages for each day
        buySellData = None
        buySellData = BacktestHistory()
        previousAction = 'Sell'
        headDate = averagePrices[headIndex][0]

        while headDate < self.endTradingDate.date():
            if shortTermAvg > longTermAvg and previousAction is 'Sell':
                previousAction = 'Buy'
                #buySellData.append((headDate, averagePrices[headIndex][1], 'Buy'))
                self.buyAction(headDate, averagePrices, buySellData, headIndex)
                #self.cashAmount -= averagePrices[headIndex][1] * self.amountToTrade
                #self.coinAmount += self.amountToTrade
                #buySellData.append((headDate, averagePrices[headIndex][1], self.coinAmount, self.cashAmount, 'Buy'))
            elif shortTermAvg < longTermAvg and previousAction is 'Buy':
                previousAction = 'Sell'
                self.sellAction(headDate, averagePrices, buySellData, headIndex)
                #buySellData.append((headDate, averagePrices[headIndex][1], 'Sell'))
                #self.cashAmount += averagePrices[headIndex][1] * self.amountToTrade
                #self.coinAmount -= self.amountToTrade
                #buySellData.append((headDate, averagePrices[headIndex][1], self.coinAmount, self.cashAmount, 'Sell'))
            elif previousAction is 'Buy' and self.getLastBuy(buySellData) is not None and (self.getLastBuy(buySellData) - (self.getLastBuy(buySellData)*(self.stopLoss/100))) > averagePrices[headIndex][1]:
                print("BuySell:", self.getLastBuy(buySellData), "Av Price:", averagePrices[headIndex][1], self.stopLoss)
                previousAction = 'Stop'
                self.stopAction(headDate, averagePrices, buySellData, headIndex)

            else:
                self.noAction(headDate, averagePrices, buySellData, headIndex)


            headIndex -= 1
            s_Sum += averagePrices[headIndex][1]
            s_Sum -= averagePrices[s_TailIndex][1]
            l_Sum += averagePrices[headIndex][1]
            l_Sum -= averagePrices[l_TailIndex][1]

            headDate = averagePrices[headIndex][0]
            s_TailIndex -= 1
            l_TailIndex -= 1
            shortTermAvg += shortFactor*(averagePrices[headIndex][1] - shortTermAvg)
            longTermAvg += longFactor*(averagePrices[headIndex][1] - longTermAvg)

        if shortTermAvg > longTermAvg and previousAction is 'Sell':
            self.buyAction(headDate, averagePrices, buySellData, headIndex)

        elif shortTermAvg < longTermAvg and previousAction is 'Buy':
            self.sellAction(headDate, averagePrices, buySellData, headIndex)


        else:
            self.noAction(headDate, averagePrices, buySellData, headIndex)
        return buySellData

    def getLastBuy(self, buySellData):
        buyPrice = None
        for state in buySellData:
            if state.getAction() == Action.BUY:
                buyPrice = state.getMarketPrice()
        return buyPrice

    def buyAction(self, headDate, averagePrices, buySellData, headIndex):
        if (self.cashAmount >= self.amountToTrade + self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount -= self.amountToTrade
            self.coinAmount += self.amountToTrade / averagePrices[headIndex][1]
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.BUY)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def sellAction(self, headDate, averagePrices, buySellData, headIndex):
        if (self.cashAmount > self.amountToTrade*(self.feePerTrade/100)):
            self.cashAmount += averagePrices[headIndex][1] * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.SELL)
            self.cashAmount -= self.amountToTrade*(self.feePerTrade/100)

    def stopAction(self, headDate, averagePrices, buySellData, headIndex):
        # if (self.coinAmount - self.amountToTrade >= 0):
            self.cashAmount += (1-(self.feePerTrade/100))*averagePrices[headIndex][1] * self.coinAmount
            self.coinAmount = 0
            buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.EXIT)

    def noAction(self, headDate, averagePrices, buySellData, headIndex):
        buySellData.insertBotState(headDate, self.cashAmount, self.coinAmount, averagePrices[headIndex][1], Action.NOACTION)

    def calculateStats(self, data):
        startBalance = self.cashAmountStart
        balance = self.cashAmountStart
        buyCount = 0
        sellCount = 0
        for b in backlog:
            if b[2] is 'Buy':
                balance -= b[1]
                buyCount += 1
            elif b[2] is 'Sell':
                balance += b[1]
                sellCount += 1
        print("Start: " + str(startBalance))
        print("End:   " + str(balance))
        if balance > startBalance:
            gain = ((balance - startBalance)/startBalance) * 100
            print("Gain: " + str(round(gain, 2)) + '%')
        if balance <= startBalance:
            loss = ((startBalance - balance)/startBalance) * 100
            print("Loss: " + str(round(loss, 2)) + '%')
        print("Buy Trades:   " + str(buyCount))
        print("Sell Trades:  " + str(sellCount))
        print("Total Trades: " + str(buyCount + sellCount))


if __name__ == '__main__':

    b = Bot()
    print(b.stopLoss)
    b.setParams(stopLoss=20)
    print(b.stopLoss)
    print(dir(b))
