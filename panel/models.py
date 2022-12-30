from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth.models import User
import uuid

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, primary_key=True)
    country = CountryField()
    balance = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Category(models.Model):
    name = models.CharField(max_length=40)
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    statuses = [
        ('in-need', 'in-need'),
        ('achieved', 'achieved'),
        ('failed', 'failed')
    ]
    poster = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    image = models.ImageField(null = True)
    title = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=1000, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    proof = models.FileField()
    status = models.CharField(choices=statuses, max_length=12)
    deadline = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.id + '-' + self.title
    
    def get_image_url(self):
        return self.image.url

class Deal(models.Model):
    statuses = [
        ('available', 'available'),
        ('sold', 'sold'),
        ('closed', 'closed')
    ]
    image = models.ImageField(null=True)
    title = models.CharField(max_length=50, null=True)
    poster = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='poster')
    initial_price = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)
    highest_bidder = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='highestbidder')
    bid_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    status = models.CharField(choices=statuses, max_length=12)
    deadline = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.id + '-' + self.title

class Transaction(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4, max_length=256)
    payment_timestamp = models.DateTimeField(auto_now_add=True)
    payer = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    deal = models.ForeignKey(Deal, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)

    def __str__(self):
        return id
