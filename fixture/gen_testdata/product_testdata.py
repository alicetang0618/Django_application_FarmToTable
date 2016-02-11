from random import *
Name = ["egg","beef","apple","dried banana","cucumber","pork","organic pork","dried mushroom","healthy apple","organic egg"]
Description = ["Organic", "super good for your health", 
"delicious, juicy", "very very sweet",
"good for children","good for women's health"]
STATE = ["Chongqing", "Beijing", "Changsha","Guangzhou","Yunan","Guizhou"]
Unit = ["Kg", "Lb","Crate","Dozen","Each"]




for i in range(0,11):
    a = {
        "fields": {
            "category": randint(0,5),
            "picture": "popular.jpg",
            "name": Name[randint(0,9)],
            "production_date": "2015-03-02T21:43:14Z",
            "expiration_date": "2015-04-03T00:00:00Z",
            "price": randint(0,10),
            "description": Description[randint(0,5)],
            "liked_by": (randint(0,10))
        }
    }
    print str(a)+ ","

