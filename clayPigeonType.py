from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from time import sleep, time

class ClayPigeon:

    @staticmethod
    def same(x,y):
        return x==y

    def __init__(self, probe):
        self.match = probe.getRandomMatch()
        self.port = probe.getRandomPort()
        self.probeResponse = self.match.example()
        print(probe.protocol+"/"+str(self.port))
        # print("Listen on",probe.protocol+"/"+str(self.port),"for",probe.probestring)
        # print("and respond with",self.probeResponse)
        # print("to emulate",self.match.service,self.match.versioninfo)
        while   True:
            if probe.protocol == 'TCP':
                self.s = socket(AF_INET,SOCK_STREAM)
            else:
                self.s = socket(AF_INET, SOCK_DGRAM)
            self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.s.bind(('127.0.0.1', self.port))
            if probe.protocol == 'TCP':
                self.s.listen(5)
            try:
                if probe.protocol == 'TCP':
                    connection, address = self.s.accept()
                    if probe.probename != 'NULL':
                        data = connection.recv(1536)
                        print("Received",data)
                else:
                    data, address = self.s.recvfrom(1536)
                    print("UDP Received",data,"from",address)
            except ConnectionResetError:
                connection.close()
                try:
                    self.s.shutdown(1)
                except OSError:
                    pass
                self.s.close()
                print("Closed!")
                continue
            dataString = data

            if probe.probename == 'NULL' or self.same(dataString, probe.probestring):
                try:
                    if probe.protocol == 'TCP':
                        connection.send(self.probeResponse)
                        print("Response", self.probeResponse)
                    else:
                        self.s.sendto(self.probeResponse, address)
                        print("UDP Response", self.probeResponse)
                except OSError:
                    pass
                while True:
                    try:
                        if probe.protocol == 'TCP':
                            getInput = connection.recv(1024)
                        else:
                            getInput, address = self.s.recvfrom(1536)
                    except OSError:
                        break
                    if not getInput:
                        break
                connection.close()
                try:
                    self.s.shutdown(1)
                except OSError:
                    pass
                self.s.close()
