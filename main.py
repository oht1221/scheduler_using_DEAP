

import re

from deap import tools, benchmarks, base, creator, algorithms
import random
import genetic_operators
#import multiprocessing as mp
import time
from evaluation import pre_evaluate
import preprocessing as pp
import displays_results as dr

CNCs = []
POP_SIZE = MU = 10
LAMBDA = 40
MUTPB = 0.5
CXPB = 0.5
VALVE_PRE_CNCs = {1, 2, 3, 32, 33, 34, 37, 38, 44}
LOK_FORGING_CNCs = {10, 15}
LOK_HEX_CNCs = {8, 9, 11, 12, 13}
WEIGHTS = (-10.0, -1.0, -1.0)
toolbox = base.Toolbox()
creator.create("FitnessMul", base.Fitness, weights=WEIGHTS)
creator.create("individual", list, fitness=creator.FitnessMul, individual_number=int, assignment=dict,
                   unassigned=tuple, raw=tuple)


def main():

    database, username, password = pp.dbConnectionCheck()

    pp.read_CNCs('./장비정보.xlsx', CNCs)
    JOB_POOL = list()
    start = str(input("delivery date from: "))
    standard = input("schedule starts on : ")
    end = "29991212"
    NGEN = int(input("# of gen: "))

    IND_SIZE, no_cycle_time = pp.make_job_pool(JOB_POOL, start, end, database, username, password)
    LEFT_OVER = pp.getLeftOver(database, username, password)

    # end = str(input("delivery date until: "))

    hof = tools.ParetoFront()
    stats = tools.Statistics()



    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("Individual", tools.initIterate, creator.individual, toolbox.schedule)
    toolbox.register("evaluate", pre_evaluate, standard, CNCs, JOB_POOL, VALVE_PRE_CNCs,
                     LOK_FORGING_CNCs, LOK_HEX_CNCs, LEFT_OVER)
    toolbox.register("population", tools.initRepeat, list, toolbox.Individual)
    toolbox.register("mate", tools.cxPartialyMatched)
    #toolbox.register("mate", tools.cxOrdered)
    #toolbox.register("mate", tools.cxCycle)
    #toolbox.register("mutate", tools.mutInversion)
    toolbox.register("mutate", genetic_operators.simple_inversion_mutation)
    toolbox.register("select", tools.selNSGA2)

    pop = toolbox.population(n=POP_SIZE)


    start_point = time.time()

    result = algorithms.eaMuPlusLambda(pop, toolbox, mu=MU, lambda_=LAMBDA, cxpb=CXPB,
                                       mutpb=MUTPB, ngen=NGEN, stats=None, halloffame=hof, verbose=None)

    m, s = divmod((time.time() - start_point), 60)
    h, m = divmod(m, 60)

    print("------------------------------------------Hall of fame------------------------------------------------")
    for i in range(min(5, len(hof))):
        print(i + 1, hof[i].fitness.values , end = " ")
        print(i + 1, len(hof[i].assignment))
    print("------------------------------------------Hall of fame------------------------------------------------")
    
    
    print("NGEN : %d\nMu : %d\nLambda : %d\nMUTPB : %f\nCXPB : %f\n" % (NGEN, MU, LAMBDA, MUTPB, CXPB))
    print("Weights : ", WEIGHTS)

    print("%s hours %s minutes and %s seconds" % (h, m, s))



    while (1):
        printed = []
        schedules_selected = input("Choose the schedules you want to print out(press 'q' to quit) : ")
        if schedules_selected == 'q':
            print("quit")
            break
        selected = re.findall("\d+", schedules_selected)
        selected = list(map(int, selected))
        try:
            for i in selected:
                if i in printed:
                    print("%d already printed"%i)
                    continue
                dr.print_job_schedule(assignment = hof[i - 1].assignment, start = start, end = end,
                                      standard = standard_in_datetime, total_number = len(hof[i - 1]),
                                      total_number_unassgiend= hof[i -1].unassigned,
                                      schedule_type = "optimized", endsAt = standard + hof[i - 1].raw[2],
                                      numDelayed =  hof[i - 1].raw[0], no_cycle_time = no_cycle_time,
                                      mu = MU, Lambda = LAMBDA, cx = CXPB, mut = MUTPB, rank = i)
                print("%d successfully printed"%i)
                printed.append(i)
        except Exception as ex:
            print("an error occured! : ", ex)
            continue

if __name__ == "__main__":
    #pool = mp.Pool(4)
    #toolbox.register("map")
    main()
    #pool.close()
    #pool.join()