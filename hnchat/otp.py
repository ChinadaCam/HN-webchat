import math, random

string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
lent = len(string)

def gen_otp():
    otp = ""
    for i in range(6):
        otp += string[math.floor(random.random()*lent)]
    return otp

