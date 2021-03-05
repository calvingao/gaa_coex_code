# dummy driver for nlcd
import numpy as np

class NlcdDriver:
    def GetLandCoverCodes(self, lat, lon):
        size = min(len(lat), len(lon))
        codes = np.random.choice([21, 22, 23, 24, 11], size, p=[0.1, 0.2, 0.2, 0.45, 0.05])
        return codes

