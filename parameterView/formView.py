import sys, math
from PyQt5.QtWidgets import QApplication, QTableWidget, QLabel, QWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QPushButton, QDoubleSpinBox , QTabWidget, QSpinBox, QDateEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QDate
from datetime import date, datetime
from enum import Enum

class InputType(Enum):
    default = 0
    date = 1
    float = 2
    int = 3
    string = 4
    currency = 5
    percentage = 6


class FormView(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parameters = {} #parameters is a dictionary of names : (InputType,widgets)
        self.groupBox = QGroupBox('Bot Parameters')
        self.innerLayout = QVBoxLayout()
        self.layout = QVBoxLayout(self)
        self.parameterTable = QTableWidget(0,2)
        self.parameterTable.horizontalHeader().hide()
        self.parameterTable.verticalHeader().hide()
        self.parameterTable.horizontalHeader().setStretchLastSection(True)

        self.parameterTable.setColumnWidth(0,180)

    def clear(self):
        self.parameters = {} #parameters is a dictionary of names : (InputType,widgets)
        self.names = {} # dict of (name : widget), where widget is the Label


    def printParamters(self):
        for p in self.parameters:
            print(p + ':' + str(self.getWidgetValue(p)))

    def createForm(self):
        self.parameterTable.setRowCount(0)
        row = 0
        for p in self.parameters:
            self.parameterTable.insertRow(row)
            self.parameterTable.setItem(row, 0, self.names[p])
            self.parameterTable.setCellWidget(row, 1, self.parameters[p][1])
            row += 1

        self.innerLayout.addWidget(self.parameterTable)
        self.groupBox.setLayout(self.innerLayout)
        self.layout.addWidget(self.groupBox)
        self.setLayout(self.layout)

    def addParameter(self, name, parameterType, tooltip, defaultVal, minVal=None, maxVal=None):
        '''
            name is a string of the parameter
            parameterType of an enum of type ParameterType
            minVal, maxVal and defaultVal are doubles or integers.
            If the parameterType is of type Datetime then minVal, maxVal and defaultVal datetime

        '''
        if name in self.parameters:
            print('Parameter with that name already exists. Aborting')
            sys.exit()
        else:
            paramLabel = QTableWidgetItem(name)
            paramLabel.setTextAlignment(2)
            self.names[name] = paramLabel
            self.names[name].setToolTip(tooltip)


        if (parameterType == InputType.date):
            self._handleDate(name, parameterType, tooltip, defaultVal, minVal, maxVal)
        elif (parameterType == InputType.float):
            self._handleFloat(name, parameterType, tooltip, defaultVal, minVal, maxVal)
        elif (parameterType == InputType.int):
            self._handleInt(name, parameterType, tooltip, defaultVal, minVal, maxVal)
        elif (parameterType == InputType.string):
            self._handleString(name, parameterType, tooltip, defaultVal, minVal, maxVal)
        elif (parameterType == InputType.currency):
            self._handleFloat(name, parameterType, tooltip, defaultVal, minVal, maxVal)
            self.parameters[name][1].setPrefix('$')
        elif (parameterType == InputType.percentage):
            self._handleFloat(name, parameterType, tooltip, defaultVal, minVal, maxVal)
            self.parameters[name][1].setSuffix('%')

    def _handleDate(self, name, parameterType, tooltip, defaultVal, minVal=None, maxVal=None):
        if (minVal is not None):
            minDate = QDate.fromString(minVal, 'yyyy-MM-dd')
        if (maxVal is not None):
            maxDate = QDate.fromString(maxVal, 'yyyy-MM-dd')
        defaultDate = QDate.fromString(defaultVal.strftime('%Y-%m-%d'), 'yyyy-MM-dd')
        widget = QDateEdit(self.parameterTable)
        widget.setDate(defaultDate)
        widget.setToolTip(tooltip)
        widget.setCalendarPopup(True)
        self.parameters[name] =  [parameterType, widget]

        if (minVal is not None and maxVal is not None):
            self.parameters[name][1].setDateRange(minDate, maxDate)

    def _handleFloat(self, name, parameterType, tooltip, defaultVal, minVal=None, maxVal=None):
        self.parameters[name] = [parameterType, QDoubleSpinBox(self.parameterTable)]
        if maxVal is not None:
            self.parameters[name][1].setMaximum(maxVal)
        if minVal is not None:
            self.parameters[name][1].setMinimum(minVal)

        self.parameters[name][1].setMaximum(100000)
        self.parameters[name][1].setMinimum(0)
        self.parameters[name][1].setValue(defaultVal)
        self.parameters[name][1].setToolTip(tooltip)

    def _handleInt(self, name, parameterType, tooltip, defaultVal, minVal=None, maxVal=None):
        self.parameters[name] = [parameterType, QSpinBox(self.parameterTable)]
        if maxVal is not None:
            self.parameters[name][1].setMaximum(maxVal)
        if minVal is not None:
            self.parameters[name][1].setMinimum(minVal)
        self.parameters[name][1].setMaximum(100000)
        self.parameters[name][1].setMinimum(0)
        self.parameters[name][1].setValue(defaultVal)
        self.parameters[name][1].setToolTip(tooltip)

    def _handleString(self, name, parameterType, tooltip, defaultVal, minVal=None, maxVal=None):
        widget = QLabel(defaultVal)
        widget.setToolTip(tooltip)
        self.parameters[name] = [parameterType, widget]

    def getWidgetValue(self, name):
        '''
            return the value from the widget associated with "name"
        '''

        if name in self.parameters:
            varType =  self.parameters[name][0]
            if (varType == InputType.date):
                return datetime.combine(self.parameters[name][1].date().toPyDate(), datetime.min.time())
            elif (varType == InputType.int):
                return self.parameters[name][1].value()
            elif varType == InputType.float or varType == InputType.currency or varType == InputType.percentage:
                return float(self.parameters[name][1].value())
            elif varType == InputType.string:
                return str(self.parameters[name][1].text())
            else:
                print('Parameter type is not valid. Aborting')
                sys.exit()
        else:
            print('Parameter with the name "' + name + '" does not exist. Aborting')
            sys.exit()



