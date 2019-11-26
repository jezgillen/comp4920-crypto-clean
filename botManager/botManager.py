import sys
import os
import importlib, json
from dateutil.parser import parse
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtWidgets import QMessageBox
from shutil import copyfile



#from bots import bots

class BotManager():
    def __init__(self, parent):
        self._botListPath = os.path.abspath('savedBots/')
        self._botListFileSetup()
        self._botListFile = os.path.abspath('savedBots/botlistfile')
        self._botlist = {}
        self._loadBots()
        self.parent = parent


    def getBotList(self):
        return self._botlist

    def getBotNames(self):
        return self._botlist.keys()

    def _botListFileSetup(self):
        if not os.path.exists(self._botListPath):
            os.makedirs(self._botListPath)


    def _checkBotExists(self, botfilename):
        botPath = os.path.join(self._botListPath, botfilename)
        if os.path.exists(botPath):
            return True
        return False

    def _showErrorMessage(self, msg):
        errorMsg = QMessageBox()
        errorMsg.setIcon(QMessageBox.Critical)
        errorMsg.setText(msg)
        errorMsg.setWindowTitle("Error")
        errorMsg.setStandardButtons(QMessageBox.Ok)
        errorMsg.exec_()


    def loadBotFromFile(self):
        root = tk.Tk()
        root.withdraw()
        filePath = None
        filePath = filedialog.askopenfilename()
        if(filePath == ()):
            return None
        elif filePath.endswith('.json'):
            filename = os.path.basename(filePath)
            if self._checkBotExists(filename):
                self._showErrorMessage("Bot with that filename already exists")
            else:
                newPath = os.path.join(self._botListPath, filename)
                copyfile(filePath, newPath)
                alias = os.path.splitext(filename)[0]
                #print(alias)
                newBot = self.loadBot(alias)
                self.saveBot(alias, newBot, False)
                return alias

        elif filePath != '':
            self._showErrorMessage("Invalid bot file")
            return None
        else:
            return None



    def _loadBots(self):
        #botlistfile should have a list of bot alaises
        #bot aliases must be unique
        if (os.path.exists(self._botListFile)):
            with open(self._botListFile, 'r+') as f:
                line = f.readline()
                while line:
                    line = line.strip("\n")
                    self._botlist[line] = None
                    self._botlist[line] = self.loadBot(line)
                    line = f.readline()                     #line should contain the alias of the bots

    def loadBot(self, alias):
        alias = str(alias)
        botPath = os.path.join(self._botListPath, str(alias.strip("\n"))+".json")
        if (os.path.exists(botPath)):
            data = None
            with open(botPath, 'r') as f:
                data = json.load(f)
            f.close()
            bot = self._createBot(data['Bot Type'])
            bot.setAlias(alias)
            bot.load()
            return bot

    def _createBot(self, name):
        module = importlib.import_module('bots')
        try:
            class_ = getattr(module, name)
        except AttributeError:
            print(f"There are saved bots of type '{name}', which no longer exists. Please delete those saved bot files")
            exit()
        bot = class_()
        return bot

    def saveBot(self, alias, bot, withSetup=True):
        if alias in self._botlist:
            print('Bot with name ' + alias + ' exists. Overwrite')
        else:
            with open(self._botListFile, 'a+') as f:
                f.write(alias+'\n')
            f.close()

        if withSetup:
            self.parent.setupBot(bot)
        bot.setAlias(alias)
        bot.save()
        self._botlist[alias] = bot

    def deleteBot(self, alias):
        botPath = os.path.join(self._botListPath, str(alias.strip("\n"))+".json")
        if (os.path.exists(botPath)):
            self._botlist.pop(alias)
            aliasToRemove = alias+'\n'
            os.remove(botPath)
            with open(self._botListFile, 'r') as f:
                lines = f.readlines()
            f.close()
            with open(self._botListFile, 'w') as f:
                for l in lines:
                    if l != aliasToRemove:
                        f.write(l)
            f.close()



    def _isDate(self, string, fuzzy=False):
        if not isinstance(string, str):
            return False
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

