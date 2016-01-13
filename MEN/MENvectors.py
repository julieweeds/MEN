__author__ = 'juliewe'


import ConfigParser,sys,ast,random,numpy as np, scipy.stats as stats
from compositionality.simEngine import SimEngine
from MENReader import MENReader




class MENManager:

    posmap={"N":"nouns","V":"verbs","J":"adjs","R":"advs"}
    INCLUDE_PREFIX="_is_included_"

    def __init__(self,configfile):
        self.configfile=configfile
        print "Reading configuration from "+self.configfile
        self.config=ConfigParser.RawConfigParser()
        self.config.read(self.configfile)
        self.myMenReader=MENReader(self.configfile)
        self.pos=ast.literal_eval(self.config.get('default','pos'))


    def get_vector_name(self,pos):
        self.myname=self.config.get('default','parentdir')+self.config.get('default','filename')
        mini = self.config.get('default','minorder')
        maxi = self.config.get('default','maxorder')
        if mini == "X":
            self.minorder=0
            self.maxorder=2
            self.reducedstring=""
        else:
            self.minorder=int(mini)
            self.maxorder=int(maxi)
            self.reducedstring=".reduce_"+str(mini)+"_"+str(maxi)
        self.suffix="."+pos+self.reducedstring+".filtered"
        self.normalised=(self.config.get('default','normalised')=="True")
        if self.normalised:
            self.suffix+=".norm"
        self.weighting=self.config.get('default','weighting')
        self.wthreshold=float(self.config.get('default','wthreshold'))
        return self.myname+self.suffix

    def _is_included_N(self,token):
        lemma = token.split("/")[0]
        #print token,lemma
        if lemma in self.nounlist.keys():
            self.nounlist[lemma]=1
            return True
        else:
            return False

    def _is_any(self,token):
        return True

    def generate_simengine(self,pos="N"):
        print "Generating SimEngine"
        filenames={}
        filenames[pos]=self.get_vector_name(MENManager.posmap[pos])
        try:
            #self.mySimEngine=SimEngine(filenames,getattr(self,MENManager.INCLUDE_PREFIX))
            self.mySimEngine=SimEngine(filenames,self._is_included_N)
        except:
            print "Fatal Error: Unable to generate simEngine"
            print filenames
            print pos
            exit(-1)
        print "Successfully generated SimEngine and loaded vectors"





    def run(self):
        self.myMenReader.readfile()
        self.tokenlists={}
        for pos in self.pos:
            self.nounlist={}
            for e in self.myMenReader.getEntryList(pos):
                self.nounlist[e]=0
            print "Need to load %s vectors "%(str(len(self.nounlist)))
            #print self.tokenlists[pos]
            self.generate_simengine(pos)
            missed=[x for x in self.nounlist.keys() if self.nounlist[x]==0]
            print "Not found: ", missed
            self.mySimEngine.selectedSims(self.myMenReader.getPairList(pos))

if __name__=="__main__":
    myManager=MENManager(sys.argv[1])
    myManager.run()