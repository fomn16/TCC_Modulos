import sys
sys.path.insert(1, '../../')
from Modules.Shared.Params import Params
from Modules.Shared.helper import *
from Modules.Augmentation.WUNETCGAN.WUNETCGAN import WUNETCGAN

class WUNETCGAN_MNIST(WUNETCGAN):
    def loadConstants(self):
        self.genWidth = 7
        self.genHeight = 7

        approximateNoiseDim = 100
        self.noiseDepth = int(np.ceil(approximateNoiseDim/(self.genWidth*self.genHeight)))
        self.noiseDim = self.genWidth*self.genHeight*self.noiseDepth

        self.initLr = 8e-5
        self.leakyReluAlpha = 0.2
        self.dropoutParam = 0.02
        self.batchNormMomentum = 0.8
        self.batchNormEpsilon = 2e-4

        self.clipValue = 0.01

        self.ganEpochs = 100
        self.batchSize = 128
        self.extraDiscEpochs = 5
        self.generator = None
        self.discriminator = None
        self.gan = None 

        self.uNetChannels = 32
        self.uNetRatio = 1.5
        self.uNetBlocks = 2
        self.uNetDropout = False
        self.uNetBatchNorm = True
    
    def genUpscale(self, model):
        model = self.TransposedBlock(model, 1, 8)
        model = self.TransposedBlock(model, 1, 4)
        return model
    
    def discDownscale(self, model):
        model = self.ResidualBlock(model, 1, 32, stride=2)
        model = self.ResidualBlock(model, 1, 32, stride=2)
        model = self.ResidualBlock(model, 1, 32)
        return model