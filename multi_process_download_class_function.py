"""
Download multiple files with multiple processes
"""
import multiprocessing
from urllib.request import urlopen, urlretrieve, HTTPError
import itertools

def download1(args):
    from urllib.request import urlopen, urlretrieve, HTTPError
    (url, path, verbose, id, nfile) = args
    if verbose: print("Getting [%d/%d %s]:\t%s"%(id+1, nfile, path, url))
    try: (a,b) = urlretrieve(url, path)
    except: (a, b) = ('', {'Expires':'-1'})
    return(True if b['Expires'].find('-1')<0 else False) 

def mdownload(url, path, n=5, verbose=True):
    """Download url and save them to paths with n threads"""
    import multiprocessing
    import itertools
    pool=multiprocessing.Pool(processes=n)
    res=pool.map(download1, zip(url,
                                path,
                                itertools.repeat(verbose,len(url)),
                                range(len(url)),
                                itertools.repeat(len(url),len(url))))
    
    pool.close(); pool.join()
    return(res)


# test fail
path = ['%s.txt'%i for i in range(50) ]
url = ['http://%s'%f for f in path]
a = mdownload(url=url, path=path, n=10)
assert(all(a)==False)
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
a = mdownload(url=url, path=path, n=10)
assert(all(a)==True)
print("\nSuccess test, pass\n")

