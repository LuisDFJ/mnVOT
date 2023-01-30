from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from mnVOT.uiWindow.uiWindow import uiWindowS
from mnVOT.utils.UVideoCap import UVideoCap

class uiWindow( QMainWindow, uiWindowS ):
    def __init__( self, parent=None ):
        QMainWindow.__init__(self, parent=parent)
        self.setupUI(self)
        fps_v = 30
        
        self.set_callbacks()

        self.timer_video = QTimer(self)
        self.timer_video.setInterval( int( 1000 / fps_v ) )
        self.timer_video.timeout.connect( self.video.update )
        
        self.timer_video.start()

    def set_callbacks(self):
        self.cpanel.start.clicked.connect( self.switch_mode )
        self.cpanel.stop.clicked.connect( self.stop_cap )

    def stop_cap(self):
        #self.video.mode = UVideoCap.STATE_NULL
        self.video.stop()

    def switch_mode(self):
        self.video.live_idx = self.cpanel.live_idx
        self.video.rec_file = self.cpanel.rec_file
        self.video.node_list = self.cpanel.nodes
        self.video.line_list = self.cpanel.lines
        if self.cpanel.liveflag:
            self.video.mode = UVideoCap.STATE_LIVE
        else:
            self.video.mode = UVideoCap.STATE_REC

    def closeEvent(self, e):
        self.timer_video.stop()
        print( "Closing Window" )