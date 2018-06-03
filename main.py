
import time
import random
import numpy as np
from preprocessing import make_job_pool
from preprocessing import read_CNCs
from deap import tools
from deap import base, creator
from evaluation import pre_evaluate
from evaluation import evaluate
from evaluation import invert_sigma_normalize
from evaluation import invert_linear_normalize
from collections import deque

if __name__ == "__main__":
    CNCs = []
    JOB_POOL = deque()
    READY_POOL = deque()
    IN_PROGRESS = deque()
    POP_SIZE = 30
    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL)
    read_CNCs('./hansun2.xlsx', CNCs)

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
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(n = POP_SIZE)
    JOBS = []
    TIMES = []
    LAST = []
    for i in range(POP_SIZE):
        indv = pop[i]
        print("---------------------indiv %d---------------------"%(i))
        for job in indv:
            print(job.getWorkno())
        result = pre_evaluate(indv, standard, machines, CNCs)
        jobs = result['jobs']
        time = result['time']
        last = result['last']
        print(jobs)
        JOBS.append(jobs)
        print(time)
        TIMES.append(time)
        print(last)
        LAST.append(last)
        print("---------------------indiv %d---------------------"%(i))
        indv.fitness.values = [result['jobs'], result['time'], result['last']]
       # print(pop[i].fitness)
    avgs = [np.average(JOBS), np.average(TIMES), np.average(LAST)]
    sigmas = [np.std(JOBS), np.std(TIMES), np.std(LAST)]
    mins = [np.min(JOBS), np.min(TIMES), np.min(LAST)]
    #print(avgs, sigmas, mins)
    for i in range(POP_SIZE):
        pop[i].fitness.values = evaluate(pop[i], invert_sigma_normalize, avgs, sigmas, 3) # 파라미터 C 선택 가능
        #print(pop[i].fitness)
'''
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        return sum(individual),


    toolbox.register("mate", tools.cxPartialyMatched())
    toolbox.register("mutate", tools.mutShuffleIndexes(), indpb=0.05)
    toolbox.register("select", tools.selSPEA2(), k=)
    toolbox.register("evaluate", evaluate)
'''
