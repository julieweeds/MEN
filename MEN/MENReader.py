__author__ = 'juliewe'

import ConfigParser,sys,ast,random,numpy as np, scipy.stats as stats


try:
    from compositionality import graphing
    graphing_loaded=True
except:
    print "Warning: unable to load graphing module"
    graphing_loaded=False


def unpack(line):
    #turn "berry-n seed-n 37.0000" into (berry,n,seed,n,37.0000)
    try:
        fields=line.split(' ')
        v1=fields[0].split('-')
        v2=fields[1].split('-')
        return (v1[0],v1[1],v2[0],v2[1],float(fields[2]))
    except:
        print "Error in data file:  "+line


class Triple:

    def __init__(self,values):
        self.leftlemma=values[0]
        self.leftpos=values[1]
        self.rightlemma=values[2]
        self.rightpos=values[3]
        self.humansim=values[4]
        self.autosim=-1

    def getLeftIndex(self):
        return self.leftlemma+'-'+self.leftpos

    def getRightIndex(self):
        return self.rightlemma+'-'+self.rightpos

    def updateAutoSim(self,sim):
        self.autosim=sim

    def getHumanSim(self):
        return self.humansim

    def getAutoSim(self):
        return self.autosim


class Triples:

    randomSeed=13

    def __init__(self,config):
        self.pos=[x.lower() for x in ast.literal_eval(config.get('default','pos'))]
        self.allindex={}
        self.entryLists={}
        for pos in self.pos:
            self.entryLists[pos]=[]


    def addEntry(self,pos,lemma):
        if lemma not in self.entryLists[pos]:
            self.entryLists[pos].append(lemma)

    def add(self,values):
        if self.include(values):
            trip=Triple(values)
            self.allindex[trip.getLeftIndex()+":"+trip.getRightIndex()]=trip
            self.addEntry(trip.leftpos,trip.leftlemma)
            self.addEntry(trip.rightpos,trip.rightlemma)
            return 1
        else:
            return 0

    def include(self,values):
        if values[1] in self.pos and values[3] in self.pos:
            return True
        else:
            return False

    def getEntryList(self,pos):

        if pos.lower() in self.entryLists.keys():
            return self.entryLists[pos.lower()]
        else:
            print "Unknown POS: "+pos


    def getPairList(self,pos):
        pairs=[]
        for trip in self.allindex.values():
            if trip.leftpos == pos.lower() and trip.rightpos==pos.lower():
                pairs.append((trip.leftlemma,trip.rightlemma))
        return pairs

    def updateAutoSims(self,simlist):

        for trip,sim in zip(self.allindex.values(),simlist):
            trip.updateAutoSim(sim)


    def stats(self):
        print "All index: ",str(len(self.allindex.keys()))


    def randomAutoSims(self):
        print "Generating random automatic similarity scores"
        random.seed(Triples.randomSeed)
        scores = [x for x in range(0,len(self.allindex.keys()),1)]
        random.shuffle(scores)
        for trip,score in zip(self.allindex.values(),scores):
            trip.updateAutoSim(score)

    def correlate(self,show_graph=True):
        xs=[]
        ys=[]
        for trip in self.allindex.values():
            x=trip.getHumanSim()
            y=trip.getAutoSim()
            if x>=0 and y>=0:
                xs.append(x)
                ys.append(y)
        print "Spearman's Correlation Coefficient and p'value for Human Judgements vs Automatic Similarity over %s values: "%(str(len(xs))),stats.spearmanr(np.array(xs),np.array(ys))
        if graphing_loaded and show_graph:
            graphing.makescatter(xs,ys)


class MENReader:
    def __init__(self,configfile):
        self.configfile=configfile
        print "Reading configuration from "+self.configfile
        self.config=ConfigParser.RawConfigParser()
        self.config.read(self.configfile)
        self.triples=Triples(self.config)

    def readfile(self):
        datafile=self.config.get('default','mendatadir')+self.config.get('default','mendatafile')
        print "Reading "+datafile

        with open(datafile,'rb') as instream:
            added=0
            lines=0
            for lines,line in enumerate(instream):
                values=unpack(line)

                added+=self.triples.add(values)
                #print lines,line

            print "Added %s from %s lines"%(added,lines+1)

    def getEntryList(self,pos="N"):
        return self.triples.getEntryList(pos=pos)

    def getPairList(self,pos="N"):
        return self.triples.getPairList(pos=pos)

    def updateAutoSims(self,simlist):
        self.triples.updateAutoSims(simlist)

    def run(self):
        self.readfile()
        self.triples.stats()
        self.triples.randomAutoSims()
        self.triples.correlate()



if __name__=="__main__":
    myReader=MENReader(sys.argv[1])
    myReader.run()




