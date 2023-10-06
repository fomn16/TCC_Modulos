import sys
sys.path.insert(1, '../../')
from Modules.Shared.helper import *
from Modules.Shared.Params import Params
from Modules.Datasets.Dataset import Dataset

class MNIST_UNBALANCED(Dataset):
    def __init__(self, params:Params):
        self.minClassInstances = 250
        self.params = params
        self.loadParams()

        self.name = params.datasetName
        self.dataset, self.info = tfds.load(name = params.datasetName, with_info=True, as_supervised=True, data_dir=params.dataDir)

        #numero de instancias nos splits de treinamento e teste no dataset original
        self.trainInstancesDataset = self.info.splits['train'].num_examples
        self.testInstancesDataset = self.info.splits['test'].num_examples
        #número total de instâncias
        self.totalInstances = self.trainInstancesDataset + self.testInstancesDataset
        #número de instâncias em cada divisão do fold que vai para treinamento
        self.n_instances_fold_train = int(np.floor(self.totalInstances/self.params.kFold))
        #numero de instâncias de treinamento nesse fold
        self.trainInstances = self.n_instances_fold_train*(self.params.kFold - 1)
        #numero de instâncias de teste nesse fold
        self.testInstances = self.totalInstances - self.trainInstances

        self.trainDataset = getFromDatasetLL(0, self.trainInstances - 1, params.currentFold, self.n_instances_fold_train,
                                             self.testInstances, self.trainInstancesDataset, params.nClasses,
                                             self.dataset, 0, 1)
        
        self.testDataset = getFromDatasetLL(0, self.testInstances - 1, params.currentFold, self.n_instances_fold_train,
                                             self.testInstances, self.trainInstancesDataset, params.nClasses,
                                             self.dataset, 0, 1, test=True)
        
        self.unbalance()

    def unbalance(self):
        self.trainDataset = self.unbalance_dataset(self.trainDataset)
        _, lbls = self.trainDataset
        self.trainInstances = len(lbls)
        
        self.testDataset = self.unbalance_dataset(self.testDataset)
        _, lbls = self.testDataset
        self.testInstances = len(lbls)

    def unbalance_dataset(self, dataset):
        imgs, lbls = dataset
        tempCounter = [0]*self.params.nClasses
        for i in range(len(lbls)):
            tempCounter[lbls[i]]+=1
        maxClassInstances = np.max(tempCounter)
        coeff = (maxClassInstances - self.minClassInstances)/(self.params.nClasses-1)

        unbalancedImgs = []
        unbalancedLbls = []
        counter = [0]*10
        for i in range(len(lbls)):
            lbl = lbls[i]
            if(counter[lbl] <= (lbl*coeff + self.minClassInstances)):
                unbalancedImgs.append(imgs[i])
                unbalancedLbls.append(lbls[i])
                counter[lbl] += 1
        return np.array(unbalancedImgs), np.array(unbalancedLbls)

    def loadParams(self):
        self.params.datasetName = 'mnist'
        self.params.nClasses = 10
        self.params.imgChannels = 1
        self.params.imgWidth = 28
        self.params.imgHeight = 28
    
    def getTrainData(self, start, end):
        imgs, lbls = self.trainDataset
        return imgs[start:end], lbls[start:end]

    def getTestData(self, start, end):
        imgs, lbls = self.testDataset
        return imgs[start:end], lbls[start:end]