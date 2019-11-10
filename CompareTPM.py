import pandas as pd
import re
import math
from scipy.stats import levene
import numpy as np
from sklearn.decomposition import PCA
from sklearn import preprocessing

class GeneFrame(object):
    def ensgToIndex(self, df):
        df['gene'] = [re.sub('\..*','',x) for x in df['gene']]
        df = df.loc[[bool(re.match('ENSG',x)) for x in df['gene']]]
        df = df.set_index('gene')
        return df

class CCLE(GeneFrame):
    def __init__(self, file, tissue=''):
        self.df = self.__importCounts(file)
        self.tissue = tissue.replace(' ', '_')
        self.geneList = self.df[self.df.keys()[:2]]
        self.geneList.columns = ['gene', 'Name']
        self.df = self.__tissueSelect(self.df)
        self.df = pd.DataFrame(self.ensgToIndex(self.df), dtype=int)
        self.geneList = self.ensgToIndex(self.geneList)

    def __importCounts(self, CCLE_File):
        # import raw counts
        f = open(CCLE_File)
        table = []
        hasNext = True
        while hasNext:
            l = f.readline().strip()
            l = l.split('\t')
            table.append(l)
            if l == ['']:
                hasNext = False

        cols = pd.Series([len(x) for x in table]).value_counts().index[0]
        newTable = []
        for x in table:
            if len(x) == cols:
                newTable.append(x)
        
        return pd.DataFrame(newTable[1:], columns=newTable[0])

    def __tissueSelect(self, df):
        temp = [bool(re.match('[G,g]{1}ene',x)) or bool(re.match('[N,n]{1}ame',x)) for x in df.columns]
        if sum(temp) < 1:
            raise AttributeError("No 'gene' index found.")
        elif sum(temp) > 1:
            raise AttributeError("Too many 'gene' indexes found.")
        i = pd.Series(range(0,len(temp)))[temp]
        cols = df.columns[[bool(re.match('.*'+self.tissue+'.*',x)) for x in df.columns]].insert(0,df.columns[i][0])
        df = df[cols]
        df.columns = cols[1:].insert(0,'gene')
        return df


class Sample(GeneFrame):
    def __init__(self, name, dataFrame):
        if isinstance(name, str) and isinstance(dataFrame, pd.DataFrame):
            if len(dataFrame.columns) > 2:
                raise ValueError('A sample can only have two columns.')
            self.__name = name
            dataFrame.columns = ['gene','counts']
            self.df = self.ensgToIndex(dataFrame)
            self.__calcCPM()
        else:
            raise TypeError('Samples consist of a string and a pandas DataFrame.')

    def __calcCPM(self):
        scaleFac = sum(self.df['counts'])/1000000
        self.df['cpm'] = [x/scaleFac for x in self.df['counts']]

    def getCPM(self):
        ret = self.df['cpm']
        ret.name = self.__name
        return ret


class GeneCompare():
    def __init__(self, *samples, CCLE_Data):
        self.__sCount = len(samples)
        for x in range(0,self.__sCount):
            if isinstance(samples[x], Sample):
                if x == 0:
                    self.df = samples[x].getCPM()
                else:
                    self.df = pd.merge(self.df,samples[x].getCPM(), left_index=True, right_index=True)
            else:
                raise TypeError('GeneCompare "samples" must be objects of type Sample.')
        if isinstance(CCLE_Data, CCLE):
            self.df = pd.merge(self.df, CCLE_Data.df, right_index=True, left_index=True)
        else:
            raise TypeError('GeneCompare "CCLE" must be objects of type CCLE.')
        self.__normalize()

    def __normalize(self):
        self.cor = {}
        df = self.df
        n = self.__sCount
        first = True
        for c in df.columns[:n]:
            df[c] = self.__calc(df[c])
            tempCor = [['CCLE Sample', 'Levene','Pearson']]
            for i in df.columns[n:]:
                if first: df[i] = self.__calc(df[i])
                lValue = levene(df[c], df[i])[1]
                score = df[c].corr(df[i])
                tempCor.append([i,lValue,score])
            if first: first = False
            tempCor = pd.DataFrame(tempCor[1:], columns=tempCor[0])
            self.cor[c] = tempCor

    def __calc(self, x):
        scaleFac = sum(x)/1000000
        return [math.log2((n/scaleFac)+1) for n in x]

    def calcPCA(self):
        df = self.df.transpose()
        x = df.loc[:].values
        cells = pd.DataFrame(df.index.values, columns=['Cell Line'])
        x = preprocessing.StandardScaler().fit_transform(x)

        n = 4
        pca = PCA(n_components=n)
        pComp = pca.fit_transform(x)
        pDF = pd.DataFrame(pComp, columns=['PC'+str(x) for x in list(range(1,n+1))])
        self.PCA = pd.concat([cells,pDF], axis=1)
        self.percVar = np.round(pca.explained_variance_ratio_* 100, decimals=2)

