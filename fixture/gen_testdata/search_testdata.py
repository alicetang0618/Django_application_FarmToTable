from random import *
ORI = ["Beijing","Shanghai","Xinjiang","Chongqing","Rongchang","Chengdu","Nanchang"]
CAT = ["F","V","M","D","S","O"]
term = ["apple","organic","pork","banana","dried","cucumber","egg","healthy","health","beef","vitamin c","good","woman","children"]
for i in range (201,251):
	a = {
	    "fields": {
	        "origin": ORI[randint(0,6)],
	        "category": CAT[randint(0,5)],
	        "term": term[randint(0,13)],
	        "user": None,
	        "time": "2015-03-1"+str(randint(0,9))+"T08:01:17.441Z"
	    },
	    "model": "applications.search",
	    "pk": i
	}
	print str(a) + ","