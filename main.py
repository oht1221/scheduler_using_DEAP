
import random
import numpy as np

import re

from deap import tools, benchmarks, base, creator, algorithms
import random

import genetic_operators
from scoop import futures
import time
from evaluation import pre_evaluate
from preprocessing import make_job_pool, read_CNCs
import displays_results as dr

toolbox = base.Toolbox()
CNCs = []
NGEN = 1000
POP_SIZE = MU = 10
MUTPB = 0.4
LAMBDA = 20
CXPB = 0.6
VALVE_PRE_CNCs = [1, 2, 3, 32, 33, 34, 37, 38, 44]
LOK_FORGING_CNCs = [10, 15]
LOK_HEX_CNCs = [8, 9, 11, 12, 13]

#start = sys.argv[1]

creator.create("FitnessMul", base.Fitness, weights=(-2.0, -1.0, -1.0))
creator.create("individual", list, fitness=creator.FitnessMul, individual_number=int, assignment=dict,
               unassigned=list)

if __name__ == "__main__":

    CNCs = []
    read_CNCs('./장비정보.xlsx', CNCs)

    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = "29991212"
    # end = str(input("delivery date until: "))
    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL, start, end)

    hof = tools.ParetoFront()
    stats = tools.Statistics()
    toolbox = base.Toolbox()

    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("Individual", tools.initIterate, creator.individual, toolbox.schedule)

    toolbox.register("population", tools.initRepeat, list, toolbox.Individual)
    toolbox.register("mate", tools.cxPartialyMatched)
    # toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", genetic_operators.inversion_with_displacement_mutation)
    toolbox.register("selTournamentDCD", tools.selTournamentDCD)  # top 0.5% of the whole will be selected
    toolbox.register("select", tools.selNSGA2)
    #toolbox.register("map", futures.map)
    toolbox.register("map", futures.map)

    start_point = time.time()

    # toolbox.register("select", tools.selSPEA2)

    standard = input("schedule starts on : ")
    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    toolbox.register("evaluate", pre_evaluate, standard, CNCs, JOB_POOL, VALVE_PRE_CNCs,
                     LOK_FORGING_CNCs, LOK_HEX_CNCs)

    pop = toolbox.population(n=POP_SIZE)


    NGEN = int(input("# of gen: "))

    result = algorithms.eaMuPlusLambda(pop, toolbox, mu=MU, lambda_=LAMBDA, cxpb=CXPB,
                                       mutpb=MUTPB, ngen=NGEN, stats=None, halloffame=hof, verbose=None)


    print("------------------------------------------Hall of fame------------------------------------------------")
    for i in range(len(hof)):
        print(i + 1, hof[i].fitness.values , end = " ")
        print(i + 1, len(hof[i].assignment))
    print("------------------------------------------Hall of fame------------------------------------------------")

    m, s = divmod((time.time() - start_point), 60)
    h, m = divmod(m, 60)

    print("%s hours %s minutes and %s seconds" % (h, m, s))

    schedules_selected = input("Choose the schedules you want to print out : ")
    selected = re.findall("\d+", schedules_selected)
    selected = list(map(int, selected))


    while (1):
        try:
            for i in selected:
                print(i)
                dr.print_job_schedule(assignment = hof[i - 1].assignment, start = start, end = end, standard = standard_in_datetime,
                                      total_number = len(hof[i - 1]), total_number_unassgiend= len(hof[i -1].unassigned), schedule_type = "optimized", rank = i)
            break
        except Exception as ex:
            print("an error occured! : ", ex)
            continue
