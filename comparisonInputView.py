from PyQt5.QtCore import pyqtSlot, QDate
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
QDialogButtonBox, QDateEdit, QLabel, QVBoxLayout)

import sys

class ComparisonInputDialog(QDialog):
    def __init__(self, parent = None):
        super(ComparisonInputDialog, self).__init__(parent)
        self.resize(200,300)

        self.selectedCoin = 'BTC'
        self.coinList = ["BTC", "ETH", "LTC","ZEC"]

        self.coinDropdown = QComboBox()
        self.setStyleSheet('''
            QComboBox::item:checked {
                font-weight: bold;
                height: 16px;
            }
        ''')
        for coin in self.coinList:
            self.coinDropdown.addItem(coin)

        self.startDate = QDateEdit(self)
        self.startDate.setCalendarPopup(True)
        self.endDate = QDateEdit(self)
        self.endDate.setCalendarPopup(True)
        self.startDate.setDate(QDate(2017,1,1))
        self.endDate.setDate(QDate(2018,1,1))

        mainLayout = QVBoxLayout()
        self.label1 = QLabel("Coin: ")
        mainLayout.addWidget(self.label1)
        mainLayout.addWidget(self.coinDropdown)
        self.label2 = QLabel("Start Date: ")
        mainLayout.addWidget(self.label2)
        mainLayout.addWidget(self.startDate)
        self.label3 = QLabel("End Date: ")
        mainLayout.addWidget(self.label3)
        mainLayout.addWidget(self.endDate)

        self.okButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.okButton.accepted.connect(self.accept)
        self.okButton.rejected.connect(self.reject)
        mainLayout.addWidget(self.okButton)
        self.setLayout(mainLayout)

        self.date1 = self.startDate.dateTime().toPyDateTime()
        self.date2 = self.endDate.dateTime().toPyDateTime()
        self.startDate.dateTimeChanged.connect(self.startChange)
        self.endDate.dateTimeChanged.connect(self.endChange)
        self.coinDropdown.currentTextChanged.connect(self.coinChange)
    def startChange(self, date):
        self.date1 = date.toPyDateTime()
    def endChange(self, date):
        self.date2 = date.toPyDateTime()
    def coinChange(self, coin):
        self.selectedCoin = self.coinDropdown.currentText()
    @staticmethod
    def getUserInput(parent = None):
        dialog = ComparisonInputDialog(parent)
        result = dialog.exec_()
        startDate = dialog.date1
        endDate = dialog.date2
        coin = dialog.selectedCoin
        return (startDate, endDate, coin, result == QDialog.Accepted)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = ComparisonInputDialog()
    sys.exit(dialog.exec_())
