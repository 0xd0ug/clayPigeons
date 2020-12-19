#!/usr/bin/env python3

from probeType import Probe
from matchType import Match
from clayPigeonType import ClayPigeon
from multiprocessing import Process
import random
from time import sleep
from ast import literal_eval

usedPorts=[]

def loadServiceDefs():

    def stringToPorts(stringports):
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

    def stringToMatch(rawMatch):
        assert rawMatch[0] == 'm'
        delim = rawMatch[1]
        stringEnd = rawMatch[2:].find(delim)+2
        return rawMatch[2:stringEnd],rawMatch[stringEnd+2:].rstrip('\n')

    def stringToProbe(rawProbe):
        assert rawProbe[0] == 'q'
        delim = rawProbe[1]
        stringEnd = rawProbe[2:].find(delim)+2
        newVal=rawProbe[2:stringEnd]
        if len(newVal)>0:
            newVal = literal_eval('"' + newVal.replace('"', '\\"') + '"')
        return bytes(newVal,"latin-1")

    probes = []
    filename = "/usr/local/share/nmap/nmap-service-probes"
    with open(filename) as f:
        data = f.readlines()
        x = 0
        while x < len(data):
            if data[x][0:6] == 'Probe ':
                probe = data[x].split(maxsplit=3)
                probeQuery=stringToProbe(probe[3])
                x += 1
                matches = []
                ports = []
                sslports = []
                while x < len(data) and data[x][0:6] != 'Probe ':
                    if data[x][0:6] == 'match ':
                        rawmatch = data[x].split(maxsplit=2)
                        pattern,version = stringToMatch(rawmatch[2])
                        matches.append(Match(rawmatch[1],pattern,version, softmatch=False))
                    elif data[x][0:10] == 'softmatch ':
                        rawmatch = data[x].split(maxsplit=2)
                        pattern,version = stringToMatch(rawmatch[2])
                        matches.append(Match(rawmatch[1],pattern,version, softmatch=True))
                    elif data[x][0:6] == 'ports ':
                        ports = stringToPorts(data[x][6:].rstrip('\n').split(','))
                    elif data[x][0:9] == 'sslports ':
                        sslports = stringToPorts(data[x][9:].rstrip('\n').split(','))
                    x += 1
                probes.append(Probe(probe[1],probe[2],probeQuery, matches, ports, sslports))
            x += 1
    return probes

def tryOne(probeToTry):
    match = probeToTry.getRandomMatch()

def makeClayPigeon(probe):
    return ClayPigeon(probe)

if __name__ == '__main__':
    probes = loadServiceDefs()
    z=[]
    for x in range(100):
        proc=Process(target=makeClayPigeon, args=(random.choice(probes),))
        z.append(proc)
        z[x].start()

