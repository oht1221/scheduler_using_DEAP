from preprocessing import make_job_pool
from preprocessing import read_CNCs
import random
import time
from evaluation import pre_evaluate
from deap import tools, benchmarks, base, creator
import displays_results as dr

import job
import copy


if __name__ == "__main__":
    CNCs = []
    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = str(input("delivery date until: "))

    IND_SIZE = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL, start, end)

    read_CNCs('./hansun2.xlsx', CNCs)

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
    indiv.sort(key = lambda job_number : (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()), reverse = False)
    for j in indiv:
        print(JOB_POOL[j].getDue())
        print(JOB_POOL[j].getTime())


    pre_evaluate(standard, machines, CNCs, JOB_POOL, indiv)

    print(indiv.fitness.values)

    dr.print_job_schedule(indiv, start, end, standard_in_datetime, "greedy")
