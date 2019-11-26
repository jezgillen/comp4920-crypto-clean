#!/usr/bin/python3
import sys
import qdarkstyle
from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QGroupBox, QVBoxLayout, QWidget, QPushButton, QGridLayout, QLabel, QComboBox, QScrollArea, QInputDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDir, QUrl

import plotly
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd

import bots
import fetchData
import exceptions

class GraphView(QWebEngineView):
    def __init__(self, parent, historicalData, coinName, comparison=False):
        super().__init__()
        self.plotlyFigure = None # this variable stores the graph to be displayed
        self.plotlyFigure = self.makeCandlestickGraph(historicalData, coinName, comparison)
        self.refreshFig()

    def setLog(self, isLog):
        fig = self.plotlyFigure
        if isLog:
            fig['layout']['yaxis_type'] = "log"
            fig['layout']['yaxis2_type'] = "log"
        else:
            fig['layout']['yaxis_type'] = "linear"
            fig['layout']['yaxis2_type'] = "linear"
        self.refreshFig()

    def addHistoricalData(self,historicalData, coinName):
        self.plotlyFigure = self.makeCandlestickGraph(historicalData, coinName, comparison=False)
        self.refreshFig()

    def addPortfolioValue(self, buySellData, botName=None, botNum=1):
        xData = buySellData.getDateHistory()
        yData = buySellData.getPortfolioValueHistory()

        self.plotlyFigure.add_trace(
            go.Scatter(x=xData, y=yData,
            name= botName+' Portfolio Value (USD)' if botName is not None else 'Portfolio Value (USD)',
            mode = 'lines',
            hovertext = 'Portfolio Value (USD)',
            yaxis='y2',
            opacity=0.8,
            line=dict(color='#e377c2' if botNum == 2 else '#aae3c7')
            )
        )
        self.refreshFig()

    def addBuySellLines(self, buySellData, botName=None, botNum=1):
        buyDates = []
        buyPrices = []
        sellDates = []
        sellPrices = []
        stopDates = []
        stopPrices = []
        max = 0
        scaler2 = 0.8
        scaler1 = 0.2
        for t in buySellData:
            if t.getMarketPrice() > max:
                max = t.getMarketPrice()
        for t in buySellData:
            if t.getAction() is bots.Action.BUY:
                buyDates.append(t.getDateStamp())
                if botNum == 2:
                    buyPrices.append(max*scaler2)
                else:
                    buyPrices.append(max*scaler1)
            elif t.getAction() is bots.Action.SELL:
                sellDates.append(t.getDateStamp())
                if botNum == 2:
                    sellPrices.append(max*scaler2)
                else:
                    sellPrices.append(max*scaler1)
            elif t.getAction() is bots.Action.EXIT:
                stopDates.append(t.getDateStamp())
                if botNum == 2:
                    stopPrices.append(max*scaler2)
                else:
                    stopPrices.append(max*scaler1)


        self.plotlyFigure.add_trace(go.Scatter(x=buyDates,
            y=buyPrices,
            name="Buy" if botName is None else botName+" Buy",
            mode='markers',
            marker=dict(symbol=6, size=12),
            marker_color="yellow" if botNum == 2 else '#17BECF',
            hovertemplate="Buy on %{x}" ))

        self.plotlyFigure.add_trace(go.Scatter(x=sellDates,
            y=sellPrices,
            name="Sell" if botName is None else botName+" Sell",
            mode='markers',
            marker=dict(symbol=5, size=12),
            marker_color="orange" if botNum == 2 else '#7F7F7F',
            hovertemplate="Sell on %{x}"))

        if(len(stopDates) != 0):
            self.plotlyFigure.add_trace(go.Scatter(x=stopDates,
                y=stopPrices,
                name="Stop" if botName is None else botName+" Stop",
                mode='markers',
                marker=dict(symbol=204, size = 20),
                marker_color="orange" if botNum == 2 else'#ffffff',
                hovertemplate="Exit at %{x}"))

        self.plotlyFigure.update_layout(showlegend=True)
        self.refreshFig()

    def refreshFig(self):
        ''' Updates the graph display with any changes to plotlyFigure '''
        path = QDir.current().filePath('plotly-latest.min.js')
        local = QUrl.fromLocalFile(path).toString()

        raw_html = '<html style="background-color: #31363b;"><head><meta charset="utf-8" />'
        raw_html += '<script src="{}"></script></head>'.format(local)
        raw_html += '<body style="margin: 0; padding: 0;">'
        raw_html += plotly.offline.plot(self.plotlyFigure, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'


        # update the actual display with setHtml
        self.setHtml(raw_html)

    def updateTitle(self, newTitle):
        self.plotlyFigure.update_layout (
            title=newTitle
        )

    def makeCandlestickGraph(self, historicalData, coinName, comparison):
        # create graph
        data = historicalData
        open_data = data['Open']
        high_data = data['High']
        low_data = data['Low']
        close_data = data['Close']
        dates = data['Date']

        fig = go.Figure(data=[go.Candlestick(x=dates,
                               name="Historical Data",
                               open=open_data, high=high_data,
                               low=low_data, close=close_data,
                               increasing_line_color="#EE0000", decreasing_line_color="#00EE00")])
        fig['layout']['legend'] = dict( orientation = 'h', yanchor='top',xanchor='center',y=1.3,x=0.5)
        fig['layout']['margin'] = dict( t=40, b=40, r=40, l=40 )


        fig.update_xaxes(title_text='Date')
        fig.update_yaxes(title_text='Price (USD)')
        fig['layout']['yaxis2'] = dict(title='Portfolio Value (USD)', overlaying='y', side='right')
        fig['layout']['yaxis']['fixedrange'] = False
        fig['layout']['yaxis2']['fixedrange'] = False
        fig['layout']['yaxis2']['rangemode'] = 'tozero'
        fig.update_layout(
            title= coinName + ' Market Price History' if comparison == False else '',
            paper_bgcolor='#19232D',
            template='plotly_dark',
        )
        return fig
    def clearFig(self):
        self.plotlyFigure.data = [self.plotlyFigure.data[0]]

    def clearGraph(self):
        # Clear markers from graph
        self.plotlyFigure.data = [self.plotlyFigure.data[0]]
        self.refreshFig()
