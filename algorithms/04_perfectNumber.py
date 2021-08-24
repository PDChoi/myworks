lm = 0  # counts perfect number => add 1 when it is found as a perfect number

for n in range(4, 10001):
    # 완전수가 판별할 숫자가 바뀔때마다 약수의 합계를 다시 계산해야 하므로 반복이 시작될 때 마다 0으로 초기화
    total = 0 
    # 어떤 숫자를 나눠서 떨어뜨릴 수 있는 가장 큰 수는 자신을 제외하면 자신의 절반을 넘어가지 않는다.    # // -> quotient
    k = n // 2

    # inner loop finds if n is a perfect number by summing aliquot except itself
    for j in range(1, k+1):
        # 완전수인가 판별할 수의 약수를 계산하기 위해 n 을 1~k 사이의 숫자로 나눈 나머지를 계산
        r = n % j  #remainder
        # n을 j로 나눈 나머지가 0이면 j는 n의 약수이므로 약수의 합계를 계산
        if r == 0: # j가 n의 약수인가?
            total += j # j가 n의 약수이므로 약수의 합계를 계산한다.
    # n이 완전수인가 판단해서 완전수면 n을 출력하고 완전수의 개수(lm)를 1 증가시킨다.
    if n == total: # 완전수인가?
        lm += 1 #완전수의 개수를 1 증가시킨다
        print('{0}th perfect number=>{1:4d}'.format(lm,n))

print('The number of perfect number: {}'.format(lm))
