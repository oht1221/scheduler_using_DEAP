
import time
import random
import numpy as np
import genetic_operators
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
    NGEN = 1000
    POP_SIZE = MU = 30
    LAMBDA = 60
    CXPB = 0.8
    MUTPB = 0.1
    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL)
    read_CNCs('./hansun2.xlsx', CNCs)

    machines = {}
    for cnc in CNCs:
        machines[float(cnc.getNumber())] = list()
    standard = input("schedule starts on : ")
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    creator.create("FitnessMul", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, metrics = dict, fitness=creator.FitnessMul, individual_number = int)

    toolbox = base.Toolbox()
    toolbox.register("schedule", random.sample, JOB_POOL, IND_SIZE)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("cxOrdered", tools.cxOrdered)
    toolbox.register("inversion_with_displacement_mutation", genetic_operators.inversion_with_displacement_mutation)
    toolbox.register("selSPEA2", tools.selSPEA2) # top 0.5% of the whole will be selected
    toolbox.register("selTournamentDCD", tools.selTournamentDCD) # top 0.5% of the whole will be selected
    toolbox.regeister("selNSGA2", tools.selNSGA2)
    pop = toolbox.population(n=POP_SIZE)
    hof = tools.ParetoFront()
    for i in range(POP_SIZE):
        pop[i].individual_number = i
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
        indv.fitness.metrics = [jobs, time, last]
       # print(pop[i].fitness)
    avgs = [np.average(JOBS), np.average(TIMES), np.average(LAST)]
    sigmas = [np.std(JOBS), np.std(TIMES), np.std(LAST)]
    mins = [np.min(JOBS), np.min(TIMES), np.min(LAST)]
    #print(avgs, sigmas, mins)
    for i in range(POP_SIZE):
        pop[i].fitness.values = evaluate(pop[i], invert_sigma_normalize, avgs, sigmas, 3) # 파라미터 C 선택 가능
        print(pop[i].individual_number)
        print(pop[i].fitness)

    selected = toolbox.selSPEA2(individuals=pop, k=3)
    print("3 pareto optimals")
    for i in range(3):
        print("indiv # :" + str(selected[i].individual_number) + " " + str(selected[i].fitness))


    #selected = toolbox.selTournamentDCD(individuals = pop, k = 3)
    #for i in range(3):
    #    print(selected[i].fitness)


'''
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        return sum(individual),


    toolbox.register("mate", tools.cxPartialyMatched())
    toolbox.register("mutate", tools.mutShuffleIndexes(), indpb=0.05)
    toolbox.register("select", tools.selSPEA2(), k=)
    toolbox.register("evaluate", evaluate)
'''
