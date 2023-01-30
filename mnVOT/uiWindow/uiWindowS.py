from PyQt5 import QtCore, QtGui, QtWidgets
from mnVOT.qtWidgets.WVideoFrame import WVideoFrame
from mnVOT.qtWidgets.WControlPanel import WControlPanel

class uiWindowS(object):
    def setupUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 480)
        # Central Widget Init
        self.centralwidget  = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.setup()
        # MainWindow Setup
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setup(self):
        self._setupCentralWidget( self.centralwidget )

    def _setupCentralWidget(self, widget : QtWidgets.QWidget ):
        aflag = QtCore.Qt.AlignmentFlag
        mlayout     = QtWidgets.QHBoxLayout()

        self.video = WVideoFrame( widget )
        mlayout.addWidget( self.video, alignment=aflag.AlignLeft | aflag.AlignTop )

        self.cpanel = WControlPanel( widget )
        mlayout.addWidget( self.cpanel, alignment=aflag.AlignLeft )

        widget.setLayout( mlayout )
        