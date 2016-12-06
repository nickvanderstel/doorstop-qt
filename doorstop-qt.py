#!/usr/bin/python3

"""
Doorstop PyQt GUI
"""


import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidget, QFileDialog
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QTableWidget
from PyQt5.QtWidgets import QTabWidget, QStackedWidget
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

    def __init__(self, doc=None):
        super().__init__()
        self.header().hide() # we don't need the header
        if doc:
            self.loadDoc(doc)

    def loadDoc(self, doc):
        for item in doc.items:
            self.addItem(item.level, item.text)

    def addItem(self, level, text):
        # strip off trailing zero
        index = level.value[:-1] if level.value[-1] == 0 else level.value
        if not index:
            raise ValueError('Invalid item index: empty')
        if (len(index) == 1) or (len(index) == 2 and index[1] == 0):
            self._addRootItem(index[0], text)
        else:
            finalIndex = index[-1]
            subIndex = index[:-1]
            self._addChildItem(self._findParent(subIndex), finalIndex, str(level), text)

    def _addRootItem(self, index, text):
        rootItem = QTreeWidgetItem()
        rootItem.setText(0, str(index) + ' ' + text)
        self.insertTopLevelItem(index-1, rootItem)

    def _addChildItem(self, parent, finalIndex, index, text):
        childItem = QTreeWidgetItem()
        childItem.setText(0, str(index) + ' ' + text)
        parent.insertChild(finalIndex-1, childItem)

    def _findParent(self, subIndex):
        if not subIndex:
            raise ValueError('Invalid item index: empty')
        parent = self.topLevelItem(subIndex[0]-1)
        if not parent:
            print('root not found ' + str(subIndex[0]-1))
        while (parent and subIndex[1:]):
            parent = parent.child(subIndex[1]-1)
            subIndex = subIndex[1:]
        if not parent:
            raise ValueError('Invalid item index: parent not found')
        return parent




class DocTable(QTableWidget):

    def __init__(self, doc=None):
        super().__init__()
        if doc:
            self.loadDoc(doc)

    def loadDoc(self, doc):
        #self.setColumnCount(
        self.setRowCount(len(doc))
        for item in doc.items:
            self._addItem(item)

    def _addItem(self, item):
        pass




class TreeStack(QStackedWidget):

    def __init__(self):
        super().__init__()
        self._docList = {}

    def addDoc(self, doc):
        newDoc = ReqTree(doc)
        self._docList[doc.prefix] = newDoc
        self.addWidget(newDoc)

    def makeDocActive(self, doc):
        self.setCurrentWidget(self._docList[doc.prefix])



class DocStack(QStackedWidget):

    def __init__(self):
        super().__init__()
        self._docList = {}

    def addDoc(self, doc):
        newDoc = DocTable(doc)
        self._docList[doc.prefix] = newDoc
        self.addWidget(newDoc)

    def makeDocActive(self, doc):
        self.setCurrentWidget(self._docList[doc.prefix])





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
        self._docTree.itemActivated.connect(self._docSelected)

        # Requirement tree view widget
        self._reqStack = TreeStack()
        reqTreeWindow = QWidget()
        reqTreeLayout = QVBoxLayout()
        reqTreeLayout.addWidget(self._reqStack)
        reqTreeWindow.setLayout(reqTreeLayout)

        # splitter for the tree views
        treeSplit = QSplitter()
        treeSplit.setOrientation(Qt.Vertical)
        treeSplit.addWidget(docTreeWindow)
        treeSplit.addWidget(reqTreeWindow)
        treeSplit.setStretchFactor(0,1)
        treeSplit.setStretchFactor(1,9)


        """
        # Tab widget to hold the tree views
        self._tabs = QTabWidget()
        self._tabs.addTab(docTreeWindow, 'Documents')
        self._tabs.addTab(reqTreeWindow, 'Requirements')
        """


        # Requirement table view widget
        self._reqView = DocStack()


        mainSplit = QSplitter()
        #mainSplit.addWidget(self._tabs)
        mainSplit.addWidget(treeSplit)
        mainSplit.addWidget(self._reqView)
        mainSplit.setStretchFactor(0,1)
        mainSplit.setStretchFactor(1,3)
        layout = QVBoxLayout()
        layout.addWidget(mainSplit)
        mainContainer.setLayout(layout)

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
                self._reqStack.addDoc(doc)
                self._reqView.addDoc(doc)

    def _docSelected(self, item, col):
        self._reqStack.makeDocActive(item.doc)
        self._reqView.makeDocActive(item.doc)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(app)
    sys.exit(app.exec_())
