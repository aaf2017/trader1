import json
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout #ADD, update_session_auth_hash /plus UPDATE def change_password IF DON'T WANT TO BE LOGGED OUT AFTER CHANGING PASSWORD/
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError

# Delete this comment
from .models import Quote, Stock, Account
from .forms import QuoteForm, SignUpForm, EditProfileForm

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
    IMGDIR = os.path.join( settings.BASE_DIR, 'myapp\static')
    plt.savefig( IMGDIR + '\my_plot.png')

def getStockInfo( request, symbol):
    #getInfo( symbol)
    return JsonResponse({"symbol": symbol })

@login_required
def home( request):
    try:
        account = Account.objects.get(user=request.user)
        stocks = Stock.objects.filter(account=account).order_by('-created').all()
        stock_symbols = stocks.values_list('symbol', 'quantity')
        account_value = sum([yf.Ticker(stock[0]).info["ask"]*stock[1] for stock in stock_symbols])
    except Account.DoesNotExist:
        account = None
        stocks = None
        
    context = {
        'account': account,
        'stocks': stocks[:5],
        'stock_count': len(stocks) if stocks else 0,
        'account_value': account_value + account.balance,
    }
        
    return render( request, 'myapp/home.html', context)
    
def explore(request):
    return render(request, 'myapp/explore.html', {})

@login_required
@csrf_exempt
def trade( request):
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
    if request.method == 'POST':
        if request.POST.get('action') == "search":
            symbol = request.POST.get("symbol")
            stock_quote = yf.Ticker(symbol).info
            stock_quote=dict(
                exDividendDate=stock_quote["exDividendDate"] if stock_quote["exDividendDate"] else "",
                open=stock_quote["open"],
                ask=stock_quote["ask"],
                volume=stock_quote["volume"],
                fiftyTwoWeekHigh=stock_quote["fiftyTwoWeekHigh"],
                fiftyTwoWeekLow=stock_quote["fiftyTwoWeekLow"],
                fiftyTwoWeekChange=stock_quote["52WeekChange"],
                bid=stock_quote["bid"],
                previousClose=stock_quote["previousClose"],
                symbol=stock_quote["symbol"],
                sharesOutstanding=stock_quote["sharesOutstanding"],
                regularMarketPrice=stock_quote["regularMarketPrice"],
                dividendYield=stock_quote["dividendYield"] if stock_quote["dividendYield"] else "",
            )
            return render( request, 'myapp/trade.html', {"stock_quote": stock_quote, "account": account})
        if request.POST.get('action') == "buy":
            pass
    return render( request, 'myapp/trade.html', {"account": account})

@login_required
@csrf_exempt
def buy_stocks( request):
    data = json.loads(request.body)
    account = Account.objects.get(user=request.user)
    print(data["quantity"])
    if account.balance > data["quantity"]*data["ask"]:    
        company_name = yf.Ticker(data["symbol"]).info["longName"]
        params = dict(symbol=data["symbol"], quantity=data['quantity'], purchase_price=data["ask"], account=account, company_name=company_name)
        # make sure that the stock doesn't exist (by symbol and purchase price) and if it does just update the quantity
        stock = Stock.objects.create(**params)
        # update the balance 
        ret = {k:v for k,v in stock.__dict__.items() if k not in ["_state", "created", "last_modified"]}
        return JsonResponse(ret, status=200)
    if account.balance < data["quantity"]*data["ask"]:
        return 

@login_required
def portfolio( request):
    try:
        account = Account.objects.get(user=request.user)
        stocks = Stock.objects.filter(account=account).order_by('symbol').all()
        stock_symbols = stocks.values_list('symbol', flat=True)
        stock_quotes = [yf.Ticker(symbol).info for symbol in stock_symbols]
    except Account.DoesNotExist:
        account = None
        stocks = None     
    return render(request, 'myapp/portfolio.html', {'account': account, 'stocks': stocks, 'stock_count': len(stocks) if stocks else 0})

def quotes( request):
    quotes = Quote.objects.all();
    context = { 'quotes' : quotes}
    return render(request, 'myapp/quotes.html', context)

def quote( request):
    print('method started')
    if request.method == 'POST':
        quoteForm = QuoteForm( request.POST)
        if quoteForm.is_valid() == False:
            return HttpResponse( quoteForm.errors)
        quoteForm.save();
        return redirect("/quotes");
    elif request.method == 'GET':
        quoteForm = QuoteForm()
    context = { 'quoteForm' : quoteForm}
    return render( request, 'myapp/quote.html', context)

def getPrice(request):
    data = json.loads(request.body)
    print('getPrice: id=', data["name"])
    ticker = yf.Ticker(data["name"])
    print('getPrice2: ticker=', ticker)
    retval = { "price" : ticker.info['regularMarketPrice']}
    print('getPrice3')
    return JsonResponse(retval)

# USER AUTHENTIFICATION - LOGIN/LOGOUT

def login_user( request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('You have been successfully logged in!'))
            return redirect('home')
            
        else:
            messages.success(request, ('Error logging in. Please try again...'))
            return redirect('login')
    else:
        return render( request, 'myapp/login.html', {})
    
def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out...'))
    return redirect('home')



# USER REGISTRATION/SIGNUP FORM

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            Account.objects.create(user=user, balance=1000)
            login(request, user)
            messages.success(request, ('You have successfully completed your registration!'))
            return redirect('home')
    else:
        form = SignUpForm()
        
    context = {'form': form}
    return render( request, 'myapp/register.html', context)
    
    
    #EDIT USER PROFILE/CHANGE PASSWORD
    
   
@login_required   
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, ('You have successfully edited your profile.'))
            return redirect('home')
    else:
        form = EditProfileForm(instance=request.user)
        
    context = {'form': form}
    return render( request, 'myapp/edit_profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            #update_session_auth_hash(request, form.user)
            messages.success(request, ('You have successfully edited your password.'))
            return redirect('home')
    else:
        form = PasswordChangeForm(user=request.user)
        
    context = {'form': form}
    return render( request, 'myapp/change_password.html', context)
    
