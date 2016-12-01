#!/usr/bin/python3

"""
Doorstop GUI
"""


import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidget
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QIcon



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

        reqTree = QTreeWidget()
        reqView = QTreeWidget()

        mainSplit = QSplitter()
        mainSplit.addWidget(reqTree)
        mainSplit.addWidget(reqView)
        mainSplit.setStretchFactor(0,1)
        mainSplit.setStretchFactor(1,3)
        layout = QVBoxLayout()
        layout.addWidget(mainSplit)
        mainContainer.setLayout(layout)

        reqTree.setHeaderLabels(['Requirement Tree'])

        llrRoot = QTreeWidgetItem(reqTree)
        llrRoot.setText(0, 'LLR')

        llrChild1 = QTreeWidgetItem()
        llrChild1.setText(0, 'LLR0001')
        llrRoot.addChild(llrChild1)

        llrChild2 = QTreeWidgetItem()
        llrChild2.setText(0, 'LLR0002')
        llrRoot.addChild(llrChild2)

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
