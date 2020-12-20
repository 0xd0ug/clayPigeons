#!/usr/bin/env python3

from probeType import Probe
from matchType import Match
from clayPigeonType import ClayPigeon
from multiprocessing import Process
import random
from time import sleep
from ast import literal_eval

def loadServiceDefs():

    def stringToPorts(stringports): # Translates nmap-style port specs to a list of ports
        ports=[]
        for port in stringports:
            if "-" not in port:
                ports.append(int(port))
            else:
                pair = port.split('-')
                assert len(pair) == 2
                pair[0] = int(pair[0])
                pair[1] = int(pair[1])
                assert pair[0] <= pair[1]
                for n in range(pair[0], pair[1] + 1):
                    ports.append(n)
        return ports

    def stringToMatch(rawMatch): # Cleans up the match string in nmap-service-probes
        assert rawMatch[0] == 'm'
        delim = rawMatch[1]
        stringEnd = rawMatch[2:].find(delim)+2
        return rawMatch[2:stringEnd],rawMatch[stringEnd+2:].rstrip('\n')

    def stringToProbe(rawProbe): # Cleans up the probe string in nmap-service-probes
        assert rawProbe[0] == 'q'
        delim = rawProbe[1]
        stringEnd = rawProbe[2:].find(delim)+2
        newVal=rawProbe[2:stringEnd]
        if len(newVal)>0:
            newVal = literal_eval('"' + newVal.replace('"', '\\"') + '"')
        return bytes(newVal,"latin-1")

    probes = []
    filename = "/usr/local/share/nmap/nmap-service-probes" # Change this to fit your system (use locate)
    with open(filename) as f:
        data = f.readlines()
        x = 0
        while x < len(data):
            if data[x][0:6] == 'Probe ':
                probe = data[x].split(maxsplit=3) # Determine protocol, probe name, and string sent as probe
                probeQuery=stringToProbe(probe[3])
                x += 1
                matches = []
                ports = []
                sslports = []
                while x < len(data) and data[x][0:6] != 'Probe ': # Everything in here applies to a single probe
                    if data[x][0:6] == 'match ': # Determine what we are supposed to match
                        rawmatch = data[x].split(maxsplit=2)
                        pattern,version = stringToMatch(rawmatch[2])
                        matches.append(Match(rawmatch[1],pattern,version, softmatch=False))
                    elif data[x][0:10] == 'softmatch ': # Same as above but for soft match
                        rawmatch = data[x].split(maxsplit=2)
                        pattern,version = stringToMatch(rawmatch[2])
                        matches.append(Match(rawmatch[1],pattern,version, softmatch=True))
                    elif data[x][0:6] == 'ports ': # Determine applicable ports if specified
                        ports = stringToPorts(data[x][6:].rstrip('\n').split(','))
                    elif data[x][0:9] == 'sslports ': # Determine applicable SSL ports if specified
                        sslports = stringToPorts(data[x][9:].rstrip('\n').split(','))
                    x += 1
                probes.append(Probe(probe[1],probe[2],probeQuery, matches, ports, sslports))
            x += 1
    return probes

def tryOne(probeToTry):
    match = probeToTry.getRandomMatch()

def makeClayPigeon(probe): # Created for multiProcessing
    return ClayPigeon(probe)

if __name__ == '__main__':
    numberOfClayPigeons=20
    probes = loadServiceDefs()
    z=[]
    for x in range(numberOfClayPigeons):
        # Uses multiprocessing to start listeners. Maybe there is a more efficient way?
        proc = Process(target=makeClayPigeon, args=(random.choice(probes),))
        z.append(proc)
        z[x].start()
