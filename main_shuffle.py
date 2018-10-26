from preprocessing import make_job_pool, read_CNCs, getLeftOver

import random
import time
from evaluation import pre_evaluate
from deap import tools, base, creator
import copy
import displays_results as dr

VALVE_PRE_CNCs = {1, 2, 3, 32, 33, 34, 37, 38, 44}
LOK_FORGING_CNCs = {10, 15}
LOK_HEX_CNCs = {8, 9, 11, 12, 13}
LEFT_OVER = getLeftOver()

if __name__ == "__main__":
    CNCs = []
    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = '29991231'
    standard = input("schedule starts on : ")
    IND_SIZE, no_cycle_time = TOTAL_NUMBER_OF_THE_POOL = make_job_pool(JOB_POOL, start, end)
    read_CNCs('./장비정보.xlsx', CNCs)
    toolbox = base.Toolbox()

    machines = {}
    for cnc in CNCs:
        machines[int(cnc.getNumber())] = list()


    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)
    WEIGHTS = (-2.0, -1.0, -1.0)
    creator.create("FitnessMul", base.Fitness, weights=WEIGHTS)
    creator.create("individual", list, fitness=creator.FitnessMul, individual_number=int, assignment=dict, unassigned=tuple, raw=tuple)


    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("Individual", tools.initIterate, creator.individual, toolbox.schedule)

    best = toolbox.Individual()
    best.fitness.values = [10000, 100000000, 100000000]

    start_point = time.time()
    counter = 0
    while(1):
        counter += 1
        counter = counter % 100
        indiv = toolbox.Individual()
        indiv.fitness.values = pre_evaluate(standard, CNCs, JOB_POOL, VALVE_PRE_CNCs,
                     LOK_FORGING_CNCs, LOK_HEX_CNCs, LEFT_OVER, indiv)

        if indiv.fitness.values[0] < best.fitness.values[0]:
            best = copy.deepcopy(indiv)
        if counter == 0:
            print("best so far: ", end='')
            print(best.fitness.values)
            m, s = divmod((time.time() - start_point), 60)
            h, m = divmod(m, 60)
            print("%s hours %s minutes and %s seconds" % (h, m, s))



    #dr.print_job_schedule(best, start, end, standard_in_datetime, "shuffle")
