import preprocessing as pp
import random
import time
from evaluation import evaluate, evaluate2
from deap import tools, base, creator
import displays_results as dr
import simulated_annealing as SA

CNCs = []
VALVE_PRE_CNCs = {1, 2, 3, 32, 33, 34, 37, 38, 44}
LOK_FORGING_CNCs = {10, 15}
LOK_HEX_CNCs = {8, 9, 11, 12, 13}

if __name__ == "__main__":
    database, username, password = pp.dbConnectionCheck()

    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = str(input("delivery date till: "))
    standard = input("schedule starts on : ")
    segmentation_cut_off = int(input("segmentation_cut_off: "))
    segmentation_size = int(input("segmentation_size: "))

    IND_SIZE , no_cycle_time = TOTAL_NUMBER_OF_THE_POOL = pp.make_job_pool(JOB_POOL, start, end, database, username, password, segmentation_cut_off, segmentation_size)
    LEFT_OVER = pp.getLeftOver(database, username, password)
    pp.read_CNCs('./장비정보.xlsx', CNCs)


    for j in JOB_POOL:
        print(j.getGoodCd(), j.getGoodNo(), j.getCycletime(), j.getType(), j.getQuantity())

    machines = {}
    for cnc in CNCs:
        machines[float(cnc.getNumber())] = list()

    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 0, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    creator.create("FitnessMul", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, metrics=list, fitness=creator.FitnessMul, individual_number=int, assignment=dict)

    toolbox = base.Toolbox()
    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)
    toolbox.register("evaluate", evaluate, standard, CNCs, JOB_POOL, VALVE_PRE_CNCs,
                     LOK_FORGING_CNCs, LOK_HEX_CNCs, LEFT_OVER)

    indiv = toolbox.individual()

    indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()),
               reverse=False)
    f1 = toolbox.evaluate(indiv)
    print(f1)
    indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (1) * JOB_POOL[job_number].getTime()),
               reverse=False)
    f2 = toolbox.evaluate(indiv)
    print(f2)
    if f1[1][0] < f2[1][0]:
        indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()),
                   reverse=False)

    start_point = time.time()

    indiv_optimized = SA.simulated_annealing(indiv, 100, 0.97, standard, CNCs, JOB_POOL, VALVE_PRE_CNCs, LOK_FORGING_CNCs, LOK_HEX_CNCs, LEFT_OVER,)

    m, s = divmod((time.time() - start_point), 60)
    h, m = divmod(m, 60)
    print("%s hours %s minutes and %s seconds" % (h, m, s))

    result = toolbox.evaluate(indiv_optimized)
    indiv_optimized.fitness.values = result[0]

    print(indiv_optimized.fitness.values)

    dr.print_job_schedule(assignment = indiv_optimized.assignment, scores = indiv_optimized.fitness.values, start=start, end=end,
                          standard=standard_in_datetime, total_number=len(indiv_optimized),
                          total_number_unassgiend=indiv_optimized.unassigned,
                          schedule_type="greedy", endsAt=standard + indiv_optimized.raw[2],
                          numDelayed=indiv_optimized.raw[0], no_cycle_time=no_cycle_time,
                          mu=0, Lambda=0, cx=0, mut=0, rank=0)
