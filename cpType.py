from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR


class ClayPigeon:

    @staticmethod
    def same(x, y):
        return x == y

    def __init__(self, probe, match, port):  # Starts and runs listener for clay pigeon
        self.match = match
        self.port = port
        self.probeResponse = self.match.example()
        firstOpen = True
        portString = probe.protocol + "/" + str(self.port) + ':' + probe.probename
        while True:
            if probe.protocol == 'TCP':
                self.s = socket(AF_INET, SOCK_STREAM)
            else:
                self.s = socket(AF_INET, SOCK_DGRAM)
            self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # Try to get the port open
            try:
                self.s.bind(('127.0.0.1', self.port))  # Binds only to localhost.
            except PermissionError:
                # Probably trying to open port <=1024 without root privileges
                self.s.close()
                print(portString + ": Can't open port (root may be required)?")
                break
            except OSError:
                # Probably opened a duplicate port (either another pigeon or a real service)
                self.s.close()
                print(portString + ": Port may already be in use.")
                break
            if firstOpen:
                # Print port info if this is the first time through (this loop repeats for each connection)
                print(portString)
                firstOpen = False
            if probe.protocol == 'TCP':
                # TCP port means you need to listen, UDP just takes data.
                self.s.listen(5)
            try:
                # Try to receive data from TCP or UDP
                if probe.protocol == 'TCP':
                    connection, address = self.s.accept()
                    if probe.probename != 'NULL':
                        data = connection.recv(1536)
                        print(portString + ": Received", data)
                else:
                    data, address = self.s.recvfrom(1536)
                    print(portString + ": Received", data, "from", address)
            except ConnectionResetError:
                connection.close()
                try:
                    self.s.shutdown(1)
                except OSError:
                    pass
                self.s.close()
                continue
            # If this is a null probe or if the input matches the signature, send the response
            if probe.probename == 'NULL' or self.same(data, probe.probestring):
                try:
                    if probe.protocol == 'TCP':
                        connection.send(self.probeResponse)
                        print("*" + portString + ": Response", self.probeResponse)
                    else:
                        self.s.sendto(self.probeResponse, address)
                        print("*" + portString + ": Response", self.probeResponse)
                except OSError:
                    pass
                # Clean up by getting anything else from the port.
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
