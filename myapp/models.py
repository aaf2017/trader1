from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Quote( models.Model):
    stock_name = models.CharField( max_length=30)
    price = models.DecimalField( max_digits=8, decimal_places=2)
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"name={self.stock_name}, price={self.price}, quantity={self.quantity}"




class Account(models.Model):
    
    """
    Account Object Specfication
    """
    
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    balance=models.FloatField(default=100000)
    created=models.DateTimeField(auto_now_add=True)
    last_modified=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} [${self.balance}]"

class Stock(models.Model):
    
    """
    Stock Object Model Specification
    """
    
    symbol=models.CharField(max_length=8)
    company_name=models.CharField(max_length=512)
    quantity=models.IntegerField()
    created=models.DateTimeField(auto_now_add=True)
    last_modified=models.DateTimeField(auto_now=True)
    account=models.ForeignKey(Account, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.account.id}: {self.symbol} {self.company_name} @ {self.quantity}"
