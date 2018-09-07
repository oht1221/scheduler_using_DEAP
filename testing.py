import cnc
import preprocessing
import evaluation
import random
import time
import datetime
from deap import tools, benchmarks, base, creator, algorithms

valve_pre_CNCs = [1, 2, 3, 32, 33, 34, 37, 38, 44]
LOK_FORGING_CNCs = [10, 15]
LOK_HEX_CNCs = [8, 9, 11, 12, 13]

creator.create("FitnessMul", base.Fitness, weights=(-1.2, -1.0, -1.0))
creator.create("Individual", list, metrics=list, fitness=creator.FitnessMul, individual_number=int, assignment=dict)

toolbox = base.Toolbox()


machines = {}
CNCs = []
preprocessing.read_CNCs('./장비정보.xlsx', CNCs)
for cnc in CNCs:
    machines[cnc.getNumber()] = list()



JOB_POOL = []
start = str(input("delivery date from: "))
end = str(input("delivery date until: "))
IND_SIZE = preprocessing.make_job_pool(JOB_POOL, start, end)
toolbox.register("schedule", random.sample, range(IND_SIZE), IND_SIZE)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.schedule)
indiv1 = toolbox.individual()

standard = input("schedule starts on : ")
standard_in_datetime = standard
standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
    (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
standard = int(standard)

ichr = evaluation.interpret(machines, indiv1, CNCs, JOB_POOL, valve_pre_CNCs, LOK_FORGING_CNCs, LOK_HEX_CNCs, standard)


for k, m in ichr.items():
    print(k)
    print("")
    for u in m:
        if u.isComp():
            comp = u.get_component()
            job = comp.getJob()

            print(job.getGoodNo())
            print(job.getType())
            print(job.getLOK())
            print(u.get_start_time())
            print(u.get_end_time())
            print("")
        else:
            print("setting time")
            print(u.get_start_time())
            print(u.get_end_time())
            print("")