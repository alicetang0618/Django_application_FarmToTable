from random import *

for i in range(3,201):
 	a= {
    	"fields": {
        	"product": randint(1,10),
        	"quantity": randint(1,5)
    	},
    	"model": "applications.item",
    	"pk": i
	}
	print str(a) + ","