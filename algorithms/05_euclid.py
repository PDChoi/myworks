a, b = map(int, input('Put two numbers: ').split()) #split puts space between chars
# map: int cannot designate two integers, only first element becomes integer
'''
map integrates below two elements 
map(data format, input('input message').split()): changes data format all at once
a = int(input('a: '))
b = int(input('b: '))
'''

if a > b:
    big = a
    small = b
else:
    big = b
    small = a
print('big = {}, small={}'.format(big, small))

# iteration varies depending on the inputs, thus implement inf loop.
# ; attaches two lines into one line

while True:
    r = big % small # % remainder
    if r == 0:      # condition that inf loop is finished
        break
    big = small
    small = r
    # ===== if
    # For next calculation, take small to divide big then put the remainder to the small
# ====== while

# the least common multiple
# the greatest common divisor
print('TGCD: {}, TLCM: {}'.format(small, a * b // small))



a, b = map(int, input('Put two inputs: ').split())
r = 1
if a > b:
    high = a; low = b
else:
    low = a: high = b
print('high = {}, low = {}'.format(high, low))

while r > 0:
    r = high % low
    high = low
    low = r

l = a * b // high
print('TGCD: {}, TLCM: {}'.format(high, low))

