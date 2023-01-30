import cv2

class UVideoCap:
    STATE_NULL = 0
    STATE_LIVE = 1
    STATE_REC  = 2
    def __init__(self, capture, draw_callback, fsize, ctype : int = 0 ) -> None:
        self.active = True
        self._draw = draw_callback
        self.capture = capture
        self.scale = self.get_scale( capture, fsize )
        self.type = ctype
        self.gen = self.run()

    def get_scale( self, capture, fsize ):
        size = ( capture.get( cv2.CAP_PROP_FRAME_WIDTH ),
                 capture.get( cv2.CAP_PROP_FRAME_HEIGHT) )
        return size[0] / fsize[0], size[1] / fsize[1]

    def run( self ):
        while True:
            if self.active:
                ret, frame = self.capture.read()
                if ret:
                    image   = cv2.flip( cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1 )
                    self._draw( image, *self.scale )
                    yield image
                else:
                    yield None
            else:
                yield None

    def next( self ):
        return next( self.gen )
    
    def close( self ):
        self.active = False
        self.capture.release()