import pandas as pd
import os
import re
import math
import gzip
from scipy.stats import levene, shapiro, ttest_ind
import numpy as np
from sklearn.decomposition import PCA
from sklearn import preprocessing
import xlsxwriter
from time import strftime, localtime

class GeneFrame(object):
    def ensgToIndex(self, df):
        df['gene'] = [re.sub('\..*','',x) for x in df['gene']]
        df = df.loc[[bool(re.match('ENSG',x,re.I)) for x in df['gene']]]
        df = df.set_index('gene')
        return df

    def __calcCPM(self, s1, s2):
        scaleFac = sum(self.df[s1])/1000000
        self.df[s2] = [math.log2(x/scaleFac + 1) for x in self.df[s1]]

class CCLE(GeneFrame):
    def __init__(self, file, tissue=''):
        self.df = self.__importCounts(file)
        self.tissue = tissue.replace(' ', '_')
        self.geneList = self.df[self.df.keys()[:2]]
        self.geneList.columns = ['gene', 'Name']
        self.df = self.__tissueSelect(self.df)
        self.df = pd.DataFrame(self.ensgToIndex(self.df), dtype=float)
        for x in self.df.keys():
            self._GeneFrame__calcCPM(x,x)
        self.geneList = self.ensgToIndex(self.geneList)

    def __importCounts(self, CCLE_File):
        CCLE_archive = os.getcwd() + r"\Info-Files\CCLE_Data.csv"
        if os.path.exists(CCLE_archive):
            ret = pd.read_csv(CCLE_archive)
        else:
            # import raw counts
            table = []
            hasNext = True
            with gzip.open(CCLE_File, 'rt') as f:
                for l in f:
                    l = l.split('\t')
                    table.append(l)
                    if l == ['']:
                        hasNext = False

            cols = pd.Series([len(x) for x in table]).value_counts().index[0]
            newTable = []
            for x in table:
                if len(x) == cols:
                    newTable.append(x)
            
            ret = pd.DataFrame(newTable[1:], columns=newTable[0])
            ret.to_csv(CCLE_archive,index=False)
        return ret

    def __tissueSelect(self, df):
        temp = [bool(re.match('gene',x,re.I)) or bool(re.match('name',x,re.I)) for x in df.columns]
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
            self._GeneFrame__calcCPM('counts', 'cpm')
        else:
            raise TypeError('Samples consist of a string and a pandas DataFrame.')

    def getCPM(self):
        ret = self.df['cpm']
        ret.name = self.__name
        return ret


class GeneCompare():
    def __init__(self, samples, CCLE_Data):
        self.__sCount = len(samples)
        first = True
        for x in samples.values():
            if isinstance(x, Sample):
                if first:
                    self.df = x.getCPM()
                    first = False
                else:
                    self.df = pd.merge(self.df,x.getCPM(), left_index=True, right_index=True)
            else:
                raise TypeError('GeneCompare "samples" must be objects of type Sample.')
        if isinstance(CCLE_Data, CCLE):
            self.df = pd.merge(self.df, CCLE_Data.df, right_index=True, left_index=True)
        else:
            raise TypeError('GeneCompare "CCLE" must be objects of type CCLE.')

    def correlation(self, samples):
        corr = {}
        df = self.df
        n = self.__sCount
        first = True
        for c in samples:
            tempCor = [['Sample','Spearman']]
            cols = list(df.columns)
            cols.remove(c)
            for i in cols:
                if first: df[i] = [math.log2((n)+1) for n in df[i]]
                score = df[c].corr(df[i], method="spearman")
                tempCor.append([i,score])
            if first: first = False
            tempCor = pd.DataFrame(tempCor[1:], columns=tempCor[0])
            corr[c] = tempCor.set_index('Sample')
        corr = pd.concat(corr, axis=1)
        return corr

    def calcPCA(self, n):
        df = self.df.transpose()
        x = df.loc[:].values
        cells = pd.DataFrame(df.index.values, columns=['Cell Line'])
        x = preprocessing.StandardScaler().fit_transform(x)

        pca = PCA(n_components=n)
        pComp = pca.fit_transform(x)
        pDF = pd.DataFrame(pComp, columns=['PC'+str(x) for x in list(range(1,n+1))])
        self.PCA = pd.concat([cells,pDF], axis=1)
        self.PCA = self.PCA.set_index('Cell Line', drop=True)
        self.percVar = np.round(pca.explained_variance_ratio_* 100, decimals=2)

    def sampleKeys(self):
        return self.df.keys()[:self.__sCount]

    def CCLEKeys(self):
        return self.df.keys()[self.__sCount:]

    def co_PCA(self, comp_1, comp_2, coordinates):
        df = self.PCA[[comp_1,comp_2]]
        cLine = []
        for x in coordinates:
            cLine.extend(list(df[[self.__round(x,12) == self.__round(df.loc[i],12) for i in df.index]].index))
        return sorted(set(cLine))

    def __round(self, l, n):
        return [round(x,n) for x in l]


class GeneReport():
    def __init__(self, compare_obj, selection, ccle):
        if not isinstance(selection,pd.Index):
            raise TypeError("selection must be of type pndas.Index")
        self.__compare_obj = compare_obj
        self.__selection = selection.tolist()
        self.__tissue_type = ccle.tissue
        self.__geneList = ccle.geneList
        self.__ignored = []
        for x in self.__compare_obj.df.columns:
            if not any([n == x for n in selection]):
                self.__ignored.append(x)
    
    def exportXLSX(self):
        file_dir = os.getcwd() + r"\Reports"
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        error = False
        try:
            self.__createWorkbook(file_dir)
            self.__popGeneSummary()
            self.__popCorrelationSheet()
            self.__writer.save()
        except:
            error = True
        return error

    def __createWorkbook(self, file_dir):
        ts = strftime("%Y-%m-%d %H%M%S", localtime())
        self.__writer = pd.ExcelWriter(os.path.join(file_dir, self.__tissue_type+' Report '+ts+'.xlsx'), engine='xlsxwriter')

    def __popGeneSummary(self):
        if len(self.__selection) > 2:
            select_df = self.__compare_obj.df[self.__selection].T
            ignore_df = self.__compare_obj.df[self.__ignored].T
            #self.__popSampleSummary(select_df,ignore_df) #Depreciated
            summary_df = {}
            summary_df['Statistical Comparison'] = self.__calcGeneComp(select_df,ignore_df)
            summary_df['Selection Descriptive Statistics'] = select_df.describe().T
            summary_df['Exclusion Descriptive Statistics'] = ignore_df.describe().T
            summary_df = pd.concat(summary_df,axis=1)
            summary_df.to_excel(self.__writer, sheet_name='Gene Summary')

    def __calcGeneComp(self,select_df,ignore_df):
        testStats = []
        for i in select_df.keys():
            select_mean = sum(select_df[i].values)/len(select_df[i].values)
            ignore_mean = sum(ignore_df[i].values)/len(ignore_df[i].values)
            normScores = [round(shapiro(select_df[i].values)[1],5), round(shapiro(ignore_df[i].values)[1],5)]
            leveneScore = levene(select_df[i].values.tolist(), ignore_df[i].values.tolist())[1]
            if leveneScore < 0.05:
                homoscedastic = False
                ttest_type = "Welch's"
            else:
                homoscedastic = True
                ttest_type = "Student's"
            ttest_pvalue = ttest_ind(select_df[i].values, ignore_df[i].values, equal_var=homoscedastic)[1]
            meanDiff = select_mean-ignore_mean
            testStats.append([i,abs(meanDiff),meanDiff,normScores,leveneScore, ttest_pvalue, ttest_type])
        ret = pd.DataFrame(testStats, columns=['gene','abs mean diff.','mean diff.','shapiro p-value','levene p-value','t-test p-value','t-test method'])
        ret = ret.set_index('gene')
        ret = self.__geneList.join(ret)
        ret = ret.sort_values('abs mean diff.', ascending=False)
        ret = ret.drop(labels=['abs mean diff.'], axis=1)
        return ret

    def __popSampleSummary(self,select_df,ignore_df): #Depreciated
        select_df = select_df.describe().T
        ignore_df = ignore_df.describe().T
        select_df.to_excel(self.__writer, sheet_name='Select Summary')
        ignore_df.to_excel(self.__writer, sheet_name='Exclude Summary')
        
    def __popCorrelationSheet(self):
        correlations_df = self.__compare_obj.correlation(self.__selection)
        correlations_df.to_excel(self.__writer, sheet_name='Correlational Data')

    def __popSampleSheets(self): #depreciated
        """Writes spearman correlations for selected samples
        to self-titled sheets. """
        correlations = self.__compare_obj.correlation(self.__selection)
        for s in correlations.keys():
            if len(s) > 30:
                cap = 30
            else:
                cap = len(s)
            correlations[s].to_excel(self.__writer, sheet_name=s[:cap])
