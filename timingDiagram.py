import time
import math
import collections
import sys
import os
import re
import matplotlib.pyplot
import matplotlib
import matplotlib.figure
import numpy
import optparse
import argparse
import xml
import xml.etree.ElementTree
import datetime
# get the file, convert time to seconds and subtract the first time in the list from all the other times 
# you need to know the initial state of the variables in order to create a file with the actual logic levels

class Graph:
     
    def __init__(self, graphableData, graphSettings):
        #self.dataSet = dict({"name": dict({"time": list(),"data": list()})})
        #self.GraphSettings = dict()
        try:
            self.dataSets=graphableData
            self.graphSettings=graphSettings
        except:
            print("error when calling graph class constructor. variable 'axes' could not be assigned to")

    def Plot(self):

        for dataSet in self.dataSets.keys():
            # use these keys to access the settings for that set
            # acccess to the set name level
            # make dictionary of plots?
            for figureName in self.graphSettings[dataSet].keys():
                subplots = len(self.graphSettings[dataSet][figureName].keys())
                fig =  matplotlib.pyplot.figure()
                fig.subplots(subplots,1)
                fig.suptitle(figureName)
                for plot in self.graphSettings[dataSet][figureName].keys():
                    subplotList=list(self.graphSettings[dataSet][figureName].keys())
                    ax = matplotlib.pyplot.subplot(subplots, 1, subplotList.index(plot)+1)
                     # add a title and axis names to the plot
                     #ax = fig.add_subplot(subplots, 1, plot.index(dataSeries)+1)
                    for dataSeries in self.graphSettings[dataSet][figureName][plot].dataSerieses: 
                        ax.plot(self.dataSets[dataSet][dataSeries]["time"], self.dataSets[dataSet][dataSeries]["data"], drawstyle="steps-post", label=plot)# title=figureName, xlabel=" time, s ", ylabel=" logic level ")
                        ax.grid()
                        matplotlib.pyplot.legend(loc="upper left")
                        matplotlib.pyplot.xlabel(" time, s ")
                        matplotlib.pyplot.ylabel(" logic level ")
                matplotlib.pyplot.show()


def buildObjs(cfgRoot, config):
    # check the configuration file 
    graphs = cfgRoot.find("graphs") #graphs is an Element object, which can :  iterate over its children, find() findall(), get(), .text
    #dataSets = xml.dom.Node()
    dataSets = graphs.find("dataSets")
    graphableData = dict()
    graphSettings = dict() #could have been its own class
    colourList = list()
    for dataSet in dataSets.iter():
        try:
            XMLdocElement = dataSet.find("settings").text

            CfgSettings = graphs.find(XMLdocElement)

            colourList = CfgSettings.find("colourList").text.split(",")

            figureSection=CfgSettings.find("figures")

            figureCount = int(figureSection.attrib[str(figureSection.tag)])

            labels = CfgSettings.find("labels")

            graphSettings[dataSet.tag] = dict()
            for figure in range(1,figureCount+1):
                figureInfo=figureSection.find("figure"+str(figure))

                figureName=figureInfo.attrib[figureInfo.tag]

                graphSettings[dataSet.tag][figureName] = dict()

                plotSection=figureInfo.find("plots")
                plotNumber=int(plotSection.attrib["plots"])

                for plot in range(1,plotNumber+1):
                    plotInfo=plotSection.find("plot"+str(plot))
 
                    plotName=plotInfo.attrib[plotInfo.tag]

                    plotSeries=plotInfo.text.split(',')

                    graphSettings[dataSet.tag][figureName][plotName]=Plot(plotSeries)
                    graphSettings[dataSet.tag][figureName][plotName].colourList = colourList
                    graphSettings[dataSet.tag][figureName][plotName].labels = labels
        except(AttributeError):
            pass
        regX = str(None)
        actualData = str(None)
        try:
            regX = dataSet.find("regX").text
        except(AttributeError):
            pass
        try:
            actualData = dataSet.find("filepath").text
        except(AttributeError):
            pass
        if regX != str(None) and actualData != str(None):
            (name, data) = processInputs(actualData, regX, cfgRoot)
            graphableData[dataSet.tag] = data
            #print("processing {0}, {1}, {2}".format(actualData, regX, config))
    return (graphableData, graphSettings)

    #add stuff to the graphs object

class Plot:

    def __init__(self, LdataSerieses):  
        self.dataSerieses=LdataSerieses
        self.colourList=list()
        self.labels=list()

def processInputs(filepath, regX, cfgRoot):
    # make the csv into a useable format
    # instantiate a datetime object with a format string
    file = open(filepath)
    lines = list(file.readlines())
    file.close
    lines.reverse()
    times = list()
    timeZero = datetime.datetime(2000,2,1)
    alreadyUsedNames=list()
    latestTime=0
    for line in lines:
        groupObj = re.search(regX, line) #it would be good for the meanings of every part of the regex to be in a file
        if groupObj != None:
            year = groupObj.group(1)
            month = groupObj.group(2)
            day = groupObj.group(3)
            hour = groupObj.group(4)
            minute = groupObj.group(5)
            second = groupObj.group(6)
            name = groupObj.group(13)
            #print("found data: {0}, {1}, {2}, {3}, {4}, {5}, {6}".format(year, month, day, hour, minute, second, name))
            timeOfData = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            if(len(times) == 0):
                timeZero = timeOfData # could instead keep the timeOfData somewhere else and put 0 and index 0 of times
                relTime = 0
            else:
                relTime=(timeOfData-timeZero).total_seconds()
            timeInSeconds = relTime
            if timeInSeconds > latestTime:
                latestTime = timeInSeconds
            times.append({name: timeInSeconds})
            year = groupObj.group(7)
            month = groupObj.group(8)
            day = groupObj.group(9)
            hour = groupObj.group(10)
            minute = groupObj.group(11)
            second = groupObj.group(12)
            #print("found data: {0}, {1}, {2}, {3}, {4}, {5}, {6}".format(year, month, day, hour, minute, second, name))
            timeOfData = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            relTime=(timeOfData-timeZero).total_seconds()
            timeInSeconds = relTime
            if timeInSeconds > latestTime:
                latestTime = timeInSeconds
            times.append({name: timeInSeconds})

    Gdata=dict()
    for data in times:
        oneName = list(data.keys())
        name = oneName[0]
        if name not in list(Gdata.keys()):
            Gdata[name] = dict({"time": list(), "data": list()})
            Gdata[name]["time"].append(data[name])
            print(startState(name, filepath, cfgRoot))
            state = invert(startState(name, filepath, cfgRoot))
            Gdata[name]["data"].append(state)
        else:
            Gdata[name]["time"].append(data[name])
            state = Gdata[name]["data"][len(Gdata[name]["data"])-1]#startState(name, filepath, config)
            Gdata[name]["data"].append(invert(state))


    for key in Gdata.keys():
        print(f"data for {key}")
        if Gdata[key]["time"][0] != 0:
            Gdata[key]["time"] = [0.0]+Gdata[key]["time"]
            Gdata[key]["data"] = [startState(key, filepath, cfgRoot)]+Gdata[key]["data"]
        if Gdata[key]["time"][len(Gdata[key]["time"])-1] != latestTime:
            Gdata[key]["time"].append(latestTime)
            Gdata[key]["data"].append(Gdata[key]["data"][len(Gdata[key]["data"])-1])
        for time in Gdata[key]["time"]:
            print(str(time)+", "+str(Gdata[key]["data"][Gdata[key]["time"].index(time)]))

    return (name, Gdata)
    

    # this can be altered to be the function that gets all the settings
def startState(name, filepath, cfgRoot):
    graphs = cfgRoot.find("graphs")
    dataSets = graphs.find("dataSets")
    for dataSet in dataSets.iter():        
        try:
            thing=dataSet.find("filepath")
            if filepath == dataSet.find("filepath").text: 
                states=dataSet.find("initialStates").text
                regex = re.search((".*"+name+"\s*=\s*([0-9]).*"), states)
                if regex.group(1) is not None:
                    state = int(regex.group(1))
                    return state
        except(AttributeError):
            pass                  
            
def main():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="file in csv format to use", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-c", "--config", dest="config", help="give a full path to a configuration file for the program")

    (options, args) = parser.parse_args()

    # read the config File
    if(options.config != None):
        cfg = xml.etree.ElementTree.parse(options.config)
        cfgRoot = cfg.getroot()
        gd, gs = buildObjs(cfgRoot, options.config)
        g = Graph(gd,gs)
        g.Plot()

def invert(a):
    return not a

if __name__ == "__main__":
    main()

