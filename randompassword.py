import random

words = open('words.txt').read().splitlines()
pwd = ''
while len(pwd) < 8:
    pwd += random.choice(words)[:3]
    pwd += str(random.choice(range(10)))

print(pwd)
