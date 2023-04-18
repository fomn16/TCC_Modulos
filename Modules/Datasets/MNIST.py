import sys
sys.path.insert(1, '../../')
from Modules.Shared.helper import *
from Modules.Shared.Params import Params
from Modules.Datasets.Dataset import Dataset

class MNIST(Dataset):
    def __init__(self, params:Params):
        self.params = params
        self.loadParams()

        self.name = params.datasetName
        self.dataset, self.info = tfds.load(name = params.datasetName, with_info=True, as_supervised=True, data_dir=params.dataDir)

        self.trainInstances = self.info.splits['train'].num_examples
        self.testInstances = self.info.splits['test'].num_examples
        self.totalInstances = self.trainInstances + self.testInstances
        self.n_instances_fold = int(np.floor(self.totalInstances/self.params.kFold))
    
    def loadParams(self):
        self.params.datasetName = 'mnist'
        self.params.nClasses = 10
        self.params.imgChannels = 1
        self.params.imgWidth = 28
        self.params.imgHeight = 28
    
    def getTrainData(self, start, end):
        return self._getFromDatasetLL(start, end)

    def getTestData(self, start, end):
        return self._getFromDatasetLL(start, end, True)
    
    def getAllTrainData(self):
        return self._getFromDatasetLL(0, self.trainInstances-1)
    
    def getAllTestData(self):
        return self._getFromDatasetLL(0, self.testInstances-1, True)
    
    #carrega instancias do dataset usando lazy loading dos dados
    def _getFromDatasetLL(self, start, end, test=False):
        if(test):
            start += self.params.currentFold*self.n_instances_fold
            end += self.params.currentFold*self.n_instances_fold
        imgs = None
        lbls = None
        if(end < self.trainInstances):
            imgs, lbls = loadIntoArrayLL('train', self.dataset, self.params.nClasses, start, end, 0, 1)
        elif (start >= self.trainInstances):
            imgs, lbls = loadIntoArrayLL('test', self.dataset, self.params.nClasses, start - self.trainInstances, end - self.trainInstances, 0, 1)
        else:
            imgs1, lbls1 = loadIntoArrayLL('train', self.dataset, self.params.nClasses, start, self.trainInstances - 1, 0, 1)
            imgs2, lbls2 = loadIntoArrayLL('test', self.dataset, self.params.nClasses, 0, end - self.trainInstances, 0, 1)
            imgs = np.concatenate((imgs1, imgs2))
            lbls = np.concatenate((lbls1, lbls2))
            del imgs1, imgs2, lbls1, lbls2
        return imgs, lbls