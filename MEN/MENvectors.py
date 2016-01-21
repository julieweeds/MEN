__author__ = 'juliewe'


import ConfigParser,sys,ast,random,numpy as np, scipy.stats as stats,time
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
        self.whereami=self.config.get('default','whereami')
        self.pos=ast.literal_eval(self.config.get('default','pos'))
        self.options=ast.literal_eval(self.config.get('default','options'))
        self.outputvectors=(self.config.get('default','outputvectors')=='True')


    def get_vector_name(self,pos):
        self.myname=self.config.get(self.whereami,'parentdir')+self.config.get('default','filename')
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
        self.weighting=ast.literal_eval(self.config.get('default','weighting'))
        self.wthreshold=ast.literal_eval(self.config.get('default','wthreshold'))
        self.cds=ast.literal_eval(self.config.get('default','cds'))
        self.saliency=ast.literal_eval(self.config.get('default','saliency'))
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


    def getvectorstream(self,pos,cds,wt,w,cons):
        if self.outputvectors:
            filename=self.get_vector_name(MENManager.posmap[pos])
            if cds:
                filename+="_cds"
            filename+="_"+wt
            filename+="_shift"+str(w)
            filename+="_cs"+str(cons)
            outstream=open(filename,"wb")
            return outstream
        else:
            return None

    def run_reweight(self):
        for pos in self.pos:
            print "Generating SimEngine"
            filenames={}
            filenames[pos]=self.get_vector_name(MENManager.posmap[pos])
            try:
                #self.mySimEngine=SimEngine(filenames,getattr(self,MENManager.INCLUDE_PREFIX))
                self.mySimEngine=SimEngine(filenames,self._is_any)
            except:
                print "Fatal Error: Unable to generate simEngine"
                print filenames
                print pos
                exit(-1)
            print "Successfully generated SimEngine and loaded vectors"
            weighting=[]
            for cds in self.cds:
                if cds=='True':
                    weighting.append('smooth_ppmi')
                for wt in self.weighting:

                    for w in self.wthreshold:
                        for cons in self.saliency:
                            print "Reweighting vectors"

                            self.mySimEngine.reweight(pos,weighting=[wt]+weighting,ppmithreshold=float(w),saliency=cons,outstream=self.getvectorstream(pos,cds,wt,w,cons))

    def run_MEN(self):
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

            results=[]
            weighting=[]
            resultsstream=open('men.out','ab')
            resultsstream.write("Starting MEN evaluation at: "+time.strftime("%c")+"\n")
            for cds in self.cds:
                if cds=='True':
                    weighting.append('smooth_ppmi')
                for wt in self.weighting:

                    for w in self.wthreshold:
                        for cons in self.saliency:
                            print "Reweighting vectors"

                            self.mySimEngine.reweight(pos,weighting=[wt]+weighting,ppmithreshold=float(w),saliency=cons,outstream=self.getvectorstream(pos,cds,wt,w,cons))
                            self.myMenReader.updateAutoSims(self.mySimEngine.selectedSims(self.myMenReader.getPairList(pos)))
                            res=(cds,wt,w,cons,self.myMenReader.triples.correlate(show_graph=False))
                            resultsstream.write(res)
                            resultsstream.write("\n")
                            results.append(res)

            print "Summary of results for ",self.weighting
            for res in results:
                print res[0],res[1],res[2],res[3],res[4]
            resultsstream.write("Ending MEN evaluation at: "+time.strftime("%c")+"\n")
            resultsstream.close()
    def run(self):
        if "MEN" in self.options:
            self.run_MEN()
        elif "reweight" in self.options:
            self.run_reweight()
        else:
            print "Unknown options: ",self.options


if __name__=="__main__":
    myManager=MENManager(sys.argv[1])
    myManager.run()