## Number system

dec, n = map(int, input('Put Decimal Notation, Number System: ').split())
convert = []

hex_16 = ['A', 'B', 'C', 'D', 'E']

while True:
    m = dec // n # quotient
    r = dec % n # remainder
    '''
    if r >= 10:
        d = r-10
        r = hex_16[d]
    '''
    convert.append(r)
    if m == 0:  # 
        break
    # ===== if
    # put quotient  to dec for next calc
    dec = m
# ====while

# reverse convert list
'''
for i in range(len(convert) - 1, -1, -1):
    print(convert[i], end = ' ')
print()
print(convert[::-1])
'''

# chr() => returns char
for i in range(len(convert) -1, -1, -1):
    print(convert[i] if convert[i] < 10 else chr(convert[i] + 55), end= ' ')

