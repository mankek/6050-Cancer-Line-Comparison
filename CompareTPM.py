import pandas as pd
import re
import math
from scipy.stats import levene

class GeneFrame(object):
    def __init__(self, df):
        self.df = df

    def clearVersions(self):
        self.df['gene'] = [re.sub('\..*','',x) for x in self.df['gene']]


class GeneList(GeneFrame):
    def __init__(self, Gene_List_CSV):
        temp = pd.read_csv(Gene_List_CSV)
        if isinstance(temp, pd.DataFrame) and \
            all([x in temp.columns for x in ['gene','length']]):
            super().__init__(temp)
            self.clearVersions()
        else:
            raise TypeError('File did not return valid DataFrame.')


class CCLE(GeneFrame):
    def __init__(self, file, tissue=''):
        self.df = pd.read_csv(file, sep='\t')
        self.tissue = tissue.replace(' ', '_')
        self.df = self.__geneCheck(self.df)
        self.clearVersions()

    def __geneCheck(self, df):
        temp = [bool(re.match('gene*',x)) for x in df.columns]
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
    def __init__(self, name, dataFrame, geneList=None):
        if isinstance(name, str) and isinstance(dataFrame, pd.DataFrame):
            if len(dataFrame.columns) > 2:
                raise ValueError('A sample can only have two columns.')
            self.__name = name
            dataFrame.columns = ['gene','counts']
            super().__init__(dataFrame)
            if isinstance(geneList, GeneList):
                self.applyGeneList(geneList)
            elif geneList != None:
                raise TypeError('geneList must be a GeneList object.')
        else:
            raise TypeError('Samples consist of a string and a pandas DataFrame.')

    def applyGeneList(self, geneList):
        self.clearVersions()
        self.df = self.df[self.df['gene'].isin(geneList.df['gene'])]
        self.df = self.df.merge(geneList.df[geneList.df['gene'].isin(self.df['gene'])][['gene','length']])
        self.__calcTPM()

    def __calcTPM(self):
        self.df['rpk'] = self.df['counts']/(self.df['length']/1000)
        self.df['tpm'] = self.__calc(self.df['rpk'])

    def compareCCLE(self, CCLE_Data):
        self.cor = [['CCLE Sample', 'Levene','Pearson']]
        if not isinstance(CCLE_Data, CCLE):
            raise TypeError('CCLE parameter must be CCLE object.')
        c = CCLE_Data.df[CCLE_Data.df['gene'].isin(self.df['gene'])]
        for i in c.columns[1:]:
            scaleFac = sum(c[i])/1000000
            c.loc[:][i] = self.__calc(c[i])
            lValue = levene(self.df['tpm'], c[i])[1]
            score = self.df['tpm'].corr(c[i])
            self.cor.append([i,lValue,score])
        self.cor = pd.DataFrame(self.cor)
        self.df = self.df.merge(c)
    
    def __calc(self, x):
        scaleFac = sum(x)/1000000
        return [(n/scaleFac) for n in x]

