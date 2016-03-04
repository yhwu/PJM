class mtdownload(object):
    """Download multiple files using threads
    Put download jobs in queue and let threads grab one and execute until queue is empty.
    """

    def __init__(self, url=[], path=[], n=5, verbose=True):
        from threading import Thread
        from queue import Queue
        from urllib.request import urlopen, urlretrieve, HTTPError
        self.n = n
        self.verbose = verbose
        self.url = url
        self.path = path
        self.res = []

    def get_url(self): return(self.url)
    def get_path(self): return(self.path)
    def get_res(self): return(self.res)

    # job
    def __download1(self, i):
        if self.verbose: print("Getting [%d/%d %s]:\t%s"%(i+1, len(self.url), self.path[i], self.url[i]))
        try: (a,b) = urlretrieve(self.url[i], self.path[i])
        except: (a, b) = ('', {'Expires':'-1'})
        self.res[i] = True if b['Expires'].find('-1')<0 else False

    # thread wrapper
    def __threader(self, q):
        while not q.empty():
            self.__download1( q.get() )
            q.task_done()

    # setup queue and threads
    def download(self):
        from threading import Thread
        from queue import Queue

        self.res = [{} for x in range(len(self.url))]
        q = Queue()
        for i in range(len(self.url)): q.put(i)

        threads = []
        for k in range(self.n):
            t = Thread(target=self.__threader, args=(q,))  # args must be tuple
            t.daemon = True
            threads.append(t)
            t.start()

        q.join()
        for t in threads: t.join()

        return self



# test fail
path = ['%s.txt'%i for i in range(50) ]
url = ['http://%s'%f for f in path]
a = mtdownload(url=url, path=path, n=10).download()
assert(all(a.get_res())==False)
print("\nFail test, pass\n")

# test success
path = ['A0A009DWA6', 'A0A009DWB1', 'A0A009DWB5', 'A0A009DWC0', 'A0A009DWC5',
        'A0A009DWD0', 'A0A009DWD5', 'A0A009DWE1', 'A0A009DWE5', 'A0A009DWF0',
        'A0A009DWF5', 'A0A009DWF8', 'A0A009DWH2', 'A0A009DWH9', 'A0A009DWI3',
        'A0A009DWI9', 'A0A009DWJ5', 'A0A009DWJ9', 'A0A009DWL0', 'A0A009DWL5',
        'A0A009DWM1', 'A0A009DWM7', 'A0A009DWN1', 'A0A009DWN6', 'A0A009DWP3',
        'A0A009DWP7', 'A0A009DWV4', 'A0A009DWW0', 'A0A009DWW6', 'A0A009DWX0',
        'A0A009DWY5', 'A0A009DWZ0', 'A0A009DWZ5', 'A0A009DX00', 'A0A009DX03',
        'A0A009DX21', 'A0A009DXC5', 'A0A009DXE3', 'A0A009DXE7', 'A0A009DXG0',
        'A0A009DXG9', 'A0A009DXI7']

path = ['%s.txt'%f for f in path]
url = [ 'http://www.uniprot.org/uniprot/%s'%f for f in path]
a = mtdownload(url=url, path=path, n=4).download()
assert(all(a.get_res())==False)
print("\nSuccess test, pass\n")


