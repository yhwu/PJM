class mtdownload():
    '''Download multiple files using threads
    Put download jobs in queue and let threads grab one and execute until queue is empty.
    '''

    # job
    def download1(i, url, path, verbose, nfile):
        from urllib.request import urlopen, urlretrieve, HTTPError
        if verbose: # noinspection PyTypeChecker
            print("Getting [%d/%d %s]:\t%s"%(i+1, nfile, path, url))
        try: (a,b) = urlretrieve(url, path)
        except: (a, b) = ('', {'Expires':'-1'})
        return( True if b['Expires'].find('-1')<0 else False )

    # thread wrapper
    def threader(q, res):
        while not q.empty():
        #while True: # never finish
            f, args = q.get()
            qres = f(*args)
            res[args[0]] = qres
            q.task_done()

    # setup queue and threads
    def download(url, path, verbose=True, n=5):
        from threading import Thread
        from queue import Queue

        nq = len(url)
        res = [{} for x in range(nq)]
        q = Queue()
        for i in range(nq):
            q.put( (mtdownload.download1, [i, url[i], path[i], verbose, nq]) )

        threads = []
        for k in range(n):
            t = Thread(target=mtdownload.threader, args=(q, res))
            t.daemon = True
            threads.append(t)
            t.start()

        q.join()
        for t in threads: t.join()

        return(res)

# test fail
path = [ '%s.txt'%i for i in range(50) ]
url = ['http://%s'%f for f in path]
r = mtdownload.download(url=url, path=path, verbose=True, n=10)
print(r)
assert(all(r)==False)
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
r = mtdownload.download(url=url, path=path, verbose=True, n=10)
print(r)
assert(all(r)==True)
print("\nSuccess test, pass\n")

