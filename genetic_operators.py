import random

def inversion_mutation(individual):
    total = len(individual)
    interval = round(len(individual) / 3)
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
    print(individual)
    temp = []
    for i in range(interval):
        temp.append(individual[(start + i) % len(individual)])
    print(temp)
    blocks = random.randrange(1, len(individual))
    print("# of blocks :", blocks)
    replaced = start
    replacing = (start + interval) % len(individual)
    for i in range(blocks):
        individual[replaced % len(individual)] = individual[replacing % len(individual)]
        individual[replacing % len(individual)] = 0
        replaced = (replaced + 1) % len(individual)
        replacing = (replacing + 1) % len(individual)
    print(individual)
    for i in range(interval):
        individual[(replaced + i) % len(individual)] = temp[i]

indiv = [1,2,3,4,5,6,7,8,9,10]
inversion_with_displacement_mutation(indiv)
print(indiv)