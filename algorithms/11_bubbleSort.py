# Bubble sorting: It is beneficial to finish earlier if data is already sorted => early stop

'''
for i in range(4):
    for j in range(4-i):
        print('[i = {}, j = {}]'.format(i, j), end='')
    print()
'''

data = [8, 3, 4, 9, 1]
for i in range(len(data)-1):
    for j in range(len(data)-1-i):
        # ascending sort => 
        if data[j] > data[j + 1]:
            data[j], data[j + 1] = data[j + 1], data[j]
            flag = False
    print('result {}: {}'.format(i+1, data))

    if flag:
        print({})
        
print('Result: {}'.format(data))
