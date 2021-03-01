#!/usr/bin/env python3
import subprocess
from time import sleep

from probeType import Probe
from matchType import Match
from cpType import ClayPigeon
from multiprocessing import Process
import random
import os
from ast import literal_eval
import json


def loadServiceDefs():
    def stringToPorts(stringports):  # Translates nmap-style port specs to a list of ports
        ports = []
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

    def stringToMatch(rawMatch):  # Cleans up the match string in nmap-service-probes
        assert rawMatch[0] == 'm'
        delim = rawMatch[1]
        stringEnd = rawMatch[2:].find(delim) + 2
        return rawMatch[2:stringEnd], rawMatch[stringEnd + 2:].rstrip('\n')

    def stringToProbe(rawProbe, debug = False):  # Cleans up the probe string in nmap-service-probes
        assert rawProbe[0] == 'q'
        delim = rawProbe[1]
        stringEnd = rawProbe[2:].find(delim) + 2
        newVal = rawProbe[2:stringEnd]
        newVal = newVal.replace(r"\0",r"\x00")
        returnVal = literal_eval('"' + newVal.replace('"', '\\"') + '"').encode('latin-1')
        if debug:
            print(newVal)
            print(returnVal)
        return returnVal

    def findProbesFile():  # Find the nmap-service-probes file
        checkme = ['./', '/usr/share/nmap/', '/usr/share/nmap/']
        filename = 'nmap-service-probes'
        for directory in checkme:
            path = directory + filename
            if os.path.exists(path):
                return path
        located = subprocess.check_output(['locate', filename])
        if len(located) == 0:
            raise Exception('Cannot locate ' + filename + ' in filesystem.')
        else:
            return located.decode('latin-1').partition('\n')[0]

    probes = []
    filename = findProbesFile()
    with open(filename) as f:
        data = f.readlines()
        x = 0
        while x < len(data):
            if data[x][0:6] == 'Probe ':
                probe = data[x].split(maxsplit=3)  # Determine protocol, probe name, and string sent as probe
                if probe[2] != "oracle-tns":
                    probeQuery = stringToProbe(probe[3])
                else:
                    probeQuery = stringToProbe(probe[3],True)
                x += 1
                matches = []
                ports = []
                sslports = []
                while x < len(data) and data[x][0:6] != 'Probe ':  # Everything in here applies to a single probe
                    if data[x][0:6] == 'match ':  # Determine what we are supposed to match
                        rawmatch = data[x].split(maxsplit=2)
                        pattern, version = stringToMatch(rawmatch[2])
                        matches.append(Match(rawmatch[1], pattern, version, softmatch=False))
                    elif data[x][0:10] == 'softmatch ':  # Same as above but for soft match
                        rawmatch = data[x].split(maxsplit=2)
                        pattern, version = stringToMatch(rawmatch[2])
                        matches.append(Match(rawmatch[1], pattern, version, softmatch=True))
                    elif data[x][0:6] == 'ports ':  # Determine applicable ports if specified
                        ports = stringToPorts(data[x][6:].rstrip('\n').split(','))
                    elif data[x][0:9] == 'sslports ':  # Determine applicable SSL ports if specified
                        sslports = stringToPorts(data[x][9:].rstrip('\n').split(','))
                    x += 1
                probes.append(Probe(probe[1], probe[2], probeQuery, matches, ports, sslports))
            x += 1
    return probes


def createConfig(probes):

    def sortFunc(e):
        return e["port"]

    numberofClayPigeons = 30
    config = readConfig(probes)  # Attempt to read config if one exists,
    if config == []:  # Otherwise create a random config
        portList = []
        config = []
        iAmRoot = True if os.geteuid() == 0 else False
        for x in range(numberofClayPigeons):
            while portList == [] or port in portList or (port < 1024 and not iAmRoot):
                probe = random.choice(probes)
                match = probe.getRandomMatch()
                port = probe.getRandomPort()
                if portList == []:
                    portList = [-1]
            portList.append(port)
            config.append({"probe": probe, "match": match, "port": port})
            config.sort(key=sortFunc)
        print("Created config with", len(config), "clayPigeons.")
    else:
        print("Loaded config with", len(config), "clayPigeons.")
    return config


def saveConfig(config):
    filename = "cp.conf"
    pigeonList = []
    f = open(filename, "w")
    for x in config:
        pigeonList.append({"probe": str(x["probe"]), "match": str(x["match"]), "port": str(x["port"])})
    f.write(json.dumps(pigeonList))
    f.close()


def readConfig(probes):
    # Attempt to read a config if it exists, otherwise return an empty list
    pigeonList = []
    filename = "cp.conf"
    if os.path.exists(filename):
        f = open(filename, "r")
        rawData = f.read()
        pigeonStrings = json.loads(rawData)  # The config contains dictionaries of strings.
        for x in pigeonStrings:  # We need to convert them to dictionaries of actual probes and matches.
            for candidateProbe in probes:  # This has unpredictable behavior if a match can't be found.
                if x["probe"] == str(candidateProbe):
                    probe = candidateProbe
                    break
            for candidateMatch in probe.matches:
                if x["match"] == str(candidateMatch):
                    match = candidateMatch
                    break
            port = int(x["port"])
            pigeonList.append({"probe": probe, "match": match, "port": port})
    return pigeonList


def makeClayPigeon(probe, match, port):  # Created for multiProcessing
    try:
      return ClayPigeon(probe, match, port)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    probes = loadServiceDefs()
    z = []
    config = createConfig(probes)
    saveConfig(config)
    numberOfClayPigeons = len(config)
    for x in range(numberOfClayPigeons):
        # Uses multiprocessing to start listeners. Maybe there is a more efficient way?
        probe = config[x]["probe"]
        match = config[x]["match"]
        port = config[x]["port"]
        proc = Process(target=makeClayPigeon, args=(probe, match, port,))
        z.append(proc)
        z[x].start()
        sleep(.01) # Makes pigeons start in order so the list appears sorted


