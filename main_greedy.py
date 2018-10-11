from preprocessing import make_job_pool
from preprocessing import read_CNCs
import random
import time
from evaluation import pre_evaluate
from deap import tools, benchmarks, base, creator
import displays_results as dr

import job
import copy

VALVE_PRE_CNCs = {1, 2, 3, 32, 33, 34, 37, 38, 44}
LOK_FORGING_CNCs = {10, 15}
LOK_HEX_CNCs = {8, 9, 11, 12, 13}

if __name__ == "__main__":
    CNCs = []
    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = "20999999"

    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL, start, end)

    read_CNCs('./장비정보.xlsx', CNCs)

    machines = {}
    for cnc in CNCs:
        machines[float(cnc.getNumber())] = list()
    standard = input("schedule starts on : ")
    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    creator.create("FitnessMul", base.Fitness, weights=(-1.3, -1.0, -1.0))
    creator.create("Individual", list, metrics=list, fitness=creator.FitnessMul, individual_number=int, assignment=dict)

    toolbox = base.Toolbox()
    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)


    indiv = toolbox.individual()
    indiv.sort(key = lambda job_number : (JOB_POOL[job_number].getDue(), (1) * JOB_POOL[job_number].getTime()), reverse = False)
    '''for j in indiv:
        print(JOB_POOL[j].getDue())
        print(JOB_POOL[j].getTime())
    '''

    pre_evaluate(standard, CNCs, JOB_POOL, VALVE_PRE_CNCs, LOK_FORGING_CNCs, LOK_HEX_CNCs, indiv)



    print(indiv.fitness.values)

    dr.print_job_schedule(indiv, start, end, standard_in_datetime, "greedy")
