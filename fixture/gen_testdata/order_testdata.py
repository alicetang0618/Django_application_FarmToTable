from random import *
STATUS = ["X","P","S","C","D","R"]
MES = ["Thanks","Great Product","Very tasty"]
PAY = ["O","CD","PD"]

def ran():
    l = [k for k in range(randint(1,200))]
    if len(l) >= 10:
        l = l[:11]
    return l

for i in range (50,101):
    a = {
        "fields": {
            "status": STATUS[randint(0,5)],
            "ordertime": "2015-03-0"+str(randint(1,9))+"T21:47:12.904Z",
            "delivertime": "2015-03-0"+str(randint(1,9))+"T21:47:43.090Z",
            "deliveryfees": randint(10,30),
            "items": [
                ran()
            ],
            "receivetime": "2015-03-1"+str(randint(0,9))+"T21:48:00.278Z",
            "buyer": randint(11,20),
            "message": MES[randint(0,2)],
            "seller": randint(3,10),
            "payment": PAY[randint(0,2)]
        },
        "model": "applications.order",
        "pk": i
    }
    print str(a)+","

