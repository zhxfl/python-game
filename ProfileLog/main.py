#coding: utf-8
import pstats
import math

class ProfData(object):
    def __init__(self):
        self.m_fTotalTime= 0.0
        self.m_dFuntion = {}
        self.m_dGraph = {}
        self.m_dFlag = {}

    def GetTotalTime(self, lLine):
        for szLine in lLine:
            if szLine.find('seconds') != -1:
                lSplit = szLine.split(' ')
                self.m_fTotalTime = float(lSplit[-2])

    def GetFunctionName(self, lSplit):
        nLen = len(lSplit)
        if nLen == 1 and  lSplit[0].find(':') != -1:
            lSplit = lSplit[0].split('(')
            szName = lSplit[0].split(':')[0] + lSplit[1].split(')')[0]
        else:
            szName = ''
            for szSplit in lSplit:
                szName += szSplit
        #print szName
        return szName

    def GetGraph(self, lLine):
        del lLine[:4]
        for szLine in lLine:
            if len(szLine) <= 1:
                continue
            if szLine.find('->') != -1:
                szStartFunction = self.GetFunctionName(szLine.split('->')[0].split())
                self.m_dGraph[szStartFunction] = {}
                if len(szLine.split('->')) >= 2 and len(szLine.split('->')[1]) >= 2:
                    lSplit = szLine.split('->')[1].split()
                    dElement = {}
                    lT = lSplit[0].split('/')
                    if len(lT) == 1:
                        dElement['ncalls'] = float(lSplit[0])
                    else:
                        dElement['ncalls'] = float(lT[0])
                    dElement['tottime'] = float(lSplit[1])
                    dElement['cumtime'] = float(lSplit[2])
                    dElement['function'] = self.GetFunctionName(lSplit[3:])
                    self.m_dGraph[szStartFunction][dElement['function']] = dElement
            else:
                lSplit = szLine.split()
                dElement = {}
                lT = lSplit[0].split('/')
                if len(lT) == 1:
                    dElement['ncalls'] = float(lSplit[0])
                else:
                    dElement['ncalls'] = float(lT[0])
                dElement['tottime'] = float(lSplit[1])
                dElement['cumtime'] = float(lSplit[2])
                dElement['function'] = self.GetFunctionName(lSplit[3:])
                if szLine.find('HasTreeAttr') != -1:
                    print 'end HasTreeAttr'
                self.m_dGraph[szStartFunction][dElement['function']] = dElement

        for (key, value) in self.m_dGraph.items():
            for(key1, value1) in value.items():
                self.m_dFlag[key1] = True

        for (key, value) in self.m_dGraph.items():
            if self.m_dFlag.has_key(key) == False:
                print key
                dFlag = {}
                dFlag[key] = True
                self.Dfs(key, float(self.m_dFuntion[key]['ncalls']), dFlag)
                #根节点，dfs重新算calls
                #print self.m_dGraph[szStartFunction]
            #print szLine
        return

    def Dfs(self, szCurName, nCalls, dFlag):
        for (key, value) in self.m_dGraph[szCurName].items():
            if dFlag.has_key(key) == False:
                dFlag[key] = True
                self.m_dGraph[szCurName][key]['ncalls'] /= nCalls
                self.Dfs(key, nCalls, dFlag)
                del dFlag[key]

    def GetFunctions(self, lLine):
        #ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        bFlag = False
        for szLine in lLine:
            if bFlag == True:
                lSplit = szLine.split()
                if len(lSplit) >= 5:
                    dFunction = {}
                    lT = lSplit[0].split('/')
                    if len(lT) == 1:
                        dFunction['ncalls'] = lSplit[0]
                    else:
                        dFunction['ncalls'] = lT[0]
                    dFunction['tottime'] = lSplit[1]
                    dFunction['percall'] = lSplit[2]
                    dFunction['cumtime'] = lSplit[3]
                    dFunction['percall'] = lSplit[4]
                    dFunction['function'] = self.GetFunctionName(lSplit[5:])
                    self.m_dFuntion[self.GetFunctionName(lSplit[5:])] = dFunction
            if szLine.find('ncalls') != -1 and szLine.find('tottime') != -1 and szLine.find('percall') != -1:
                bFlag = True

    def Analyze(self, FilePath):
        FileObj = open('x.prof', 'w')
        PstatsObj = pstats.Stats(FilePath, stream=FileObj)
        PstatsObj.strip_dirs().sort_stats(-1).print_stats()
        FileObj.close()
        FileObj = open('x.prof', 'r')
        szData = FileObj.read()
        lLine = szData.split('\n')
        self.GetTotalTime(lLine)
        print 'totalTime', self.m_fTotalTime
        self.GetFunctions(lLine)

        FileObj1 = open('y.prof', 'w')
        PstatsObj1 = pstats.Stats(FilePath, stream=FileObj1)
        PstatsObj1.strip_dirs().sort_stats(-1).print_callees()
        FileObj1.close()
        FileObj1 = open('y.prof', 'r')
        szData1 = FileObj1.read()
        lLine = szData1.split('\n')
        self.GetGraph(lLine)

def GetMaxCalls(ProfDataObj1, ProfDataObj2, nMaxCalls, fUnilizationRatio):
    dD1 = ProfDataObj1.m_dFuntion
    dD2 = ProfDataObj2.m_dFuntion
    dG1 = ProfDataObj1.m_dGraph
    dG2 = ProfDataObj2.m_dGraph
    fTime1 = ProfDataObj1.m_fTotalTime
    fTime2 = ProfDataObj2.m_fTotalTime
    #计算频率
    print '=========='
    #sorted(dD1.iteritems(), key=lambda d:d[1][], reverse = False )
    dAns = {}
    for (key, value) in dD1.items():
        if dG2.has_key(key):
            if float(dD1[key]['cumtime']) / fTime1 >= fUnilizationRatio or \
                            float(dD2[key]['cumtime']) / fTime2 >= fUnilizationRatio:
                for (key1, value1) in dG1[key].items():
                    #print (key1, value1)
                    nT1 = float(dG1[key][key1]['ncalls'])
                    nT2 = float(dG2[key][key1]['ncalls'])
                    if nT1 != nT2:
                        print float(dD1[key]['cumtime']) / fTime1, float(dD2[key]['cumtime']) / fTime2
                        print key, key1
                        print dG1[key][key1]['ncalls']
                        print dG2[key][key1]['ncalls']
                        print '--'
                        dAns[key] = math.fabs(nT1 - nT2)
        else:
            print 'new Function', key

    dAns = sorted(dAns.iteritems(), key = lambda d:d[1], reverse = True)
    for (key, value) in dAns:
        nCalls2 = float(dD2[key]['ncalls'])
        nCalls1 = float(dD1[key]['ncalls'])
        if math.fabs(nCalls2 - nCalls1) > nMaxCalls:
            print '调用频率相差%s calls/s' % math.fabs(nCalls1 - nCalls2)
            print 'ncalls=%s, tottime=%s, percall=%s, cumtime=%s, percall=%s, filename:lineno(function)=%s'\
                  %(dD1[key]['ncalls'], dD1[key]['tottime'], dD1[key]['percall'], dD1[key]['cumtime'], dD1[key]['percall'], dD1[key]['function'])
            print 'ncalls=%s, tottime=%s, percall=%s, cumtime=%s, percall=%s, filename:lineno(function)=%s'\
                  %(dD2[key]['ncalls'], dD2[key]['tottime'], dD2[key]['percall'], dD2[key]['cumtime'], dD2[key]['percall'], dD2[key]['function'])
            print '----------'

def GetMaxFunTime(dD1, dD2, fTime1, fTime2, mMaxFunTime, fUnilizationRatio):
    print '=========='
    dAns = {}
    #计算函数的平均时间差
    for (key, value) in dD2.items():
        if dD1.has_key(key):
            if float(dD1[key]['cumtime']) / fTime1 >= fUnilizationRatio or \
                            float(dD2[key]['cumtime']) / fTime2 >= fUnilizationRatio:
                nCalls1 = 1000 * float(dD1[key]['cumtime']) / float(dD1[key]['ncalls'])
                nCalls2 = 1000 * float(dD2[key]['cumtime']) / float(dD2[key]['ncalls'])
                dAns[key] = math.fabs(nCalls2 - nCalls1)
        else:
            print 'new Function', key

    dAns = sorted(dAns.iteritems(), key = lambda d:d[1], reverse = True)
    for (key, value) in dAns:
        nCalls1 = 1000 * float(dD1[key]['cumtime']) / float(dD1[key]['ncalls'])
        nCalls2 = 1000 * float(dD2[key]['cumtime']) / float(dD2[key]['ncalls'])
        if math.fabs(nCalls2 - nCalls1) > mMaxFunTime:
                print '平均时间差%fms' %(math.fabs(nCalls1 - nCalls2))
                print 'cpu时间占用率%f, 函数调用的平均时间=%fms, ncalls=%s, tottime=%s, percall=%s, cumtime=%s, percall=%s, filename:lineno(function)=%s'\
                      %(float(dD1[key]['cumtime']) / fTime1, nCalls1, dD1[key]['ncalls'], dD1[key]['tottime'], dD1[key]['percall'], dD1[key]['cumtime'], dD1[key]['percall'], dD1[key]['function'])
                print 'cpu时间占用率%f, 函数调用的平均时间=%fms, ncalls=%s, tottime=%s, percall=%s, cumtime=%s, percall=%s, filename:lineno(function)=%s'\
                      %(float(dD2[key]['cumtime']) / fTime2, nCalls2, dD2[key]['ncalls'], dD2[key]['tottime'], dD2[key]['percall'], dD2[key]['cumtime'], dD2[key]['percall'], dD2[key]['function'])
                print '----------'

if __name__ == '__main__':
    ProfDataObj1 = ProfData()
    ProfDataObj1.Analyze("dtws_mobile_client1.pstat")
    ProfDataObj2 = ProfData()
    ProfDataObj2.Analyze("dtws_mobile_client2.pstat")

    dD1 = ProfDataObj1.m_dFuntion
    dD2 = ProfDataObj2.m_dFuntion
    fTime1 = ProfDataObj1.m_fTotalTime
    fTime2 = ProfDataObj2.m_fTotalTime

    nMaxCalls = 10
    mMaxFunTime = 0.01 #ms
    #函数调用频率差别最大的
    GetMaxCalls(ProfDataObj1, ProfDataObj2, nMaxCalls, 0.10)
    
    #函数调用平均时间差别最大的
    GetMaxFunTime(dD1, dD2, fTime1, fTime2, mMaxFunTime, 0.10)
    


