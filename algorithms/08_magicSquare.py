'''
a = [0 for i in range(5)]
print(a)

a = [[0] * 5 for i in range(5)]
print(a)
'''

'''
import numpy as np
b = np.array(a)
print(b)
'''

'''
for i in range(5):
    for j in range(5):
        print('{0:2d} '.format(a[i][j]), end='')
    print()
'''

'''
# define 5x5 list
a = [[0] * 5 for i in range(5)]

i = 0 # row
j = 2 # column

# repeat putting numbers in 2d list for the magic square
for k in range(1, 5**2 +1):
    a[i][j] = k
    # check if a number put in the magic square is a multiple of 5
    if k % 5 == 0:
        # if multiple of 5 increase 1 line only
        i += 1
    else:
        # if not decrease 1 line, increase i column.
        i -= 1
        # 
        if i < 0:
            i = 4
        j += 1
        # 
        if j >= 5:
            j = 0

for i in range(5):
    for j in range(5):
        print('{0:2d} '.format(a[i][j]), end='')
    print()
'''

#====================================================
while True:
    n = int(input('Put an odd number greater than 3: '))
    if n >= 3 and n % 2 == 1:
        break
    print('Error: Put an odd number greater than 3')
    
a = [[0] * n for i in range(n)]
i = 0
# decide a location of 1 depending on a dimension of matrix
j = n // 2

for k in range(1, n ** 2 +1):
    a[i][j] = k
    if k % n == 0:
        i += 1
    else:
        i -= 1
        if i < 0:
            i = n - 1
        j += 1
        if j >= n:
            j = 0

for i in range(n):
    for j in range(n):
        print('{0:3d} '.format(a[i][j]), end='')
    print()
        


