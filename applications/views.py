from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django import forms
from PIL import Image as PImage
from os.path import join as pjoin
from datetime import datetime, timedelta
from nltk import word_tokenize
import pylab as plt

from forms import *
from models import *
from util import *
from recommend import recommend_sim_user, recommend_sim_product
from search import build_search_engine, term_and_origin, word_list

search_engine = build_search_engine()


# Main Pages
def intro(request):
    if request.user.is_authenticated():
        return redirect("/home/")
    return render(request,'intro.html',{})


def home(request):
    if request.method == 'POST' and request.POST.get('search'):
        form = SearchForm(request.POST)
        if form.is_valid():  
            search = form.save(commit = False)
            if request.user.is_authenticated():
                search.user = request.user.profile # if the user is logged in
            search.save()  
            return redirect("/search/"+str(search.id))
    else:
        form = SearchForm()  
    c = {'form':form}    
    return render(request,'home.html',c)


# User Account Functions
def register(request):
    if not request.user.is_authenticated():
        if request.method == 'POST':
            form = UserCreateForm(request.POST, request.FILES)
            if form.is_valid():
                new_user = UserProfile(picture =request.FILES['profile_picture'])
                new_user = form.save()
                return redirect("/login/")
        else:
            form = UserCreateForm()
        c = {
            'form': form
        }
    else:
        c={}
    return render(request, "register.html", c, context_instance = RequestContext(request))


def login(request):
    if request.user.is_authenticated():
        return render(request,'login.html',{})
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return redirect("/home/")
                else:
                    return redirect("/login/")
            else:
                return redirect("/login/")
        else:
            return render_to_response('login.html', {}, RequestContext(request))


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
        return render(request, 'logout.html', {})
    else:
        return redirect("/home/")


# User Functions
def my_profile(request):
    if request.user.is_authenticated():
        user = request.user.profile
        c = {
            'user': user
        }
    else:
        return redirect("/login/")
        c={}
    return render(request,"my_profile.html", c)


def modify_profile(request):
    if request.method == 'POST' and request.POST.get('profile'):
        form = UserModifyForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('/my_profile/')
    else:
        form = UserModifyForm(instance=request.user.profile)
    c = {
        'form': form
    }
    return render(request, 'modify_profile.html', c)


def profile(request, user_id):
    viewuser = UserProfile.objects.get(id=user_id)
    products = Product.objects.filter(owner=viewuser)
    donations = Donation.objects.filter(donor=viewuser)
    ratings = Rating.objects.filter(rated=viewuser)
    if request.method == 'POST' and request.POST.get('rate_submit'):
        rateform = RateForm(request.POST)       
        if rateform.is_valid(): 
            rate = rateform.save() 
            rate.rater = request.user.profile 
            rate.rated = viewuser
            rate.save()
    else:
        rateform = RateForm()
    if request.method == 'POST' and request.POST.get('message_submit'):
        messageform = MessageForm(request.POST)       
        if messageform.is_valid(): 
            message = messageform.save() 
            message.sender = request.user.profile 
            message.receiver = viewuser
            message.save()
    else:
        messageform = MessageForm()
    if request.method == 'POST' and request.POST.get('donate'):
        form = DonateForm(request.POST)       
        if form.is_valid(): 
            donate = form.save() 
            donate.donor = request.user.profile 
            donate.receipient = viewuser
            donate.save()
            if donate.donor.account < donate.amount:
                donate.delete()
                return redirect("/error_account/")
            donate.donor.account -= donate.amount
            donate.donor.save()
            donate.receipient.account += donate.amount
            donate.receipient.save()
    else:
        form = DonateForm() 
    c = {
        'viewuser': viewuser,
        'products': products,
        'num_product': len(products),
        'donations': donations,
        'num_donation': len(donations),
        'rateform': rateform,
        'donateform': form,
        'ratings': ratings,
        'messageform': messageform,
        'num_rating': len(ratings)
    }
    return render(request,"profile.html",c)


def my_messages(request):
    if not request.user.is_authenticated():
        return redirect("/login/")
    messages = Message.objects.filter(receiver=request.user.profile).order_by('time').reverse()
    sent = Message.objects.filter(sender=request.user.profile).order_by('time').reverse()
    c={
        "receive": messages,
        "num_rece": len(messages),
        "sent": sent,
        "num_sent": len(sent)
    }
    return render(request,"my_messages.html",c)


def message(request, message_id):
    message=Message.objects.get(id=message_id)
    if request.method == 'POST':
        messageform = MessageForm(request.POST)      
        if messageform.is_valid():
            reply = messageform.save()
            reply.sender = request.user.profile
            if message.sender == request.user.profile:
                reply.receiver = message.receiver
            else:
                reply.receiver = message.sender
            reply.save()
    else:
        messageform = MessageForm()
        reply = None
    c = {
        'message': message,
        'reply': reply,
        'messageform': messageform
    }
    return render(request,"message.html",c)


def finance(request):
    if not request.user.is_authenticated():
        return redirect("/login/")
    user = request.user.profile
    if user.usertype == "B":
        c = {
            "net": user.account-user.pending_payment,
            "month_spend": total_spending(user, 4),
            "3_month_spend": total_spending(user, 12),
            "year_spend": total_spending(user, 48)
        }
    else:
        c = {
            "net": user.account-user.pending_payment,
            "month_reve": total_revenue(user, 4),
            "3_month_reve": total_revenue(user, 12),
            "year_reve": total_revenue(user, 48)
        }
    return render(request,"finance.html", c)


def spend_categories(request):
    user = request.user.profile
    start_time = datetime.now() - timedelta(weeks=12)
    dic = calculate_spending_by_type(user, start_time)
    labels = [x for (x,y) in dic.items()]
    fractions = [y for (x,y) in dic.items()]
    response = HttpResponse(content_type='image/svg+xml')
    plt.clf()
    plt.figure(figsize=(6, 6))
    plt.pie(fractions, labels=labels, autopct='%1.1f%%')
    plt.savefig(response, format='svg')
    plt.close()
    return response


def revenue_categories(request):
    user = request.user.profile
    start_time = datetime.now() - timedelta(weeks=12)
    dic = calculate_revenue_by_type(user, start_time)
    xs = [x for (x,y) in dic.items()]
    ys = [y for (x,y) in dic.items()]
    response = HttpResponse(content_type='image/svg+xml')
    plt.clf()
    plt.figure(figsize=(6, 6))
    plt.bar(range(len(ys)), ys, width=0.5, alpha=0.5)
    plt.xticks(range(len(xs)),xs)
    plt.savefig(response, format='svg')
    plt.close()
    return response


def my_products(request):
    products = Product.objects.filter(owner=request.user.profile)
    num = len(products)
    c = {
        'products':products,
        'num':num
    }
    return render(request, "my_products.html", c)


def add_product(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = AddProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = Product(picture = request.FILES['picture'])
                product = form.save()
                product.owner=request.user.profile
                product.save()
                search_engine = build_search_engine()
                return redirect("/my_products/")
        else:
            form = AddProductForm()
        c = {
            'form': form
        }
        return render(request, 'add_product.html', c)
    else:
        return redirect("/login/")


def modify_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404('Product does not exist')
    modified=False
    if request.method == 'POST':
        form = ModifyProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            modified = True
    else:
        form = ModifyProductForm(instance=product)
    c = {
        'product':product,
        'form': form,
        'modified':modified
    }
    return render(request, 'modify_product.html', c)


def product(request,product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404('Product does not exist')

    if request.method == 'POST' and request.POST.get('remove'):
        product.delete()
        return redirect('/my_products/')

    if request.method == 'POST' and request.POST.get('modify'):
        url='/modify_product/'+str(product_id)
        return redirect(url)

    if request.method == 'POST' and request.POST.get('like'):
        if not request.user.is_authenticated():
            return redirect("/login/")
        if request.user.profile not in product.liked_by.all():
            product.liked_by.add(request.user.profile)
            product.save()
        return redirect("/product/"+str(product_id))

    if request.method == 'POST' and request.POST.get('cart'):
        return redirect("/add_to_cart/"+str(product_id))

    currentrating = Rating.objects.filter(product = product)
    num = 0
    totalrating = 0
    for rate in currentrating:
        totalrating += rate.rate
        num += 1
    if num == 0:
        avgrating = 0
    else: 
        avgrating = int(totalrating/num)

    liked = False
    if request.user.is_authenticated() and request.user.profile in product.liked_by.all():
        liked = True

    buyer = False
    if request.user.is_authenticated():
        for order in Order.objects.filter(buyer=request.user.profile, status='R'):
            for item in order.items.all():
                if item.product == product:
                    buyer = True
                    break

    if request.method == 'POST' and request.POST.get('rate_submit'):
        form = RateForm(request.POST)       
        if form.is_valid(): 
            rate = form.save() 
            rate.rater = request.user.profile 
            rate.product = product
            rate.save()
            return redirect("/product/"+str(product_id))
    else:
        form = RateForm() 

    c = {
        'product': product,
        'liked': liked,
        'buyer': buyer,
        'ratings': currentrating,
        'num_rating': len(currentrating),
        'avgrating':avgrating,
        'rateform': form,
        'sold': quantity_sold(product, datetime.now()-timedelta(weeks=12))
    }

    return render(request, 'product.html', c)


def my_orders(request):
    if not request.user.is_authenticated():
        return redirect("/login/")
    user=request.user.profile
    if user.usertype == 'B':
        orders=Order.objects.filter(buyer=user)
    else:
        orders=Order.objects.filter(seller=user)
    num = len(orders)
    c={
        'orders': orders,
        'num': num
    }
    return render(request, "my_orders.html", c)


def like(request):
    user = request.user.profile
    like = []
    for product in Product.objects.all():
        if user in product.liked_by.all():
            like.append(product)
    c={
        "likes": like,
        "num": len(like)
    }
    return render(request,"like.html",c)


# Transaction Functions
def add_to_cart(request, product_id):
    cart = request.user.profile.shopping_cart
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            item.product = product
            item.save()
            if item.quantity > product.quantity:
                return redirect("/error_quant/"+str(item.id))
            cart.add(item)
            if len(cart.all())>0:
                for i in cart.all():
                    if i != item:
                        if item.product.id == i.product.id:
                            i.quantity += item.quantity
                            item.delete()
                            i.save()
                            break
            return redirect("/product/"+str(product_id))
    else:
        form = AddItemForm()
    c = {
        'form': form,
        'product': product,
        'error': "cart"
    }
    return render(request, "add_to_cart.html", c)


def shopping_cart(request):
    items = request.user.profile.shopping_cart.all()
    num = len(items)
    amount = 0
    for item in items:
        amount += item.product.price*item.quantity
    if request.method == 'POST' and request.POST.get('checkout'):
        return redirect("/checkout/")
    if request.method == 'POST' and request.POST.get('clear'):
        for item in items:
            item.delete()
        return redirect("/shopping_cart/")
    c = {
        'items':items,
        'num':num,
        'amount':amount
    }
    return render(request, "shopping_cart.html", c)


def item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Product.DoesNotExist:
        raise Http404('Item does not exist')

    if request.method == 'POST' and request.POST.get('remove'):
        item.delete()
        return redirect('/shopping_cart/')

    if request.method == 'POST' and request.POST.get('modify'):
        return redirect('/modify_item/'+str(item_id))

    amount = item.product.price * item.quantity

    c = {
        'item': item,
        'amount': amount,
    }

    return render(request, 'item.html', c)


def modify_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Product.DoesNotExist:
        raise Http404('Item does not exist')
    modified = False
    if request.method == 'POST':
        form = AddItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            modified = True
    else:
        form = AddItemForm(instance=item)
    c = {
        'form': form,
        'modified': modified,
        'item': item
    }
    return render(request, 'modify_item.html', c)


def checkout(request):
    items = request.user.profile.shopping_cart.all()
    orders = []
    for item in items:
        if len(Order.objects.filter(buyer=request.user.profile,\
            seller=item.product.owner, status="X"))==0:
            Order.objects.create(buyer=request.user.profile, \
                seller=item.product.owner, status="X")
        order=Order.objects.get(buyer=request.user.profile,\
            seller=item.product.owner, status="X")
        if item not in order.items.all():
            order.items.add(item)
        if order not in orders:
            orders.append(order)
    for order in orders:
        if request.method == 'POST' and request.POST.get(str(order.id)):
            return redirect("/verify_order/"+str(order.id))
    if request.method == 'POST' and request.POST.get('submit'):
        for order in orders:
            amount = order_amount(order)
            if order.payment == "O":
                if order.buyer.account < amount:
                    return redirect("/error_account/")
            for item in order.items.all():
                if item.quantity > item.product.quantity:
                    return redirect("/error_quant/"+str(item.id))
            #After passing the amount check and quantity check:
            for item in order.items.all():
                item.product.quantity -= item.quantity
                request.user.profile.shopping_cart.remove(item)
                item.product.save()
            if order.payment == "O":
                order.status = "P"
                order.buyer.account -= amount
                order.buyer.save()
                order.seller.account += amount
                order.seller.save()
            else:
                order.status = "S"
            order.ordertime = datetime.now()
            order.save()
        return redirect("/order_success/")
    amount_table = {}
    for order in orders:
        amount_table[order] = order_amount(order)
    c = {
        'order_amount': amount_table,
        'error': "order"
    }
    return render(request, 'checkout.html', c)


def verify_order(request, order_id):
    order=Order.objects.get(id=order_id)
    completed = False
    if request.method == 'POST':
        form = VerifyOrderForm(request.POST)
        if form.is_valid():
            order.payment=form.cleaned_data['payment']
            order.message=form.cleaned_data['message']
            order.save()
            if order.payment in ['O', 'CD', 'PD']:
                completed = True
    else:
        form = VerifyOrderForm()
    c = {
        'form': form,
        'order':order,
        'completed':completed
    }
    return render(request, 'verify_order.html', c)    


def order_success(request):
    return render(request, "order_success.html", {})


def error_account(request):
    return render(request, "error_account.html", {})


def error_quant(request, item_id):
    item=Item.objects.get(id=item_id)
    return render(request, "error_quant.html", {'item':item})


def order(request, order_id):
    order=Order.objects.get(id=order_id)
    if request.method == 'POST' and request.POST.get("x2p"):
        for item in order.items.all():
            if item not in request.user.profile.shopping_cart.all():
                request.user.profile.shopping_cart.add(item)
        return redirect('/shopping_cart/')
    if request.method == 'POST' and request.POST.get("d2r"):
        order.status = 'R'
        order.receivetime = datetime.now()
        order.save()
        return redirect('/order/'+str(order_id))
    if request.method == 'POST' and request.POST.get("cancel"):
        order.status = 'CA'
        if order.payment == 'O':
            amount = order_amount(order)
            order.buyer.account += amount
            if order.seller.account < amount:
                order.seller.pending_payment += amount - order.seller.account
                order.seller.account = 0.00
            else:
                order.seller.account -= amount
        order.save()
        order.seller.save()
        order.buyer.save()
        return redirect('/order/'+str(order_id))
    if request.method == 'POST' and request.POST.get("p2c"):
        order.status = 'CS'
        order.save()
        return redirect('/order/'+str(order_id))
    if request.method == 'POST' and request.POST.get("c2d"):
        order.delivertime=datetime.now()
        order.status='D'
        if order.deliveryfees not in [0.00, None]:
            if order.buyer.account < order.deliveryfees:
                order.buyer.pending_payment += order.deliveryfees - order.buyer.account
                order.buyer.account = 0.00
            else:
                order.buyer.account -= order.deliveryfees
            order.seller.account += order.deliveryfees
            order.buyer.save()
            order.seller.save()
        order.save()
        return redirect('/order/'+str(order_id))
    filled = False
    if request.method == 'POST' and request.POST.get("fee"):
        form = DeliveryForm(request.POST)
        if form.is_valid():
            order.deliveryfees = form.cleaned_data['deliveryfees']
            order.save()
            if order.deliveryfees != None:
                filled = True
    else:
        form = DeliveryForm()
    c={
        'order': order,
        'amount': order_amount(order),
        'form': form,
        'filled': filled
    }
    return render(request, "order.html", c)    


# Features
def search(request, search_id):
    search = Search.objects.get(id = search_id)
    if search.origin == None or search.origin.strip() == "":
        products = search_engine(search)
    else:
        products = []
        for i in word_list(search.origin):
            products += Product.objects.filter(origin__iexact = i)
        if search.term != None and search.term.strip() != "":
            products = term_and_origin(search_engine(search), products)
    if search.category != None:
        categorized = filter(lambda x: x.category==search.category, products)
        if len(categorized) != 0:
            products = categorized

    if request.method == "POST" and request.POST.get('price'):
        products = order_by_price(products)
    if request.method == "POST" and request.POST.get('fresh'):
        products = order_by_fresh(products)
    if request.method == "POST" and request.POST.get('quantity'):
        products = order_by_quantity(products)
    if request.method == "POST" and request.POST.get('sales'):
        pop = popularity(products)
        sorted_list = [(k,v) for v,k in sorted([(v,k)for k,v in pop.items()],reverse=True)]
        products = []
        for i in sorted_list:
            products.append(Product.objects.get(id = i[0]))
   
    c = {
        'products': products
    }

    return render(request, "search.html", c)


def best_seller(request):
    top10 = find_best_seller(Product.objects.all(), "NO")
    form = BestSellerForm()
    if request.method == 'POST':
        form = BestSellerForm(request.POST)
        if form.is_valid():
            filled = True
            dic = form.cleaned_data
            weeks = dic.get("in_how_many_weeks")
            category = dic.get("category")
            number = dic.get("number")
            if weeks == 0:
                start_time = "NO"
            else:
                start_time = datetime.now()-timedelta(weeks=weeks)
            if category == "-":
                best = find_best_seller(Product.objects.all(), start_time)[:number]
            else:
                best = find_best_seller(Product.objects.filter(category=category), start_time)[:number]
            c = {
                "best":best,
                "num":len(best),
                "top10":top10,
                "form":form,
                "filled":filled
            }
    else:
        filled = False
        c = {
                "top10":top10,
                "form":form,
                "filled":filled
            }
    return render(request, 'best_seller.html', c) 


def discussion(request):
    messages = Message.objects.filter(receiver = None).order_by('time').reverse()
    if request.method == 'POST':
        messageform = MessageForm(request.POST)      
        if messageform.is_valid():
            message = messageform.save()
            if request.user.is_authenticated():
                message.sender = request.user.profile
                message.save()
    else:
        messageform = MessageForm()
    c = {
        'messages': messages,
        'num':len(messages),
        'messageform': messageform
    }
    return render(request,"discussion.html",c)


def demand(request):
    top10 = most_frequently_searched("NO", 10)
    messages = Message.objects.filter(receiver = None).order_by('time').reverse()
    form = MostSearchForm()
    if request.method == 'POST':
        form = MostSearchForm(request.POST)
        if form.is_valid():
            filled = True
            dic = form.cleaned_data
            weeks = dic.get("in_how_many_weeks")
            number = dic.get("number")
            if weeks == 0:
                start_time = "NO"
            else:
                start_time = datetime.now()-timedelta(weeks=weeks)
            most = most_frequently_searched(start_time, number)
            c = {
                "most":most,
                "top10":top10,
                "form":form,
                "filled":filled,
                'messages': messages,
                'num': len(messages)
            }
    else:
        filled = False
        c = {
                "top10":top10,
                "form":form,
                "filled":filled,
                'messages': messages,
                'num': len(messages)
            }
    return render(request,"demand.html",c)


def recommend(request):
    if not request.user.is_authenticated():
        return redirect("/login/")
    user=request.user.profile
    if user.usertype == "B":
        products_user = recommend_sim_user(user)
        products_prod = recommend_sim_product(user)
        c = {
            'products_user': products_user,
            'num_user': len(products_user),
            'products_prod': products_prod,
            'num_prod': len(products_prod)
        }
    else:
        c={}
    return render(request,"recommend.html",c)


# footer link (company) views
def contactus(request):
    c ={}
    return render(request,"contactus.html", c)

def ourteam(request):
    c ={}
    return render(request,"ourteam.html", c)

def career(request):
    c ={}
    return render(request,"career.html", c)

def aboutus(request):
    c ={}
    return render(request,"aboutus.html", c)