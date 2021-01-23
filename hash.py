import nacl.pwhash as hash
import os
import random
import sys
import string

USER_NUM = 10
# Πρώτο ερώτημα

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return str.encode(result_str)



def generate_users(num):
    users = []
    while(len(users) < num):
        x = random.randint(100,999)
        if "users"+str(x) not in users:
            users.append(str.encode("users"+str(x)))

    return users

def first():
    try:
        os.mkdir("users")
    except:
        pass

    try:
        f = open("users/passwords.txt", "xb")
    except:
        print("Passwords have been generated")
        sys.exit()

    password = []
    for i in range(USER_NUM):
        password.append(str.encode(str(i)))
      #  password.append(b'123456')
      #  password.append(get_random_string(8))

    users = generate_users(USER_NUM)
#    randompass = random.randint(0, 1)
#    randompass1 = random.randint(0, 1)
#    password[randompass] = b'123456'
#    password[randompass1] = b'iloveyoumom'
    for i in range(USER_NUM):
        f.write(users[i] + b': ' + hash.str(password[i]))
        f.write(b'\n')

    f.close()

def verify(passwd, hashes):
    for p in passwd.readlines():
        for i, h in enumerate(hashes):
            try:
                if hash.verify(str.encode(h[10:].strip()),str.encode(p.strip())):
                    print("user{0}".format(i), end='')
                    print(" - " + p.strip())
            except:
                print("OOPS")
                return

def second():
    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit()

    passwd = open(sys.argv[1], "r")  # common passwords
    hashes = open(sys.argv[2], "r").readlines()

    verify(passwd, hashes)
    
        

#first()
second()
