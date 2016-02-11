from models import *
from recommend import empty_list
import nltk
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer


def build_search_engine():
	'''
	Returns a search function which searches the string that user enters
	within the two indexes which map from words to lists of products.
	'''
	index_name = index("name")
	index_total = index("description")
	def search_engine(search):
		outcome_name = search_helper(search, index_name)
		if len(outcome_name) >= 30:
			return id_to_product(outcome_name)
		outcome_total = search_helper(search, index_total)
		return id_to_product(outcome_total)
	return search_engine


def search_helper(search, index):
	stemmer = SnowballStemmer("english")
	category_tag = nltk.pos_tag(word_tokenize(search.term.strip()))
	nouns = []
	for i in category_tag:
		if i[1] in ["NN", "NNS", "NNP", "NNPS"]:
			nouns.append(stemmer.stem(i[0]))
	terms = word_list(search.term)
	outcome_nouns = words2products(nouns, 1, index)
	for i in range(1,len(terms)+1)[::-1]:
		outcome = words2products(terms, i, index)
		for j in outcome:
			if j not in outcome_nouns:
				outcome.remove(j)
		if len(outcome)>=15 or i == 1:
			return outcome


def words2products(terms, threshold, index):
	if len(Product.objects.all())==0:
		return []
	products = empty_list(Product.objects.all().order_by("id").reverse()[0].id)
	for term in terms:
		if term in index:
			for i in index[term]:
				products[i-1] += 1
	outcome = []
	for i in range(len(products)):
		if products[i] >= threshold:
			outcome.append((products[i], i+1))
	outcome = sorted(outcome)
	rv = [y for (x,y) in outcome]
	return rv


def index(index_type):
	dic={}
	products=Product.objects.all()
	for product in products:
		if index_type == "name":
			words=word_list(product.name)
		else:
			words=word_list(product.name)+word_list(product.description)
		for word in words:
			if word not in dic:
				dic[word]=[]
			if product.id not in dic[word]:
				dic[word].append(product.id)
	return dic


def word_list(text):
	stemmer = SnowballStemmer("english")
	return [stemmer.stem(i) for i in word_tokenize(text.strip())]


def term_and_origin(term_list, origin_list):
	rv = []
	temp = []
	for product in term_list:
		if product.origin.strip().lower() in origin_list:
			rv.append(product)
		else:
			temp.append(product)
	rv = rv+temp
	return rv


def id_to_product(id_list):
	rv = []
	for i in id_list:
		rv.append(Product.objects.get(id=i))
	return rv