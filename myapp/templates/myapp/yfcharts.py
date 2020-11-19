import yfinance as yf
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from django.conf import settings
import os

#stock = yf.Ticker('SPCE')
#print(dir(stock))

def getInfo( symbol):
    STARTDATE = '2014-01-01'
    ENDDATE = str( datetime.now().strftime('%Y-%m-%d'))
    company = yf.download( symbol, start=STARTDATE, end=ENDDATE)
    hist = company['Adj Close']
    hist.plot()
    plt.xlabel("Date")
    plt.ylabel("Adjusted")
    plt.title( symbol + " Price Data")
    #plt.show()
    #IMGDIR = os.path.join( settings.BASE_DIR, 'example\static')
    IMGDIR = os.path.join( settings.BASE_DIR, 'myapp\static')
    plt.savefig( IMGDIR + '\my_plot.png')
getInfo( 'MSFT')




