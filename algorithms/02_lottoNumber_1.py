import random  # for randrange() method
import time    # for sleep() method

lotto = list()   # or lotto = []

#for i in range(1, 46):
#    lotto.append(i)
#print(lotto)

lotto = [i for i in range(1,46)] # generates repeating i for 45 times

# print 10 items per lines before mixing
#print(lotto[0:9], lotto[10:19], lotto[20:29], lotto[30:39], lotto[40:46], sep='\n')

'''
for i in range(45):
    print('{0:2d} '.format(lotto[i]), end='')
    if (i+1) % 10 ==0:
        print()

print('\n=' + '=' * 30 + '   before mixing')
'''




# mix and pick random numbers in range 1 - 44
for i in range(1000000):
    r = random.randrange(1, 45)
    # lotto[0] and lotto[r]
    lotto[0], lotto[r] = lotto[r], lotto[0]

'''
for i in range(45):
    print('{0:2d} '.format(lotto[i]), end='')
    if (i+1) % 10 ==0:
        print()
'''
#print('\n=' + '=' * 30 + '   after mixing')

# Get 1st prize & bonus number
print('1st prize:  ', end='')
for i in range(6):
    print('{0:2d}  '.format(lotto[i]), end='')
    time.sleep(1)
print('Bonus number:  {}'.format(lotto[6]))



#=======================================================#


# Powerball Lottery
# White ball: 1 - 69, Red ball 1 - 26


# mix and pick random numbers in range 1 - 44
lotto = [i for i in range(1, 70)]

for i in range(1000000):
    r = random.randrange(1, 69)
    # lotto[0] and lotto[r]
    lotto[0], lotto[r] = lotto[r], lotto[0]

#print('\n=' + '=' * 30 + '   after mixing')

# Get 1st prize & bonus number
print('White ball:  ', end='')
for i in range(5):
    print('{0:2d}  '.format(lotto[i]), end='')
    time.sleep(1)
print('Red ball:  {}'.format(random.randrange(1,27)))









### Exercise
'''
a = 3
b = 4
print('a = {}, b = {}'.format(a,b))

temp = a
a = b
b = temp
print('a = {}, b = {}'.format(a,b))

[a, b] = [b, a]
print('a = {}, b = {}'.format(a,b))


(a, b) = (b, a)
print('a = {}, b = {}'.format(a,b))

a, b = b, a
print('a = {}, b = {}'.format(a,b))
'''
