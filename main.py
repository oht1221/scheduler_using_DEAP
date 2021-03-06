
import time
import random
import numpy as np
import genetic_operators
from preprocessing import make_job_pool
from preprocessing import read_CNCs
from deap import tools, benchmarks, base, creator, algorithms
import time, array, random, copy, math
from evaluation import evaluate, invert_linear_normalize, invert_sigma_normalize, pre_evaluate, Machine
import displays_results as dr


start_point = time.time()

if __name__ == "__main__":
    CNCs = []
    JOB_POOL = list()
    NGEN = 10
    POP_SIZE =  MU = 30
    MUTPB = 0.5
    LAMBDA = 25
    CXPB = 0.5
    VALVE_PRE_CNCs = [1, 2, 3, 32, 33, 34, 37, 38, 44]
    LOK_FORGING_CNCs = [10, 15]
    LOK_HEX_CNCs = [8, 9, 11, 12, 13]

    start = str(input("delivery date from: "))
    #end = str(input("delivery date until: "))
    end = "29991212"
    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL, start, end)
    read_CNCs('./장비정보.xlsx', CNCs)

    standard = input("schedule starts on : ")
    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    creator.create("FitnessMul", base.Fitness, weights=(-2.0, -1.0, -1.0))
    creator.create("Individual", list, metrics = list, fitness=creator.FitnessMul, individual_number = int, assignment = dict, unassigned = list)

    toolbox = base.Toolbox()
    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    #toolbox.register("mate", tools.cxPartialyMatched)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", genetic_operators.inversion_with_displacement_mutation)
    toolbox.register("selTournamentDCD", tools.selTournamentDCD) # top 0.5% of the whole will be selected
    toolbox.register("select", tools.selNSGA2)
    #toolbox.register("select", tools.selSPEA2)


    pop = toolbox.population(n=POP_SIZE)
    for i in range(POP_SIZE):
        pop[i].individual_number = i
    JOBS = []
    TIMES = []
    LAST = []
    '''
    for i in range(POP_SIZE):
        indiv = pop[i]
        print("---------------------indiv %d---------------------"%(i))
        for j in indiv:
            print(JOB_POOL[j].getWorkno())
        result = pre_evaluate(indiv, standard, machines, CNCs, JOB_POOL)
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
        indiv.metrics.append(jobs)
        indiv.metrics.append(time)
        indiv.metrics.append(last)
       # print(pop[i].fitness)
    avgs = [np.average(JOBS), np.average(TIMES), np.average(LAST)]
    sigmas = [np.std(JOBS), np.std(TIMES), np.std(LAST)]
    mins = [np.min(JOBS), np.min(TIMES), np.min(LAST)]
    '''
    #toolbox.register("evaluate", lambda ind : evaluate(ind, invert_sigma_normalize, avgs, sigmas, 3))
    toolbox.register("evaluate", pre_evaluate, standard, CNCs, JOB_POOL, VALVE_PRE_CNCs, LOK_FORGING_CNCs, LOK_HEX_CNCs)
    '''
    for i in range(POP_SIZE):
        pop[i].fitness.values = evaluate(pop[i], invert_sigma_normalize, avgs, sigmas, 3) # 파라미터 C 선택 가능
        print(pop[i].individual_number)
        print(pop[i].fitness)
    '''

    '''
    selected = toolbox.selSPEA2(individuals=pop, k=5)
    print("5 pareto optimals")
    for i in range(5):
        print("indiv # :" + str(selected[i].individual_number) + " " + str(selected[i].fitness))
    '''
    hof = tools.ParetoFront()
    stats = tools.Statistics()
    stats.register("agv", np.average)
    stats.register("min", np.min)
    result = algorithms.eaMuPlusLambda(pop, toolbox, mu = MU, lambda_ = LAMBDA, cxpb = CXPB,
                        mutpb = MUTPB, ngen = NGEN, stats = None, halloffame = hof, verbose = None)
    print("------------------------------------------Hall of fame------------------------------------------------")
    for i in range(len(hof)):
        print(i + 1, hof[i].fitness.values)
    print("------------------------------------------Hall of fame------------------------------------------------")

    m, s = divmod((time.time() - start_point), 60)
    h, m = divmod(m, 60)
    print("%s hours %s minutes and %s seconds" %(h, m, s))
    schedules_selected = input("Choose the schedules you want to print out : ")
    selected = schedules_selected.split(" ")
    selected = list(map(int, selected))
    while(1):
        try:
            for i in selected:
                dr.print_job_schedule(hof[i - 1], start, end, standard_in_datetime, "optimized", i)
            break
        except Exception as ex:
            print("an error occured! : ", ex)
            continue

