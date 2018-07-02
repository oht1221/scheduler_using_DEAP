import random
import numpy as np
import time

def inversion_mutation(individual):
    total = len(individual)
    interval = round(len(individual) / 3)
    random.seed(time.time() * 10 % 10)
    start = random.randrange(0, total) #시작점 (왼쪽)
    end = start + interval - 1
    i = 0
    print(start)
    print(end)
    while i < (interval / 2):
        temp = individual[(start + i) % total]
        individual[(start + i) % total] = individual[(end - i) % total]
        individual[(end - i) % total] = temp
        i += 1
    return individual, interval, start, end

def inversion_with_displacement_mutation(individual):
    dummy, interval, start, end = inversion_mutation(individual)
    #print(individual)
    temp = []
    for i in range(interval):
        temp.append(individual[(start + i) % len(individual)])
    #print(temp)
    random.seed(time.time() * 10 % 10)
    blocks = random.randrange(1, len(individual))
    #print("# of blocks :", blocks)
    replaced = start
    replacing = (start + interval) % len(individual)
    for i in range(blocks):
        individual[replaced % len(individual)] = individual[replacing % len(individual)]
        individual[replacing % len(individual)] = 0
        replaced = (replaced + 1) % len(individual)
        replacing = (replacing + 1) % len(individual)
    #print(individual)
    for i in range(interval):
        individual[(replaced + i) % len(individual)] = temp[i]
    return individual,

def order_crossover(start, end, ind1, ind2):
    #print("chromosome %2d X chromosome %2d" % (parent_1, parent_2))
    p1 = ind1
    p2 = ind2
    print(ind1)
    print(ind2)
    print(start)
    print(end)
    start = start
    end = end
    offspring1 = []
    offspring2 = []
    for j in p1:
        offspring1.append(j)
    for j in p2:
        offspring2.append(j)
    not_selected_1 = list(range(0, len(p2))) #p1에서
    not_selected_2 = list(range(0, len(p1)))
    for i in range(start, end+1):
        selected = p2.index(p1[i])
        not_selected_1.remove(selected)#여기서 선택 안된 것은 p2에서 선택할 것들
    i = end + 1
    j = end + 1
    while 1:
        if i%len(p2) in not_selected_1:
            offspring1[j%len(offspring1)] = p2[i%len(p2)]
            not_selected_1.remove(i%len(p2))
            j = j + 1
        i = i + 1
        if not not_selected_1:
            break

    for i in range(start, end + 1):
        selected = p1.index(p2[i])
        not_selected_2.remove(selected)  # 여기서 선택 안된 것은 p2에서 선택할 것들
    i = end + 1
    j = end + 1
    while 1:
        if i % len(p2) in not_selected_2:
            offspring2[j % len(offspring2)] = p1[i % len(p1)]
            not_selected_2.remove(i % len(p1))
            j = j + 1
        i = i + 1
        if not not_selected_2:
            break

    return offspring1, offspring2

def random_permutation():
    pool = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    permutation = []
    while(pool):
        sel = random.choice(pool)
        permutation.append(sel)
        pool.remove(sel)
    return permutation

'''
indiv1 = random_permutation()
indiv2 = random_permutation()
print(indiv1)
print(indiv2)
offspring1, offspring2 = order_crossover(indiv1, indiv2, 2, 8)
print(offspring1)
print(offspring2)
'''