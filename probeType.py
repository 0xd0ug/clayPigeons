from copy import deepcopy
import random

class Probe:

    def __init__(self, protocol, probename, probestring, matches=[], ports=[], sslports=[]):
        self.protocol = protocol
        self.probename = probename
        self.probestring = probestring
        self.matches = deepcopy(matches)
        self.ports = deepcopy(ports)
        self.sslports = deepcopy(sslports)

    def __str__(self):
        x = 'Probe ' + self.protocol + ' ' + self.probename + ' ' + self.probestring + '\n'
        for a in self.matches:
            x += '  ' + str(a)+'\n'
        if self.ports != []:
            x += '  ports ' + ",".join([str(element) for element in self.ports]) + '\n'
        if self.sslports != []:
            x += '  sslports ' + ",".join([str(element) for element in self.sslports])
        return x.rstrip('\n')

    def getRandomMatch(self):
        return random.choice(self.matches)

    def getRandomPort(self):
        # Randomly choose from an expected port
        if self.ports != []:
            port = random.choice(self.ports)
        # And if no ports are specified, just pick one in a high range.
        else:
            port = random.randint(10000,11000)
        # usedPorts.append(port)
        return port
