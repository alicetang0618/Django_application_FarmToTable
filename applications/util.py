from datetime import datetime, timedelta
from nltk import word_tokenize
from models import *

# finance function helpers
def calculate_spending_by_type(user, start_time):
    orders = Order.objects.filter(buyer=user, ordertime__gte=start_time)
    donations = Donation.objects.filter(donor=user, time__gte=start_time)
    dic = {"V":0,"F":0,"M":0,"D":0,"S":0,"O":0,"donate":0,"deliver":0}
    for order in orders:
        if order.status != "CA":
            if order.deliveryfees != None:
                dic["deliver"]+=order.deliveryfees
            for item in order.items.all():
                dic[item.product.category]+=item.quantity*item.product.price
    for donate in donations:
        dic["donate"]+=donate.amount
    rv={}
    for i in dic:
        if dic[i] != 0:
            rv[i] = dic[i]
    return rv


def total_spending(user, num_weeks):
    total=0
    dic = calculate_spending_by_type(user, datetime.now() - timedelta(weeks=num_weeks))
    for i in dic:
        total+=dic[i]
    return total


def calculate_revenue_by_type(user, start_time):
    orders = Order.objects.filter(seller=user, ordertime__gte=start_time)
    donations_d = Donation.objects.filter(donor=user, time__gte=start_time)
    donations_r = Donation.objects.filter(receipient=user, time__gte=start_time)
    dic = {"revenue":0,"donation received":0,"donation to others":0}
    for order in orders:
        if order.status != "CA":
            for item in order.items.all():
                dic["revenue"]+=item.quantity*item.product.price
    for donate in donations_r:
        dic["donation received"]+=donate.amount
    for donate in donations_d:
        dic["donation to others"]+=donate.amount
    return dic


def total_revenue(user, num_weeks):
    dic = calculate_revenue_by_type(user, datetime.now() - timedelta(weeks=num_weeks))
    return dic["revenue"]+dic["donation received"]-dic["donation to others"]


# product function helpers
def quantity_sold(product, start_time):
    quantity = 0
    if start_time == "NO":
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(ordertime__gte=start_time)
    for order in orders:
        if order.status != "CA":
            for item in order.items.all():
                if item.product == product:
                    quantity += item.quantity
                    break
    return quantity


def find_best_seller(group, start_time):
    best_list = []
    for product in group:
        quantity = quantity_sold(product, start_time)
        if quantity != 0:
            best_list.append((quantity,product))
    best_list=[y for (x,y) in sorted(best_list, reverse=True)]
    return best_list


def order_amount(order):
    items = order.items.all()
    amount = 0
    for item in items:
        amount += item.product.price * item.quantity
    return amount


def popularity(products):
    popularity = {}
    for product in products:
        popularity[product.id] = 0
        items = Item.objects.filter(product = product)
        for item in items:
            for order in filter(lambda order: order.status != "CA", Order.objects.all()):
                if item in order.items.all():
                    popularity[product.id] = popularity.get(product.id) + item.quantity
    return popularity


def most_frequently_searched(start_time, number):
    dic={}
    if start_time=="NO":
        searches=Search.objects.all()
    else:
        searches=Search.objects.filter(time__gte=start_time)
    for search in searches:
        words = word_tokenize(search.term.strip().lower())
        for word in words:
            dic[word]=dic.get(word,0)+1
    tuplelist=sorted([(t[1], t[0]) for t in dic.items()], reverse=True)
    return [y for (x,y) in tuplelist][:number]


def order_by_price(products):
    rv = []
    for product in products:
        rv.append((product.price, product))
    rv = sorted(rv)
    rv = [y for (x,y) in rv]
    return rv


def order_by_fresh(products):
    rv = []
    for product in products:
        rv.append((product.expiration_date, product))
    rv = sorted(rv, reverse=True)
    rv = [y for (x,y) in rv]
    return rv


def order_by_quantity(products):
    rv = []
    for product in products:
        rv.append((product.quantity, product))
    rv = sorted(rv, reverse=True)
    rv = [y for (x,y) in rv]
    return rv