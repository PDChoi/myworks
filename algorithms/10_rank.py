# descending order sorting 
score = [70, 100, 80, 100, 90]
# create a list to memorize a rank
rank = [1 for i in range(len(score))]
#print(rank)

for i in range(len(score) - 1):
    for j in range(i + 1, len(score)):
        # if i'th score is greater than j'th, increase 1 in rank, vice versa.
        if score[i] > score[j]:
            rank[j] += 1
        elif score[i] < score[j]:
            rank[i] += 1


for i in range(len(score)):
    print('{0:3d} is rank {1}.'.format(score[i], rank[i]), end='')
    print('*' * (score[i]//10))
