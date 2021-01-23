import random

num = 899
users = []

while(len(users) < num):
    x = random.randint(100,999)
    if "users"+str(x) not in users:
        users.append("users"+str(x))


if len(users) == len(set(users)):
        print("False") 
else:
        print("True")
