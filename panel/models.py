from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth.models import User
import uuid

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    country = CountryField(null=True, max_length=100)
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
    poster = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, db_constraint=False)
    image = models.ImageField(null = True)
    title = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=1000, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    proof = models.FileField()
    status = models.CharField(choices=statuses, max_length=12)
    posted_on = models.DateTimeField(auto_now_add=True, null=True)
    deadline = models.DateTimeField(null=True)
    donated_amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    
    def __str__(self):
        return str(self.id) + '-' + str(self.title)
    
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
    poster = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='poster', db_constraint=False)
    initial_price = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)
    highest_bidder = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='highestbidder', db_constraint=False)
    bid_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    status = models.CharField(choices=statuses, max_length=12)
    posted_on = models.DateTimeField(auto_now_add=True, null=True)
    deadline = models.DateTimeField(null=True)
    
    def __str__(self):
        return str(self.id) + '-' + str(self.title)

class Transaction(models.Model):
    transaction_id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4, max_length=256)
    payment_timestamp = models.DateTimeField(auto_now_add=True)
    payer = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    deal = models.ForeignKey(Deal, on_delete=models.DO_NOTHING, null=True)
    activity = models.ForeignKey(Activity, on_delete=models.DO_NOTHING, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)

    def __str__(self):
        return id
