# coding: utf-8
"""
Download Monthly FTR Auction Bid Data – 4 month delay
"""

import os, sys, re, pandas as pd, numpy as np
import multiprocessing
import itertools
from urllib.request import urlopen, urlretrieve, HTTPError
from bs4 import BeautifulSoup
import dateutil.parser

from IPython.display import clear_output


"""
Download multiple files with multiple processes
"""
def download1(args):
    (url, path, verbose, id, nfile) = args
    if verbose: print("Getting [%d/%d %s]:\t%s"%(id+1, nfile, path, url))
    try: (a,b) = urlretrieve(url, path)
    except: (a, b) = ('', {'Expires':'-1'})
    return(True if b['Expires'].find('-1')<0 else False) 

def mdownload(links, paths, n=5, verbose=True):
    """Download links and save them to paths with n threads"""
    pool=multiprocessing.Pool(processes=n)
    res=pool.map(download1, zip(links,
                                paths,
                                itertools.repeat(verbose,len(links)),
                                range(len(links)),
                                itertools.repeat(len(links),len(links))))
    
    pool.close(); pool.join()
    return(res)




"""
Download bids_ftr_auction_monthly
"""
def get_bids_ftr_auction_monthly_data(
    url="http://www.pjm.com/markets-and-operations/energy/real-time/historical-bid-data/bids-ftr-auction-monthly.aspx", 
    path="bids-ftr-auction-monthly", 
    refresh=True,
    ext='(csv|xls)'):
    
    """Download Monthly FTR Auction Bid Data.
    
    Args:
        url (Optional[str]): Link to the web page.
        path (Optional[str]): Path to save the files.
        refresh (Optional[bool]): If True download all and overwrite the files in path; else download new files.
        ext (Optional[str]): File extension(s) to search for, such as csv, xls.
    
    Note:
        Monthly FTR Auction Bid Data – 4 month delay is available from: 
        http://www.pjm.com/markets-and-operations/energy/real-time/historical-bid-data/bids-ftr-auction-monthly.aspx
        Columns description can be found on the same page: 
        http://www.pjm.com/~/media/markets-ops/energy/real-time/historical-bid-data/monthly-data-description.ashx"
        The table looks like this:
        ------------------------------------------------
        File                        Posting Date
        201509-pjm-bftramd._9.csv   12/1/2015 6:00:35 AM
        201509-pjm-bftramd._8.csv   12/1/2015 6:00:35 AM
        201509-pjm-bftramd._7.csv   12/1/2015 6:00:34 AM
        201509-pjm-bftramd._6.csv   12/1/2015 6:00:34 AM
        ------------------------------------------------
    
    """
    
    if not os.path.isdir(path): os.mkdir(path)
    
    r = urlopen(url)
    if r.url.lower().find("not-found") >= 0 :
        raise HTTPError(r.url, r.code, "not found", "", "")
    r = urlopen(url)
    soup = BeautifulSoup(r.read(), "html.parser")

    # The actural url to the csv table
    src = soup.find_all("iframe", src=re.compile("bids-ftr-auction-monthly", re.I))[0]["src"]
    iframeUrl = url.rsplit('/',1)[0] + '/' + src

    r = urlopen(iframeUrl)
    if r.url.lower().find("not-found") >= 0 :
        raise HTTPError(r.url, r.code, "not found", "", "")
    r = urlopen(iframeUrl)
    soup = BeautifulSoup(r.read(), "html.parser")

    ncsv = []
    for tab in soup.find_all("table"):
        number_of_rows = len(tab.find_all('a', href=re.compile('%s'%ext, re.I)))
        ncsv.append(number_of_rows)
        #print(number_of_rows)
    ind = np.argmax(ncsv)
    #print(ind)
    # the csv table in html format
    csvtab = soup.find_all("table")[ind]

    data = []
    for row in csvtab.find_all('tr'):
        if row.text.find('.csv') < 0 : continue
        cols = row.find_all('td')
        if len(cols) < 2 : continue
        fn = cols[0].text.strip()
        fhref = iframeUrl.rsplit('/',1)[0] + '/' + cols[0].a['href']
        timestamp = cols[1].text
        updateTime=dateutil.parser.parse(timestamp)
        data.append([fn, fhref, updateTime])
    #data

    csv_df = pd.DataFrame(data, columns = ["csv", "link", "timestamp"])
    csv_df['path'] = [os.path.join(path, f) for f in csv_df['csv']]
    csv_df['existed'] = [os.path.exists(f) for f in csv_df['path']]
    csv_df['updated'] = (-csv_df['existed']) | refresh
    #csv_df
    
    # download files with multiple processes
    idx = np.where(csv_df['updated'])[0].tolist()
    href = csv_df.loc[idx, 'link'].tolist()
    csv_path = csv_df.loc[idx, 'path'].tolist()
    res = mdownload(href, csv_path)
    csv_df.loc[idx, 'updated'] = res
    
    for i, row in csv_df.iterrows():
        if not row['updated']:
            print(index, row['csv'], "skip")
            continue
        print(index, row['csv'], "downloading")
        resp=urlretrieve(row['link'], os.path.join(path, row['csv']))
        if resp[1]['Expires'].lower().find('-1') >= 0:
            csv_df.ix[i, 'updated'] = False
    	
    return(csv_df)




def main():
    get_bids_ftr_auction_monthly_data()

if __name__ == '__main__':
    main()


    
