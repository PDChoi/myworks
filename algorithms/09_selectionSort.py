data = [8, 3, 4, 9, 1]

for i in range(4):
    for j in range(i+1, 5):
        if data[i] > data[j]:
            data[i], data[j] = data[j], data[i]
    print('result {}: {}'.format(i + 1, data))

print('Result: {}'.format(data))


# ==============================


data = [8, 3, 4, 9, 1]

for i in range(len(data)-1):  # rotation number(n-1 times), location to select data
    for j in range(i+1, len(data)):  # location to compare with the selected data
        if data[i] > data[j]:
            data[i], data[j] = data[j], data[i]
    print('result {}: {}'.format(i + 1, data))

print('Result: {}'.format(data))
                                 
