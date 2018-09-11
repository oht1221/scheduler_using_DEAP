import datetime
import numpy as np
import copy
from job import unit, component_unit, setting_time_unit


def invert_linear_normalize(fitnesses, avgs, mins, c= None):
    scaled = []
    for i in range(avgs):
        normalized = avgs[i] * (fitnesses[i] - mins[i]) / (avgs[i] - mins[i])
        scaled.append(normalized)
    return scaled

def invert_sigma_normalize(fitnesses, avgs, sigmas, c):
    scaled = []
    for i in range(len(avgs)):
        normalized = ((fitnesses[i] - avgs[i] + c * sigmas[i]) / sigmas[i]) #standardization
        if normalized > 0:
            scaled.append(normalized)
        else:
            scaled.append(0)
    return scaled

def splitPool(indiv, normPool, hexPool, job_pool):
    jobs = list()
    for i in indiv:
        jobs.append(job_pool[i])
    for i,assignment in enumerate(jobs):
        if assignment.getType() == 0:
            normPool.append(assignment)

        elif assignment.getType() == 1:
            hexPool.append(assignment)

    return 0

def refer_individual(indiv, job_pool):
    indiv_ref = []
    for i in indiv:
        indiv_ref.append(job_pool[i])

    return indiv_ref

def interpret(machines, indiv, CNCs, job_pool, valve_pre_CNCs, LOK_forging_CNCs, LOK_hex_CNCs, standard):
    for v in machines.values():  # 각 machine에 있는 작업들 제거(초기화)
        v.clear()
    unAssigned = []
    indiv_ref = refer_individual(indiv, job_pool)

    CNCs_2jaw = list(filter(lambda x: x.getShape() == 0, CNCs))
    CNCs_3jaw = list(filter(lambda x: x.getShape() == 1, CNCs))
    CNCs_round = list(filter(lambda  x : (x.getShape() == 1 and not (x.getNote() == "코렛")), CNCs))
    CNCs_square = list(filter(lambda x : x.getShape() == 0, CNCs))
    CNCs_valve_pre = list(filter(lambda x : x.getNumber() in valve_pre_CNCs, CNCs))
    CNCs_LOK_size_forging = list(filter(lambda x : x.getNumber() in LOK_forging_CNCs, CNCs))
    CNCs_LOK_size_hex = list(filter(lambda x : x.getNumber() in LOK_hex_CNCs, CNCs))


    for i, j in enumerate(indiv_ref):

        if j.lok_fitting_size == 1:
            if j.getType() == 0:
                assign(j, CNCs_LOK_size_forging, machines, unAssigned)
            elif j.getType() == 1:
                assign(j, CNCs_LOK_size_hex, machines, unAssigned)

        elif j.getType() == 0:
            assign(j, CNCs_2jaw, machines, unAssigned)

        elif j.getType() == 1:
            assign(j, CNCs_3jaw, machines, unAssigned)

        elif j.getType() == 2:
            assign(j, CNCs_round, machines, unAssigned)

        elif j.getType() == 3:
            assign(j, CNCs_square, machines, unAssigned)

        elif j.getType() == 4:
            assign(j, CNCs_valve_pre, machines, unAssigned)

        else:
            print("job type error!")


    interpreted = {}
    for k, v in machines.items():
        interpreted[k] = []
        component_start_time = standard
        component_end_time = component_start_time
        time_left_of_machine = 0

        for comp in v:
            time_taken = comp.getTime()
            component_end_time = component_start_time + time_taken

            startTime = datetime.datetime.fromtimestamp(int(component_start_time)).strftime('%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.fromtimestamp(int(component_end_time)).strftime('%Y-%m-%d %H:%M:%S')
            new = component_unit(comp, startTime, endTime)

            component_start_time = component_end_time
            time_left_of_machine += time_taken

            component_end_time = component_start_time + 60 * 45
            startTime = datetime.datetime.fromtimestamp(int(component_start_time)).strftime('%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.fromtimestamp(int(component_end_time)).strftime('%Y-%m-%d %H:%M:%S')

            setting_time = setting_time_unit(startTime, endTime)

            component_start_time = component_end_time
            time_left_of_machine += 60 * 45

            interpreted[k].append(new)
            interpreted[k].append(setting_time)


        try:
            interpreted[k].pop()
        except Exception as ex:
            continue

    '''
    for m in interpreted.values():
        component_start_time = standard
        component_end_time = component_start_time
        time_left_of_machine = 0

        for u in m:
            comp = u.get_component()
            time_taken = comp.getTime()
            component_end_time = component_start_time + time_taken

            startTime = datetime.datetime.fromtimestamp(int(component_start_time)).strftime('%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.fromtimestamp(int(component_end_time)).strftime('%Y-%m-%d %H:%M:%S')

            component_start_time = component_end_time
            time_left_of_machine += time_taken

            u.set_start_time(startTime)
            u.set_end_time(endTime)
    '''
    return interpreted

def interpret2(machines, indiv, CNCs, job_pool):
    for v in machines.values():  # 각 machine에 있는 작업들 제거(초기화)
        v.clear()
    unAssigned = []
    '''for cnc in CNCs:
        machines[cnc.getNumber()] = list()'''
    forging = list()
    hex = list()
    round = list()
    square = list()
    valvePre = list()
    splitPool(indiv, forging, hex, round, square, valvePre, job_pool)
    # normPool.sort(key=lambda x: x.getDue())
    # hexPool.sort(key=lambda x: x.getDue())
    # normPool = permutations(normPool,len(normPool))
    # hexPool = permutations(hexPool,len(hexPool))
    normCNCs = list(filter(lambda x: x.getShape() == 0, CNCs))
    hexCNCs = list(filter(lambda x: x.getShape() == 1, CNCs))
    # sortedNormPool = sorted(normPool, key = lambda j : j.getDue())
    # sortedHexPool = sorted(hexPool, key = lambda j: j.getDue())

    for i, j in enumerate(forging):

        selected_CNCs = []
        for c in normCNCs:
            if c.getGround() <= j.getSize() <= c.getCeiling():  # size 맞는 CNC는 모두 찾음
                selected_CNCs.append(c)

        timeLefts = [sum([j.getTime() for j in machines[c.getNumber()]]) for c in selected_CNCs]
        if len(timeLefts) <= 0:  # 조건에 맞는 CNC가 하나도 없으면
            unAssigned.append(j)
            continue
        minValue = min(timeLefts)
        minIndex = timeLefts.index(minValue)
        cnc = selected_CNCs[minIndex]
        (machines[cnc.getNumber()]).append(j)
        j.assignedTo(cnc)


    for i, j in enumerate(hex):

        selected_CNCs = []
        for c in hexCNCs:
            if (c.getGround() <= j.getSize() <= c.getCeiling()):  # size 맞는 CNC는 모두 찾음
                selected_CNCs.append(c)

        timeLefts = [sum([j.getTime() for j in machines[c.getNumber()]]) for c in selected_CNCs]
        if len(timeLefts) <= 0:  # 조건에 맞는 CNC가 하나도 없으면
            unAssigned.append(j)
            continue
        minValue = min(timeLefts)
        minIndex = timeLefts.index(minValue)
        cnc = selected_CNCs[minIndex]
        (machines[cnc.getNumber()]).append(j)
        j.assignedTo(cnc)

    interpreted = {}
    for k, v in machines.items():
        interpreted[k] = []
        for comp in v:
            new = unit(comp)
            interpreted[k].append(new)

    return interpreted

def pre_evaluate(standard, machines, CNCs, job_pool, valve_pre_CNCs, LOK_forging_CNCs, LOK_hex_CNCs, individual):
    interpreted = interpret(machines, individual, CNCs, job_pool, valve_pre_CNCs, LOK_forging_CNCs, LOK_hex_CNCs, standard)

    TOTAL_DELAYED_JOBS_COUNT = 0
    TOTAL_DELAYED_TIME = 0
    LAST_JOB_EXECUTION = 0
    output = {}

    diff = j.getDue() - (component_end_time + 60*60*24*5) #5일간 다른 공정
    # time_left_of_machine += j.getTime()
    if diff < 0:
        TOTAL_DELAYED_JOBS_COUNT += 1
        TOTAL_DELAYED_TIME += (-1) * diff
        u.set_delayed()

        if time_left_of_machine > LAST_JOB_EXECUTION:
            LAST_JOB_EXECUTION = time_left_of_machine

    output['jobs'] = int(TOTAL_DELAYED_JOBS_COUNT)
    output['time'] = int((TOTAL_DELAYED_TIME) / (60 * 30))
    output['last'] = int((LAST_JOB_EXECUTION) / (60 * 30))
    individual.fitness.values = [output['jobs'], output['time'], output['last']]
    individual.assignment = ichr
    print(individual.fitness.values)
    return individual.fitness.values


def evaluate(individual, normalization, avgs, params, c = None):
    print(individual.metrics)
    scaled = normalization(individual.metrics, avgs, params, c)
    individual.fitness.values = scaled
    print(scaled)
    return scaled


def assign(job, CNCs, machines, unAssigned):
    selected_CNCs = []
    type = job.getType()
    if type in [0,1,2]:
        for c in CNCs:
            if c.getGround() <= job.getSize() <= c.getCeiling():  # size 맞는 CNC는 모두 찾음
                selected_CNCs.append(c)
    elif type == 3:
        selected_CNCs = CNCs
    elif type == 4:
        selected_CNCs = CNCs
    elif type == 5:
        selected_CNCs = CNCs

    if len(selected_CNCs) <= 0:  # 조건에 맞는 CNC가 하나도 없으면
        unAssigned.append(job)

        return -1

    components = job.getComponent()

    timeLefts = [sum([j.getTime() for j in machines[c.getNumber()]]) for c in selected_CNCs]
    minValue = min(timeLefts)
    minIndex = timeLefts.index(minValue)
    cnc = selected_CNCs[minIndex]
    cnc_number = cnc.getNumber()

    if cnc_number in [39, 40] and job.getLokFitting():
        (machines[cnc_number]).append(components[0])
        components[0].assignedTo(cnc)
        cnc_next = selected_CNCs[minIndex+1]
        try:
            (machines[cnc_number + 2]).append(components[1])
            components[1].assignedTo(cnc_next)

        except Exception as ex:
            pass

    else:
        for comp in components:
            (machines[cnc.getNumber()]).append(comp)
            comp.assignedTo(cnc)

    return 0