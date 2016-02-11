from scipy.stats.stats import pearsonr
import numpy as np
from models import *


def recommend_sim_user(user):
	'''
	Recommend products rated high by users similar to the user. Similarity
	is measured by purchase history and rating behaviors.
	'''
	recommend = recommend_sim_user_helper(user, 5)
	if len(recommend) < 10:
		return recommend_sim_user_helper(user, 4)
	return recommend


def recommend_sim_user_helper(user, threshold):
	users=[]
	for i in UserProfile.objects.filter(usertype='B'):
		if i != user:
			users.append(i)
	recommend=[]
	group = similar_rating_user(similar_purchase_user(users, user, 20), user, 10)
	if len(group) <= 5:
		group = similar_purchase_user(users, user, 20)
	for person in group:
		for product in high_rate_product_by_user(person, threshold):
			if product not in recommend and product not in products_bought_by_user(user):
				recommend.append(product)
	return recommend


def recommend_sim_product(user):
	'''
	Recommend products similar to products liked by or rated high by the user.
	'''
	for i in range(1,10):
		if len(recommend_sim_product_helper(user, i))>=10:
			return recommend_sim_product_helper(user, i)
	return recommend_sim_product_helper(user, 10)


def recommend_sim_product_helper(user, num):
	recommend = []
	for i in product_like(user):
		for product in similar_product(i, num):
			if product not in recommend:
				recommend.append(product)
	return recommend


def product_like(user):
	product_like = []
	ratings = Rating.objects.filter(rater=user, rated=None, rate=5)
	for i in ratings:
		if i.product not in product_like:
			product_like.append(i.product)
	for i in Product.objects.all():
		if user in i.liked_by.all():
			product_like.append(i)
	return product_like


def similar_purchase_user(group, user, num):
	return most_similar(group,user,num,buy_corr)


def similar_rating_user(group, user, num):
	return most_similar(group,user,num,rate_corr)


def similar_product(product, num):
	products=[]
	for i in Product.objects.all():
		if i != product:
			products.append(i)
	return most_similar(products, product, num, product_corr)


def most_similar(group, target, num, function):
	highest=[]
	for i in group:
		value=function(i,target)
		if value!=None:
			if len(highest)==0:
				highest.append((i,value))
			else:
				for j in range(len(highest)):
					if value >= highest[j][1]:
						highest.insert(j,(i,value))
						break
					if j==len(highest)-1:
						highest.append((i,value))
	sims=[]
	if len(highest) > num:
		highest = highest[:num]
	for i in highest:
		sims.append(i[0])
	return sims


def buy_corr(user_one, user_two):
	return corr(user_one, user_two, buy_history)


def rate_corr(user_one, user_two):
	return corr(user_one, user_two, rate_history)


def product_corr(product_one, product_two):
	return corr(product_one, product_two, product_history)


def buy_history(user):
	if len(Product.objects.all())==0:
		return []
	orders=filter(lambda order: order.status != "CA", Order.objects.filter(buyer=user))
	product_dict={}
	for order in orders:
		items=order.items.all()
		for item in items:
			product=item.product.id
			product_dict[product]=product_dict.get(product, 0)+1
	history=empty_list(Product.objects.all().order_by("id").reverse()[0].id)
	for i in product_dict:
		history[i-1]+=product_dict[i]
	return history


def rate_history(user):
	if len(Product.objects.all())==0:
		return []
	rates = Rating.objects.filter(rater=user, rated=None)
	rate_dict = {}
	rate_dict_num = {}
    #building the dictionary with product id as keys to values include the rating
    # and the number of times it's rated by the user.
	for rate in rates:
		rate_dict[rate.product.id] = rate_dict.get(rate.product.id, 0) + rate.rate
		rate_dict_num[rate.product.id] = rate_dict_num.get(rate.product.id, 0) + 1
    #to gain the average rating of a product by the user
	for product in rate_dict:
		rate_dict[product] = rate_dict.get(product)/rate_dict_num[product]
	history = empty_list(Product.objects.all().order_by("id").reverse()[0].id)
	for product_id in rate_dict:
        # minus one to count the index (the list starts from 0)
		history[product_id-1] = rate_dict[product_id]
	return history


def product_history(product):
	history=[]
	full_history=product_history_helper(product)
	for i in range(len(full_history)):
		if UserProfile.objects.get(id=i+1).usertype=="B":
			history.append(full_history[i])
	return history


def product_history_helper(product):
	if len(UserProfile.objects.all())==0:
		return []
	orders=filter(lambda order: order.status != "CA", Order.objects.all())
	buyer_dict={}
	for order in orders:
		items=order.items.all()
		for item in items:
			if item.product.id == product.id:
				buyer_dict[order.buyer.id]=buyer_dict.get(order.buyer.id,0)+1
				break
	history=empty_list(UserProfile.objects.all().order_by("id").reverse()[0].id)
	for i in buyer_dict:
		history[i-1] += buyer_dict[i]
	return history


def corr(one, two, function):
	list_one=function(one)
	list_two=function(two)
	if (not identical(list_one)) and (not identical(list_two)):
		return pearsonr(list_one, list_two)[0]
	empty = empty_list(len(list_one))
	if list_one==empty or list_two==empty:
		return None
	elif function == buy_history or function == product_history:
		return 1
	else:
	    return 1-np.square(list_two[0]-list_two[0])/8


def empty_list(num):
	rv=[]
	for i in range(num):
		rv.append(0)
	return rv


def identical(l):
	if l == []:
		return True
	for i in l:
		if i != l[0]:
			return False
	return True


def high_rate_product_by_user(user, threshold):
	rates=Rating.objects.filter(rater=user, rated=None)
	product_list=[]
	for rate in rates:
		if rate.rate >= threshold and len(Product.objects.filter(id=rate.product.id))!=0:
			product_list.append(rate.product)
	return product_list


def products_bought_by_user(user):
	products = []
	orders=filter(lambda order: order.status != "CA", Order.objects.filter(buyer=user))
	for order in orders:
		for item in order.items.all():
			if item.product not in products:
				products.append(item.product)
	return products