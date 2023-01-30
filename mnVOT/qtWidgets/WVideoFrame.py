from PyQt5 import QtWidgets, QtGui, QtCore
from mnVOT.cvEngine.DTracker import DTracker
from mnVOT.cvEngine.DRectangle import DRectangle
from mnVOT.cvEngine.DMouseTracker import DMouseTracker
from mnVOT.utils.UVideoCap import UVideoCap
import cv2
import numpy as np

node_list = [
    ( 1,2 ),
    ( 2,3 ),
    ( 3,4 ),
    ( 4,1 ),
]

class WVideoFrame( QtWidgets.QLabel ):
    STATE_NODES = 0
    STATE_BOXES = 1
    STATE_READY = 2

    def __init__( self, parent=None ):
        super( QtWidgets.QLabel, self ).__init__( parent=parent )
        self.setObjectName( "VideoFrame" )
        self.setMouseCallbacks()
        #self.mt = DMouseTracker( 5 )
        self.live_idx = 0
        self.rec_file = ""
        self.fsize = ( 640, 480 )
        self.fscale = ( 1, 1 )
        self.mode = UVideoCap.STATE_NULL
        self.gen_cover()
        self.gen = self.run()
        self.update()
        self.resize( self.sizeHint() )
    
    def gen_cover( self ):
        frame = np.zeros( [ self.fsize[1], self.fsize[0], 3 ] )
        self.cover = QtGui.QImage( frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888 )

    def update( self ):
        frame = next( self.gen )
        if not isinstance( frame, type( None ) ):
            frame = cv2.resize( frame, self.fsize )
            imageQt = QtGui.QImage( frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888 )
        else:
            imageQt = self.cover
        self.setPixmap( QtGui.QPixmap.fromImage( imageQt ) )
    
    def run( self ):
        self._source = None
        while True:
            if self.mode == UVideoCap.STATE_LIVE:
                yield self._get_live()
            elif self.mode == UVideoCap.STATE_REC:
                yield self._get_record()
            else:
                yield self._get_null()

    def _get_null( self ):
        if not isinstance( self._source, type( None ) ):
            self._source.close()
            self._source = None
        return None

    def _get_record( self ):
        def set_src():
            if self.rec_file:
                capture = cv2.VideoCapture( self.rec_file )
                self._source = UVideoCap( capture, self._draw, self.fsize, UVideoCap.STATE_REC )
                self.fscale = self._source.scale
                return False
            self._source = None
            self.mode = UVideoCap.STATE_NULL
            return True
        if isinstance( self._source, type( None ) ):
            if set_src(): return None
        elif self._source.type != UVideoCap.STATE_REC:
            self._source.close()
            if set_src(): return None
        return self._source.next()

    def _get_live( self ):
        def set_src():
            capture = cv2.VideoCapture( self.live_idx, cv2.CAP_DSHOW )
            self._source = UVideoCap( capture, self._draw, self.fsize, UVideoCap.STATE_LIVE )
            self.fscale = self._source.scale
        if isinstance( self._source, type( None ) ):
            set_src()
        elif self._source.type != UVideoCap.STATE_LIVE:
            self._source.close()
            set_src()
        return self._source.next()

    def stop( self ):
        self._get_null()
        self.mode = UVideoCap.STATE_NULL
        self.setMouseCallbacks()

    def setMouseCallbacks( self ):
        self.mt = None
        self.mc = None
        self.nodes = None
        self.tracker = None
        self.node_list = []
        self.line_list = []
        self._pos    = None
        self._flagL  = False
        self._states = self._genState()
        self._state  = next( self._states )
        self.setMouseTracking( True )

    def _getPos( self, e : QtGui.QMouseEvent ):
        pos = e.pos()
        return self._scale( pos.x(), pos.y() )

    def _genState( self ):
        yield WVideoFrame.STATE_NODES
        yield WVideoFrame.STATE_BOXES
        while True: yield WVideoFrame.STATE_READY

    def _getMt( self ):
        if isinstance( self.mt, type(None) ):
            size = len( self.node_list )
            self.mt = DMouseTracker( size if size else 1, False )
        return self.mt
    
    def _getMc( self ):
        if isinstance( self.nodes, type(None) ):
            self.nodes = self.mt.get( self.line_list )
            self.mc = DMouseTracker( self.nodes.size(), False )
        return self.mc

    def _getTracker( self, frame ):
        if isinstance( self.tracker, type(None) ):
            self.tracker = DTracker( frame, self.nodes, self.mc.get_rects() )
        return self.tracker

    def _mouse_callback( self, *args ):
        if self._state == self.STATE_NODES:
            self._getMt().mouse_callback( *args )
        elif self._state == self.STATE_BOXES:
            self._getMc().mouse_callback( *args )
        elif self._state == self.STATE_READY:
            pass

    def _draw( self, image, *args ):
        if self._state == self.STATE_NODES:
            self._getMt().draw( image, *args )
        elif self._state == self.STATE_BOXES:
            self._getMt().draw( image, *args )
            self._getMc().draw( image, *args )
        elif self._state == self.STATE_READY:
            self._getTracker( image ).update( image )
            self.nodes.update()
            self.nodes.draw( image, *args )

    def _scale( self, x, y ):
        return int( x * self.fscale[0] ), int( y * self.fscale[1] )

    def mouseMoveEvent( self, e : QtGui.QMouseEvent ):
        if self._flagL:
            pos = self._getPos( e )
            self._mouse_callback( DRectangle.EVENT_LHOVER, *pos )
        
    def mousePressEvent( self, e : QtGui.QMouseEvent ):
        flagL = e.buttons() & QtCore.Qt.MouseButton.LeftButton
        flagC = e.buttons() & QtCore.Qt.MouseButton.MiddleButton
        if flagL:
            if not self._flagL:
                self._flagL = True
                pos = self._getPos( e )
                self._mouse_callback( DRectangle.EVENT_LPRESS, *pos )
        if flagC:
            self._state = next( self._states )

    def mouseReleaseEvent( self, e : QtGui.QMouseEvent ):
        flagL = e.buttons() & QtCore.Qt.MouseButton.LeftButton
        if not flagL:
            if self._flagL:
                self._flagL = False
                pos = self._getPos( e )
                self._mouse_callback( DRectangle.EVENT_LRELEASE, *pos )