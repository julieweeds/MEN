__author__ = 'juliewe'

import ConfigParser,sys

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

    def init(self,values):
        leftlemma=values[0]
        leftpos=values[1]
        rightlemma=values[2]
        rightpos=values[3]
        sim=values[4]

    def getLeftIndex(self):
        return self.leftlemma+'-'+self.leftpos

    def getRightIndex(self):
        return self.rightlemma+'-'+self.rightpos

class Triples:

    def init(self,config):
        self.pos=config.read('default','pos')
        self.leftindex={}
        self.rightindex={}
        

    def add(self,values):
        if self.include(values):
            trip=Triple(values)

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
            for lines,line in enumerate(instream):
                values=unpack(line)

                self.triples.add(values)
                print lines,line


    def run(self):
        self.readfile()



if __name__=="__main__":
    myReader=MENReader(sys.argv[1])
    myReader.run()




