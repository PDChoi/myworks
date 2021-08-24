data = [19, 2, 31, 45, 30, 11, 121, 27]
# decide a median location of sorting => size of a block
mid = len(data) // 2

while mid > 0:
    for i in range(mid, len(data)):
        key = data[i]
        index = i
        while index >= mid and data[index - mid] > key:
            data[index] = data[index - mid]
            index -= mid

        data[index] = key
    print(data)
    mid //= 2

print(data)
