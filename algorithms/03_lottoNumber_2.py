import random

# Generate a set to memorize lotto number
lotto = set()
#print(type(lotto))

# 1st prize number: never know how many times that repeated numbers appear
while True:
    number = random.randrange(1,46)
    lotto.add(number)
    print('{0:2d} {1}'.format(number, lotto))
    # escape inf loop when 6 unrepeated numbers are saved
    if len(lotto) == 6:
        break

print('1st prize num: {}'.format(lotto))

# Bonus num
while True:
    bonus = random.randrange(1, 46)
#    print('\n' + str(bonus), end='')
    if bonus not in lotto: # check if bonus num is not repeated in 1st rpize num
        break

print('Bonus num: {}'.format(bonus))
