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

ichr = evaluation.interpret(machines, indiv1, CNCs, JOB_POOL, valve_pre_CNCs, LOK_FORGING_CNCs, LOK_HEX_CNCs)

for m in ichr.values():
    component_start_time = standard
    component_end_time = component_start_time
    # time_left_of_machine = sum([j.getTime() for j in m])
    time_left_of_machine = 0

    for u in m:
        # each_job_execution_time += j.getTime()
        times = []
        comp = u.get_component()
        time_taken = comp.getTime()
        component_end_time = component_start_time + time_taken

        startTime = datetime.datetime.fromtimestamp(int(component_start_time)).strftime('%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.fromtimestamp(int(component_end_time)).strftime('%Y-%m-%d %H:%M:%S')

        component_start_time = component_end_time
        time_left_of_machine += time_taken

        u.set_start_time(startTime)
        u.set_end_time(endTime)

for k, m in ichr.items():
    print(k)
    print("")
    for u in m:
        comp = u.get_component()
        job = comp.getJob()

        print(job.getGoodNo())
        print(job.getType())
        print(job.getLOK())
        print(u.get_start_time())
        print(u.get_end_time())
        print("")