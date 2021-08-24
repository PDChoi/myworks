# create empty 2d list for a queue 
queueList = [[] for i in range(10)]

data = [19, 2, 31, 45, 30, 11, 121, 27]
isSort = False # a variable that memorize if sorting is done. Finished if turns to True
radix = 1 # memorize the number of digits 1 => 10 => 100 => ...

# repeat until isSort turns to True

while not isSort:
    isSort = True
    # 정렬할 숫자의 기수(진법)의 크기만큼 큐로 사용할 리스트를 만든다.
    queueList = [[] for i in range(10)]
    print('radix: {}'.format(radix))

    for n in data:
        print('n: {0:3d}'.format(n), end= ' => ')
        # picks a number of radix(digits) for queue
        digit = n // radix % 10
        print(digit)
        # put numbers in the queues
        queueList[digit].append(n)
        # inspect if sorting is done.
        if isSort and digit > 0:
            isSort = False

    # pick up saved data from queue 0 in order and designate on the data list again.
    index = 0
    for numbers in queueList:
        for number in numbers:
            data[index] = number
            index += 1
    print(data)
    print('=' * 80)
    radix *= 10 
