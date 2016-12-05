#!/usr/bin/python3

"""
Doorstop PyQt GUI
"""


import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidget, QFileDialog
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QTableWidget
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtGui import QIcon

from doorstop.core import builder



class DocTreeItem(QTreeWidgetItem):
    def __init__(self, doc):
        super().__init__()
        self.doc = doc

class DocTree(QTreeWidget):

    def __init__(self):
        super().__init__()
        self._docList = []
        self.header().hide() # we don't need the header
        #self.setHeaderLabels(['Requirement Tree'])

    def addItem(self, doc):
        if doc.parent is None:
            self._addRootItem(doc)
        else:
            self._addChildItem(self._findParent(doc), doc)

    def _addRootItem(self, doc):
        rootItem = DocTreeItem(doc)
        rootItem.setText(0, doc.prefix)
        self.addTopLevelItem(rootItem)
        self._docList.append(rootItem)

    def _addChildItem(self, parent, doc):
        childItem = DocTreeItem(doc)
        childItem.setText(0, doc.prefix)
        if parent is None:
            raise ValueError('Can\'t find document parent for {}'.format(doc.prefix))
        parent.addChild(childItem)
        parent.setExpanded(True) # TODO: make this optional?
        self._docList.append(childItem)

    def _findParent(self, child):
        for parent in self._docList:
            if parent.doc.prefix == child.parent:
                return parent
        return None



class ReqTree(QTreeWidget):

    def __init__(self):
        super().__init__()
        self.header().hide() # we don't need the header

    def addRootItem(self, index, text):
        rootItem = QTreeWidgetItem()
        rootItem.setText(0, str(index) + ' ' + text)
        self.insertTopLevelItem(index-1, rootItem)

    def addChildItem(self, parent, finalIndex, index, text):
        childItem = QTreeWidgetItem()
        childItem.setText(0, str(index) + ' ' + text)
        parent.insertChild(finalIndex-1, childItem)

    def addItem(self, index, text):
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
        self._startUI(app)
        self._tree = None


    def _startUI(self, app):

        # Create the menubar
        openAction = QAction('&Open Project', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Project')
        openAction.triggered.connect(self._openProject)

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


        # Parent container to hold everything in the main window
        mainContainer = QWidget()
        self.setCentralWidget(mainContainer)

        # Document tree view widget
        self._docTree = DocTree()
        docTreeWindow = QWidget()
        docTreeLayout = QVBoxLayout()
        docTreeLayout.addWidget(self._docTree)
        docTreeWindow.setLayout(docTreeLayout)

        # Requirement tree view widget
        self._reqTree = ReqTree()
        reqTreeWindow = QWidget()
        reqTreeLayout = QVBoxLayout()
        reqTreeLayout.addWidget(self._reqTree)
        reqTreeWindow.setLayout(reqTreeLayout)

        # Tab widget to hold the tree views
        self._tabs = QTabWidget()
        self._tabs.addTab(docTreeWindow, 'Documents')
        self._tabs.addTab(reqTreeWindow, 'Requirements')


        # Requirement table view widget
        reqView = QTableWidget()


        mainSplit = QSplitter()
        mainSplit.addWidget(self._tabs)
        mainSplit.addWidget(reqView)
        mainSplit.setStretchFactor(0,1)
        mainSplit.setStretchFactor(1,3)
        layout = QVBoxLayout()
        layout.addWidget(mainSplit)
        mainContainer.setLayout(layout)

        test1 = '1.1'
        test2 = str(test1)
        test = str("1.1")

        self._reqTree.addItem('1', 'Hardware')
        self._reqTree.addItem('1.1', 'AXI')
        self._reqTree.addItem('1.2', 'DMA')
        self._reqTree.addItem('1.3', 'SERDES')
        self._reqTree.addItem('2', 'Software')
        self._reqTree.addItem('1.1.1', 'req1')
        self._reqTree.addItem('1.1.2', 'req2')
        self._reqTree.addItem('1.1.3', 'req3')

        sg = app.desktop().screenGeometry()
        wmax = sg.width()
        hmax = sg.height()
        self.setGeometry(wmax/8, hmax/8, (wmax*3)/4, (hmax*3)/4)
        self.setWindowTitle('Doorstop')
        self.statusBar().showMessage('No Requirements Loaded')
        self.show()

    def _openProject(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOptions(QFileDialog.ShowDirsOnly)
        if dialog.exec():
            # TODO: this returns a list... should give user an error if they select multiple
            dir = dialog.selectedFiles()[0]
            self._tree = builder.build(root=dir)
            for doc in self._tree:
                self._docTree.addItem(doc)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(app)
    sys.exit(app.exec_())
