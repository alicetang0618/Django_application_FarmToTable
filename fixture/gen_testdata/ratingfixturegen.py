from random import *
COMMENT = ["Very good product","It tasted funny","I will buy this again","I dont like this but okay","You should keep selling this","Truely organic","Very healthy","Yum","Thanks","Okay"]
COMMENT_USER = ["You are my favorite", "Your product is great", "Thank you so much", "The food is great"]
for i in range(201,211):
	a = {"fields":{"comment":COMMENT_USER[randint(0,3)],"product":None,"rated":None,"rate":randint(1,5), "rater":randint(11,21),"time":"2015-03-0"+str(randint(1,9))+"T21:56:35.246Z"},"model":"applications.rating","pk":i} 
	print str(a)+"," 
