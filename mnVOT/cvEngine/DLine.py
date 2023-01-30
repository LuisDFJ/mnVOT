from mnVOT.cvEngine.DPoint import DPoint
from mnVOT.cvEngine.DTwoPointAbstract import DTwoPointAbstract
import cv2 as cv

class DLine (DTwoPointAbstract):
    MAX_ENUM = 100
    __enumarator = ( i for i in range( 1, MAX_ENUM + 1 ) )
    def __init__(self, pa: DPoint = None, pb: DPoint = None):
        super().__init__(pa, pb)
        self.n = self.enum( self.__enumarator )
        self.color = ( 0, 255, 0 )

    def draw(self, img, sx, sy):
        if bool( self ):
            cv.line( img, tuple( self.pa ), tuple( self.pb ), self.color, int( sx + sy ) )