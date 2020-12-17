import exrex

class Match:

    def __init__(self, service, pattern, versioninfo, softmatch):
        self.service = service
        self.pattern = pattern
        self.versioninfo = versioninfo
        self.softmatch = softmatch

    def __str__(self):
        if self.softmatch:
            x = 'softmatch '
        else:
            x = 'match '
        x += self.service + ' ' + self.versioninfo + ' ' + self.pattern
        return x.rstrip('\n')

    def example(self):
        sample = exrex.getone(self.pattern)
        return bytes(sample,'latin-1')
