pip install pandas-datareader
pip install pandas
pip install numpy
pip install matplotlib
pip install datetime
pip install yfinance --upgrade --no-cache-dir
django-admin startproject djangoyfinance
cd djangoyfinance
django-admin startapp example










Quotes/views.py

from django.shortcuts import render
from django.http import request, JsonResponse
from . import models

def create_portfolio(request):
    pass

def fetch_portfolio(request):
    pass

def trade_stocks(request):
    pass

""""



models.py

from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    
    """
    Account Object Specfication
    
    """
    
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    balance=models.FloatField(default=1000)
    created=models.DateTimeField(auto_add_now=True)
    last_modified=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} [${self.balance}]"

class Stock(models.Model):
    
    """
    Stock Object Model Specification
    
    """
    
    symbol=models.Charfield(max_length=8)
    company_name=models.Charfield(max_lenght=512)
    purchase_price=models.FloatField()
    quantity=models.IntegerField()
    created=models.DateTimeField(auto_add_now=True)
    last_modified=models.DateTimeField(auto_add=True)
    account=models.OneToOneField(Account, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.account.id}: {self.symbol} {self.company_name} ${self.purchase_price} @ {self.quantity}"




""""
Superuser=User Commands:

""""
In shell:
python manage.py shell
from django.contrib.auth.models import User
User.objects.all()
User.objects.all(delete)
User._meta.get_fields
User.objects.(filter)
User.objects.filter(username='tarder1')
User.objects.filter(username='trader1').update(is_superuser=True)

Exite shell:
exit




"""""""""""""

Order of yfshart.py

"""""""""""""

import yfinance as yf
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from django.conf import settings
import os

#stock = yf.Ticker('SPCE')                  1) print this first (green > data in the terminal)
#print(dir(stock))

def getInfo( symbol):                                                       2) same - gives the chart img
    company = yf.download( symbol, start='2014-01-01', end='2020-11-18')
    hist = company['Adj Close']
    hist.plot()
    plt.xlabel("Date")
    plt.xlabel("Adjasted")
    plt.title( symbol + " Price Data")
    plt.show()
getInfo( 'FB')


3) Modified:


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
    IMGDIR = os.path.join( settings.BASE_DIR, 'trader1\static')
    plt.savefig( IMGDIR + '\my_plot.png')
getInfo( 'MSFT')


""""""""""''
middleware.py
""""""""""""""

import re

from django.conf import settings
from django.shortcuts import redirect

EXEMPT_URLS = [re.compile(settings.LOGIN_USER_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_USER_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.LOGIN_USER_EXEMPT_URLS]
    
class LoginRequireMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    def process_view(self, request, view_func, view_args, view_kwards):
        assert hasattr(request, 'user')
        path = request.path_info
        print(path)
        
        if not request.user.is_authenticated():
            if not any(url.match(path) for url in EXEMPT_URLS):
                return redirect(settings.LOGIN_USER_URL)