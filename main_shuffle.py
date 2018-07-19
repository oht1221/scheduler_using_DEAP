from preprocessing import make_job_pool
from preprocessing import read_CNCs
import random
import time
from evaluation import pre_evaluate
from deap import tools, benchmarks, base, creator
import copy
import displays_results as dr

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

    creator.create("FitnessMul", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, metrics=list, fitness=creator.FitnessMul, individual_number=int, assignment=dict)

    toolbox = base.Toolbox()
    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)

    best = toolbox.individual()
    best.fitness.values = [10000,100000000,100000000]
    for i in range(0,10000000):
        indiv = toolbox.individual()
        pre_evaluate(standard, machines, CNCs, JOB_POOL, indiv)

        if indiv.fitness.values[0] < best.fitness.values[0]:
            best = copy.deepcopy(indiv)

        print("best so far: ", end='')
        print(best.fitness.values)


    dr.print_job_schedule(best, start, end, standard_in_datetime, "shuffle")
