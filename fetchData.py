#!/usr/bin/python3
import pandas as pd
from datetime import datetime
import urllib.request
import urllib.error
import shutil
import os

dataDirectory = "data"

def getData(exchange="Bitfinex", resolution="day", coin="BTC"):
    '''
    Use this function to download and retrieve historical price data
    Returns a pandas dataframe of the data

    TODO: figure out which exchanges/coins will work
    '''
    filePath = downloadData(exchange, resolution, coin)
    data = pd.read_csv(filePath,header=1)
    return data

def downloadData(exchange="Bitfinex", resolution="day", coin="BTC"):
    '''
    This function shouldn't be used outside of this module
    Returns the file path of the downloaded csv file
    '''
    res = {"day":"d", "hour":"1hr", "minute":"2019_1min"}
    

    # check if it's already downloaded 
    fileName = f"{exchange}_{coin}USD_{res[resolution]}.csv"
    altfileName = f"{exchange.lower()}_{coin}USD_{res[resolution]}.csv"
    filePath = os.path.join(dataDirectory,fileName)
    if os.path.exists(filePath):
        return filePath

    # otherwise we download it
    urlBase = "http://www.cryptodatadownload.com/cdd/"
    fullUrl = urlBase + fileName
    altFullUrl = urlBase + altfileName
    print("Downloading from {}".format(fullUrl))

    # make sure there is a data folder
    if not os.path.isdir(dataDirectory):
        os.mkdir(dataDirectory)

    # confirm url exists
    try:
        with urllib.request.urlopen(fullUrl) as response:
            with open(filePath, 'wb') as outFile:
                print("Written")
                shutil.copyfileobj(response, outFile)
    except urllib.error.HTTPError:
        print("Downloading from {}".format(altFullUrl))
        with urllib.request.urlopen(altFullUrl) as response:
            with open(filePath, 'wb') as outFile:
                print("Written")
                shutil.copyfileobj(response, outFile)
    except urllib.error.URLError:
        print("Invalid URL, couldn't download data")
        raise


    return filePath
