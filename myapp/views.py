import json
#import matplotlib               #added after RuntimeError: main thread is not in main loop
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import os
import io
import base64, urllib

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

from .models import Stock, Account
from .forms import SignUpForm, EditProfileForm

def get_stock_graph(symbol):
    STARTDATE = '2020-01-01'
    ENDDATE = str( datetime.now().strftime('%Y-%m-%d'))
    company = yf.download( symbol, start=STARTDATE, end=ENDDATE)
    hist = company['Adj Close']
    hist.plot()
    plt.xlabel("Date")
    plt.ylabel("Adjusted")
    plt.title( symbol + " Price Data")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def getStockInfo( request, symbol):
    return JsonResponse({"symbol": symbol })

def home( request):
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        stocks = Stock.objects.filter(account=account).order_by('-created').all()[:5]
        stock_symbols = stocks.values_list('symbol', 'quantity')
        account_value = sum([yf.Ticker(stock[0]).info["ask"]*stock[1] for stock in stock_symbols])
        account_value += account.balance
    else:
        account = None
        stocks = []
        account_value = 0
        
    context = {
        'account': account,
        'stocks': stocks,
        'stock_count': len(stocks) if stocks else 0,
        'account_value': account_value,
    }
        
    return render( request, 'myapp/home.html', context)

def get_stock_info(stocks):
    ret = []
    for stock in stocks:
        stock_quote = yf.Ticker(stock.symbol).info
        sell_price = stock_quote["bid"]
        ret.append({"symbol": stock.symbol, "company_name": stock.company_name, "quantity": stock.quantity, "value": sell_price * stock.quantity})
    return ret

@login_required
@csrf_exempt
def trade(request):
    account = None
    stocks = []
    message = ""
    if request.user.is_authenticated:
        print('trade:authenticated')
        account = Account.objects.get(user=request.user)
        all_stocks = Stock.objects.filter(account=account)
        stocks = get_stock_info(all_stocks)
    if request.method == 'POST':
        print('trade:POST')
        if request.POST.get('action') == "search":
            symbol = request.POST.get("symbol")
            print('trade:POST symbol='+ symbol)
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
            graph = get_stock_graph(symbol)
            return render( request, 'myapp/trade.html', {"stock_quote": stock_quote, "account": account, "stocks": stocks, "image": graph})
        if request.POST.get('action') == "sell":
            print('trade:POST action=sell')
            quantity = int(request.POST.get("quantity"))
            print('trade:POST quantity='+str(quantity))

            symbol = request.POST.get("stock")
            print('trade:POST symbol='+str(symbol))

            if symbol == "":
                return render( request, 'myapp/trade.html', {"account": account, "stocks": stocks})
            stock = Stock.objects.get(account=account, symbol=symbol)
            if quantity <= stock.quantity:   
                print('trade:quantity='+str(quantity))
                print('trade:stock.quantity='+str(stock.quantity))
 
                stock_quote = yf.Ticker(symbol).info
                sell_price = stock_quote["bid"]
                cash = quantity * sell_price
                account.balance += cash
                account.save()
                filtered_stock = Stock.objects.get(account=account, symbol=symbol)
                filtered_stock.quantity -= quantity
                filtered_stock.save()
                stocks = get_stock_info(Stock.objects.filter(account=account))
                message = "Succesfully sold stock"
            else:
                message = "That is more quantity than you have on your balance"
        if request.POST.get('action') == "buy":
            quantity = int(request.POST.get("quantity"))
            symbol = request.POST.get("symbol")
            account = Account.objects.get(user=request.user)
            stock_quote = yf.Ticker(symbol).info
            total_price = quantity*stock_quote["ask"]
            if account.balance > total_price:  
                stock = Stock.objects.filter(symbol=symbol, account=account)  
                if stock:
                    stock = stock[0]
                    stock.quantity += quantity
                    stock.save()
                else:
                    company_name = stock_quote["longName"]
                    # make sure that the stock doesn't exist (by symbol and purchase price) and if it does just update the quantity
                    stock = Stock.objects.create(symbol=symbol, quantity=quantity, account=account, company_name=company_name)
                # update the balance 
                account.balance -= total_price
                account.save()
                stocks = get_stock_info(Stock.objects.filter(account=account))
                message = "Succesfully bought stock"
            else:
                message = "Insufficient funds for buying stock"
    return render( request, 'myapp/trade.html', {"account": account, "stocks": stocks, "message": message})

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
            Account.objects.create(user=user, balance=100000)
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

    
