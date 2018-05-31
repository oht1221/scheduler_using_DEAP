
import time
from preprocessing import make_job_pool
from deap import tools
from deap import base, creator
import random

import cnc
import accessDB
from collections import deque

if __name__ == "__main__":
    CNCs = []
    JOB_POOL = deque()
    READY_POOL = deque()
    IN_PROGRESS = deque()
    POP_SIZE = 30
    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL)
    #preprocessing.read_CNCs('./hansun2.xlsx', CNCs)


    machines = {}
    for cnc in CNCs:
        machines[float(cnc.getNumber())] = list()
    standard = input("schedule starts on : ")
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)


    creator.create("FitnessMin", base.Fitness, weights=(1.0, 1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("schedule", random.sample, JOB_POOL, IND_SIZE)
    toolbox.register("individual", tools.initIterate, creator.Individual,
                     toolbox.schedule)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(n = POP_SIZE)
    for i in range(POP_SIZE):
        indv = pop[i]
        print("---------------------indiv %d---------------------"%(i))
        for job in indv:
            print(job.getWorkno())
        evaluate(indv)
        print("---------------------indiv %d---------------------"%(i))
    '''
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        return sum(individual),


    toolbox.register("mate", tools.cxPartialyMatched())
    toolbox.register("mutate", tools.mutShuffleIndexes(), indpb=0.05)
    toolbox.register("select", tools.selSPEA2(), k=)
    toolbox.register("evaluate", evaluate)
'''
