import numpy as np
import math

class Compass:

    rawX = []
    rawY = []
    rawZ = []

    ignoreXYZ = ''

    scale_D1 = 0
    scale_D2 = 0
    origin_D1 = 0
    origin_D2 = 0

    # def __init__(self):
    #    """Clear the calibration data structure of the compass"""

    def get_heading(self, mx, my, mz):
        """Translate a raw compass reading into 360 Degree value"""
        assert self.ignoreXYZ

        if self.ignoreXYZ == 'X':
            d1 = float((my - self.origin_D1)) / float(self.scale_D1)
            d2 = float((mz - self.origin_D2)) / float(self.scale_D2)
        if self.ignoreXYZ == 'Y':
            d1 = float((mx - self.origin_D1)) / float(self.scale_D1)
            d2 = float((mz - self.origin_D2)) / float(self.scale_D2)
        if self.ignoreXYZ == 'Z':
            d1 = float((mx - self.origin_D1)) / float(self.scale_D1)
            d2 = float((my - self.origin_D2)) / float(self.scale_D2)

        return int(180 + 180/math.pi * math.atan2(d2,d1))

    def set_north(self, mx, my, mz):
        """Define current raw compass reading as north"""
        pass

    def push_calibration_value(self, mx, my, mz):
        """ Pass a raw compass reading into the calibration data structure"""
        self.rawX.append(mx)
        self.rawY.append(my)
        self.rawZ.append(mz)

    def calibrate_compass(self):
        """ Perform a calibration using raw compass readings received so far"""
        np_rawX = np.array(self.rawX,dtype=int)
        np_rawY = np.array(self.rawY,dtype=int)
        np_rawZ = np.array(self.rawZ,dtype=int)

        rangeX = np_rawX.max() - np_rawX.min()
        rangeY = np_rawY.max() - np_rawY.min()
        rangeZ = np_rawZ.max() - np_rawZ.min()

#        print(np_rawX[0])
#        print(np_rawY[100])
#        print(np_rawZ[200])
#        print("range: %d %d %d" % (rangeX, rangeY, rangeZ))

        if  min(rangeX,rangeY,rangeZ) == rangeX:
            planarD1 = np_rawY
            planarD2 = np_rawZ
            self.ignoreXYZ = 'X'
        if  min(rangeX,rangeY,rangeZ) == rangeY:
            planarD1 = np_rawX
            planarD2 = np_rawZ
            self.ignoreXYZ = 'Y'
        if  min(rangeX,rangeY,rangeZ) == rangeZ:
            planarD1 = np_rawX
            planarD2 = np_rawY
            self.ignoreXYZ = 'Z'

        self.scale_D1 = int((planarD1.max() - planarD1.min())/2)
        self.scale_D2 = int((planarD2.max() - planarD2.min())/2)

        self.origin_D1 = self.scale_D1 + planarD1.min()
        self.origin_D2 = self.scale_D2 + planarD2.min()

#        print("D1 origin: %d, scale %d" % (self.origin_D1, self.scale_D1))
#        print("D2 origin: %d, scale %d" % (self.origin_D2, self.scale_D2))
        
