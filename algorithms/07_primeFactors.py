# Terminate if prime factor is less than 2

while True:
    n = int(input('Put a number for prime factor: '))
    if n < 2:
        print('Found a number less than 2: Program terminated.')
        break
    # ===== if

    # Initialize memory used for prime factor factorization
    s = []
    c = 0 # The number of prime factor
    number = n # save a number for factorization of prime factor

    # Start factorization of prime factor
    while True:
        k = 2 # Starting number for factorization
        while True:
            r = n % k
            if r == 0: # Check if factorized
                break
            k += 1    # 

        c += 1 # increase the number of prime factor. when there is only one prime factor left, it is divided by it self.
        s.append(k) # add prime factor into a list
        n //= k
        if n == 1: # Check if the factorization is finished
            break  # Terminate inf loop if the factorization is finished.

    if c == 1:
        print('Input: {} => Prime Number'.format(number))
    else:
        print('Input: {} => '.format(number), end='')
        for i in range(len(s)-1):
            print(s[i], end=' * ')
        print(s[-1])
