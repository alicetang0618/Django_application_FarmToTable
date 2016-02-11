from random import *
FIRST = ["Hong", "Chang","Xiaorui","Lingwei","Feng","Jianan","Zhonglun"]
LAST = ["Zhao","Qian","Sun","Li","Zhou","Wu","Zheng","Wang"]
PHONE = ["8273849284","2839380922"]
INTRODUCTION = ["First time selling things online.", "Hope you like my product", 
"Hello, I like selling things online", "This is an awesome platform",
"My product is organic and I hope you like them"]
STATE = ["Chongqing", "Beijing", "Changsha","Guangzhou","Yunan","Guizhou"]

for i in range(3,11):
    a = {
        "fields": {
            "picture": "",
            "first_name": FIRST[randint(0,6)],
            "last_name": LAST[randint(0,7)],
            "phone": PHONE[randint(0,1)],
            "introduction": INTRODUCTION[randint(0,4)],
            "zipcode": "382923",
            "usertype": "S",
            "state": STATE[randint(0,5)],
            "user": i,
            "address": "Xiaoshan Village",
            "account": "191",
            "pending_payment": "0",
            "shopping_cart": [],
            "email": "seller@farmer.org"
        },
        "model": "applications.userprofile",
        "pk": i
    }
    print str(a) + ","