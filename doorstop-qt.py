#!/usr/bin/python3

"""
Doorstop GUI
"""


import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidget
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QIcon



class ReqTree(QTreeWidget):

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(['Requirement Tree'])

    def addRootItem(self, index, text):
        rootItem = QTreeWidgetItem()
        rootItem.setText(0, str(index) + ' ' + text)
        self.insertTopLevelItem(index-1, rootItem)

    def addChildItem(self, parent, finalIndex, index, text):
        childItem = QTreeWidgetItem()
        childItem.setText(0, str(index) + ' ' + text)
        parent.insertChild(finalIndex-1, childItem)

    def addItem(self, index, text):
        print('additem ' + str(index))
        indexArray = [int(x) for x in index.split('.') if x.strip()]
        if not indexArray:
            raise ValueError('Invalid item index: empty')
        if len(indexArray) == 1:
            self.addRootItem(indexArray[0], text)
        else:
            finalIndex = indexArray[-1]
            subIndex = indexArray[:-1]
            self.addChildItem(self.findParent(subIndex), finalIndex, index, text)

    def findParent(self, subIndex):
        if not subIndex:
            raise ValueError('Invalid item index: empty')
        parent = self.topLevelItem(subIndex[0]-1)
        if not parent:
            print('root not found ' + str(subIndex[0]-1))
        while (parent and subIndex[1:]):
            del subIndex[0]
            parent = parent.child(subIndex[0]-1)
        if not parent:
            raise ValueError('Invalid item index: parent not found')
        return parent



class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.startUI(app)


    def startUI(self, app):
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Requirements')

        saveAction = QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Requirements')

        exportAction = QAction('&Export', self)
        exportAction.setShortcut('Ctrl+E')
        exportAction.setStatusTip('Export Requirements')

        quitAction = QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit')
        quitAction.triggered.connect(app.quit)

        aboutAction = QAction('About', self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exportAction)
        fileMenu.addSeparator()
        fileMenu.addAction(quitAction)

        helpMenu = menuBar.addMenu('Help')
        helpMenu.addAction(aboutAction)

        mainContainer = QWidget()

        self.setCentralWidget(mainContainer)

        reqTree = ReqTree()
        reqView = QTreeWidget()

        mainSplit = QSplitter()
        mainSplit.addWidget(reqTree)
        mainSplit.addWidget(reqView)
        mainSplit.setStretchFactor(0,1)
        mainSplit.setStretchFactor(1,3)
        layout = QVBoxLayout()
        layout.addWidget(mainSplit)
        mainContainer.setLayout(layout)

        test1 = '1.1'
        test2 = str(test1)
        test = str("1.1")

        reqTree.addItem('1', 'Hardware')
        reqTree.addItem('1.1', 'AXI')
        reqTree.addItem('1.2', 'DMA')
        reqTree.addItem('1.3', 'SERDES')
        reqTree.addItem('2', 'Software')
        reqTree.addItem('1.1.1', 'req1')
        reqTree.addItem('1.1.2', 'req2')
        reqTree.addItem('1.1.3', 'req3')

        sg = app.desktop().screenGeometry()
        wmax = sg.width()
        hmax = sg.height()
        self.setGeometry(wmax/8, hmax/8, (wmax*3)/4, (hmax*3)/4)
        self.setWindowTitle('Doorstop')
        self.statusBar().showMessage('No Requirements Loaded')
        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(app)
    sys.exit(app.exec_())
