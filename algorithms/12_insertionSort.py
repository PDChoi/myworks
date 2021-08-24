for i in range(1, 5):
    for j in range(i-1, -1, -1):
        print('[1 = {}, j = {}]'.format(i, j), end='')
    print()



data = [8, 3, 4, 9, 1]

for i in range(1, len(data)):
    # In order to find new location of new data in arranged file, save new data and indece 
    key = data[i]
    index = i
    # find new location for new data
    for j in range(i - 1, -1, -1):
        if data[j] > key:  # compare with data in front
            # the arranged file is larger than 
            data[j + 1] = data[j]
            index -= 1
        else:
            #  data to be inserted 
            break
    # put new data(key) in (index)
    data[index] = key
    print('result {}: {}'.format(i, data))
print('Result: {}'.format(data))
