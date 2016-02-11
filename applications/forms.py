from django import forms
from models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    buyer_Or_Seller = forms.ChoiceField(choices=[("","----"),("B","Buyer"),("S","Seller")])
    phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$', error_message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    address = forms.CharField()
    state = forms.CharField()
    zip_Code = forms.CharField(max_length=6)
    profile_picture = forms.ImageField()
    introduction = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name","last_name","password1",\
            "password2","email","phone","buyer_Or_Seller","address",\
            "state","zip_Code","introduction", "profile_picture")

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create User and UserProfile without database save")
        user = super(UserCreateForm, self).save(commit=True)
        user_profile = UserProfile(user=user, email=self.cleaned_data["email"], \
            first_name=self.cleaned_data["first_name"], last_name=self.cleaned_data["last_name"], \
            usertype=self.cleaned_data["buyer_Or_Seller"], phone=self.cleaned_data["phone"],\
            address=self.cleaned_data["address"], zipcode=self.cleaned_data["zip_Code"],
            state=self.cleaned_data["state"],introduction=self.cleaned_data["introduction"],\
            picture = self.cleaned_data["profile_picture"])
        user_profile.save()
        return user, user_profile

class AddProductForm(forms.ModelForm):
    price = forms.DecimalField(min_value=0.0)
    quantity = forms.IntegerField(min_value=1)
    picture = forms.ImageField(required=True)
    class Meta:
        model = Product
        fields = ['name','origin','category','unit','quantity','price','production_date','expiration_date','picture']

class ModifyProductForm(forms.ModelForm):
    price = forms.DecimalField(min_value=0.0)
    quantity = forms.IntegerField(min_value=1)
    class Meta:
        model = Product
        fields = ['name','origin','category','unit','quantity','price','production_date','expiration_date']

class UserModifyForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone","usertype","address",\
            "state","zipcode","introduction"]

class AddItemForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1)
    class Meta:
        model = Item
        fields = ["quantity"]

class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ["term","origin","category"]

class VerifyOrderForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = Order
        fields = ["payment", "message"]

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['deliveryfees']

class RateForm(forms.ModelForm):
    rate = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = Rating
        fields = ["rate", "comment"]

class DonateForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = Donation
        fields = ["amount", "message"]

class MessageForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = Message
        fields = ["text"]

class BestSellerForm(forms.Form):
    in_how_many_weeks = forms.IntegerField(min_value=0, required=False)
    CATE_CHOICES=(("-","-------"),("V","vegetable"),("F","fruit"),("M","meat"),("D","dairy"),("S","snack"),("O","other"))
    category = forms.ChoiceField(choices=CATE_CHOICES, required = False)
    number = forms.IntegerField(min_value=1)

class MostSearchForm(forms.Form):
    in_how_many_weeks = forms.IntegerField(min_value=0, required=False)
    number = forms.IntegerField(min_value=1)