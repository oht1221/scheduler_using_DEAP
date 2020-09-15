

import re

from deap import tools, base, creator, algorithms
import random
import genetic_operators
import time
from evaluation import evaluate
import preprocessing as pp
import displays_results as dr

CNCs = []
MUTPB = 0.25
CXPB = 0.75
VALVE_PRE_CNCs = {1, 2, 3, 32, 33, 34, 37, 38, 44}
LOK_FORGING_CNCs = {10, 15}
LOK_HEX_CNCs = {8, 9, 11, 12, 13}
WEIGHTS = (-1.0, -1.0, -1.0)
toolbox = base.Toolbox()
creator.create("FitnessMul", base.Fitness, weights=WEIGHTS)
creator.create("individual", list, fitness=creator.FitnessMul, individual_number=int, assignment=dict,
                   unassigned=tuple, raw=tuple)

#POP_SIZE = MU = int(input("MU : "))
#꺠LAMBDA = int(input("LAMBDA : "))

POP_SIZE = MU = 50
LAMBDA = 50

def main():
    server, database, username, password = pp.dbConnectionCheck_Deployment()

    pp.read_CNCs('./장비정보.xlsx', CNCs)
    JOB_POOL = list()
    start = str(input("delivery date from: "))
    end = str(input("delivery date till: "))
    standard = input("schedule starts on : ")
    NGEN = int(input("# of gen: "))

    #segmentation_cutoff = int(input("segmentation cut off: "))
    #partition_size = int(input("the size of a job partition : "))

    segmentation_cutoff = 100000000
    partition_size = 100000000

    IND_SIZE, no_cycle_time = pp.make_job_pool(JOB_POOL, start, end, server, database, username, password, segmentation_cutoff, partition_size)
    LEFT_OVER = pp.getLeftOver(server, database, username, password)

    #for j in JOB_POOL:
    #    print(j.getGoodCd(), j.getGoodNo(), j.getCycletime(), j.getType(), j.getQuantity())

    # end = str(input("delivery date until: "))

    hof = tools.HallOfFame(MU)
    #hof = tools.ParetoFront()
    standard_in_datetime = standard
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 0, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)

    toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
    toolbox.register("Individual", tools.initIterate, creator.individual, toolbox.schedule)
    toolbox.register("evaluate", evaluate, standard, CNCs, JOB_POOL, VALVE_PRE_CNCs,
                     LOK_FORGING_CNCs, LOK_HEX_CNCs, LEFT_OVER)
    toolbox.register("population", tools.initRepeat, list, toolbox.Individual)
    toolbox.register("mate", tools.cxPartialyMatched)
    #toolbox.register("mate", tools.cxOrdered)
    #toolbox.register("mate", genetic_operators.cycle_crossover)
    #toolbox.register("mutate", tools.mutInversion)
    toolbox.register("mutate", genetic_operators.inversion_with_displacement_mutation)
    toolbox.register("select", tools.selNSGA2)

    pop = toolbox.population(n=POP_SIZE)


    start_point = time.time()
    
    #미리 정렬시켜놓은 상태에서(greedy는 적용시켜 놓은 상태에서) 시작
    for ith, indiv in enumerate(pop):
        indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()),
                   reverse=False)
        f1 = toolbox.evaluate(indiv)
        #print(f1)
        indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (1) * JOB_POOL[job_number].getTime()),
                   reverse=False)
        f2 = toolbox.evaluate(indiv)
        #print(f2)
        if f1[1][0] < f2[1][0]:
            indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()),
                       reverse=False)
        elif f1[1][0] == f2[1][0]:
            if f1[1][1] < f2[1][1]:
                indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()), reverse=False)
            elif f1[1][1] == f2[1][1]:
                if f1[1][2] <= f2[1][2]:
                    indiv.sort(key=lambda job_number: (JOB_POOL[job_number].getDue(), (-1) * JOB_POOL[job_number].getTime()), reverse=False)


    result = algorithms.eaMuPlusLambda(pop, toolbox, mu=MU, lambda_=LAMBDA, cxpb=CXPB,
                                       mutpb=MUTPB, ngen=NGEN, stats=None, halloffame=hof, verbose=None)

    m, s = divmod((time.time() - start_point), 60)
    h, m = divmod(m, 60)

    print("------------------------------------------Hall of fame------------------------------------------------")
    #for i in range(min(MU, len(hof))):
    for i in range(5):
        print(i + 1, hof[i].raw)
    print("------------------------------------------Hall of fame------------------------------------------------")


    #print("NGEN : %d\nMu : %d\nLambda : %d\nMUTPB : %f\nCXPB : %f\n" % (NGEN, MU, LAMBDA, MUTPB, CXPB))
    print("delivery date from %s to %s, starting date %s"%(start, end, standard_in_datetime))
    #print("Weights : ", WEIGHTS)
    #print("MU : %d, LAMBDA : %d"%(MU, LAMBDA))
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
                dr.print_job_schedule(assignment = hof[i - 1].assignment, scores =hof[i - 1].fitness.values, start = start, end = end,
                                      standard = standard_in_datetime, total_number = len(hof[i - 1]),
                                      total_number_unassgiend= hof[i -1].unassigned,
                                      schedule_type = "optimized", endsAt = standard + hof[i - 1].raw[2],
                                      numDelayed =  hof[i - 1].raw[0], no_cycle_time = no_cycle_time,
                                      rank = i)
                print("%d successfully printed"%i)
                printed.append(i)
        except Exception as ex:
            print("an error occured! : ", ex)
            continue


if __name__ == "__main__":
    '''pool = pool.Pool(40)
    toolbox.register("map", pool.map)
    while 1:
        main()
        pool.close()
        pool.join()'''
    main()
