import preprocessing as pp
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
    database, username, password = pp.dbConnectionCheck()

    CNCs = []
    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = str(input("delivery date till: "))
    standard = input("schedule starts on : ")

    IND_SIZE , no_cycle_time = TOTAL_NUMBER_OF_THE_POOL = pp.make_job_pool(JOB_POOL, start, end, database, username, password)
    LEFT_OVER = pp.getLeftOver(database, username, password)
    pp.read_CNCs('./장비정보.xlsx', CNCs)

    machines = {}
    for cnc in CNCs:
        machines[float(cnc.getNumber())] = list()

    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 8, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    creator.create("FitnessMul", base.Fitness, weights=(-1.0, -3.0, -1.0))
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

    result = pre_evaluate(standard, CNCs, JOB_POOL, VALVE_PRE_CNCs, LOK_FORGING_CNCs, LOK_HEX_CNCs, LEFT_OVER, indiv)
    indiv.fitness.values = result[0]

    print(indiv.fitness.values)

    dr.print_job_schedule(assignment = indiv.assignment, scores = indiv.fitness.values, start=start, end=end,
                          standard=standard_in_datetime, total_number=len(indiv),
                          total_number_unassgiend=indiv.unassigned,
                          schedule_type="greedy", endsAt=standard + indiv.raw[2],
                          numDelayed=indiv.raw[0], no_cycle_time=no_cycle_time,
                          mu=0, Lambda=0, cx=0, mut=0, rank=0)
