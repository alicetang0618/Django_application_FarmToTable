from django.db import models
from django. contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

import logging
logr = logging.getLogger(__name__)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	email = models.EmailField()
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	TYPE_CHOICES=(
		("B","Buyer"),("S","Seller"))
	usertype = models.CharField(max_length=1, choices=TYPE_CHOICES)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone = models.CharField(max_length=15, validators=[phone_regex])
	address = models.CharField(max_length=100)
	state = models.CharField(max_length=15)
	zipcode = models.CharField(max_length=6)
	picture = models.ImageField(upload_to="profile_images", blank = True, null=True)
	introduction = models.TextField(blank=True)
	account = models.DecimalField(blank=True, max_digits=8, decimal_places=2, default=100.00)
	shopping_cart = models.ManyToManyField('Item', blank=True)
	pending_payment = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user = u)[0])


class Product(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey('UserProfile', null=True, related_name="owner")
    liked_by = models.ManyToManyField('UserProfile', null=True, related_name="liked_by")
    CATE_CHOICES=(("V","vegetable"),("F","fruit"),("M","meat"),("D","dairy"),("S","snack"),("O","other"))
    category = models.CharField(max_length=1, choices=CATE_CHOICES)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    QUANT_CHOICES = (("Kg", "kg"), ("Lb","lb"), ("Crate","crate"), ("Dozen","dozen"), ("Each","each"))
    unit = models.CharField(max_length=5, choices = QUANT_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.00)])
    production_date = models.DateTimeField(default=datetime.now)
    expiration_date = models.DateTimeField()
    description = models.TextField()
    picture = models.ImageField(upload_to="product_images", blank = True, null=True)
    origin = models.CharField(max_length=30)


class Order(models.Model):
	buyer = models.ForeignKey('UserProfile', related_name='buyer')
	seller = models.ForeignKey('UserProfile', related_name='seller')
	items = models.ManyToManyField('Item', blank=True, null=True)
	STATUS_CHOICES= (("X","pending"),("P","paid"),("S","submitted by user"),\
		("CA","cancelled by user"),("CS","comfirmed by seller"),("D","delivered"),\
		("R","received by buyer"))
	status = models.CharField(max_length=1, choices=STATUS_CHOICES)
	ordertime = models.DateTimeField(blank=True, null=True)
	delivertime = models.DateTimeField(default=datetime.now)
	receivetime = models.DateTimeField(blank=True, null=True)
	deliveryfees = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	PAY_CHOICES = (("O","pay online"),("CD","cash on delivery"),("PD","pay on delivery"))
	payment = models.CharField(max_length=2, choices=PAY_CHOICES, blank=True, null=True, default=0)
	message = models.TextField(blank=True, null=True)


class Rating(models.Model):
	rater = models.ForeignKey('UserProfile', related_name='rater', blank=True, null=True)
	rated = models.ForeignKey('UserProfile', related_name='rated', blank=True, null=True)
	product = models.ForeignKey('Product', blank=True, null=True)
	rate = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1),MaxValueValidator(5)])
	comment = models.TextField(blank=True, null=True)
	time = models.DateTimeField(default=datetime.now)


class Search(models.Model):
	#enable visitors to search and save their search terms
	user = models.ForeignKey("UserProfile", null=True, blank = True) 
	term = models.CharField(max_length=50, null = True, blank = True)
	origin = models.CharField(max_length = 30, null=True, blank = True)
	CATE_CHOICES=(("V","vegetable"),("F","fruit"),("M","meat"),("D","dairy"),("S","snack"),("O","other"))
	category = models.CharField(max_length=1, choices=CATE_CHOICES, blank=True, null=True)
	time = models.DateTimeField(default=datetime.now)


class Item(models.Model):
	product = models.ForeignKey('Product', blank=True, null=True)
	quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])


class Donation(models.Model):
	donor = models.ForeignKey("UserProfile", related_name='donor', null=True, blank = True)
	receipient = models.ForeignKey("UserProfile", related_name='receipient', null=True, blank = True)
	time = models.DateTimeField(default = datetime.now)
	amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, default=0.00)
	message = models.TextField(blank=True, null=True)


class Message(models.Model):
	sender = models.ForeignKey("UserProfile", related_name='sender', null=True, blank = True)
	receiver = models.ForeignKey("UserProfile", related_name='receiver', null=True, blank = True)
	text = models.TextField(blank=True, null=True)
	time = models.DateTimeField(default = datetime.now)