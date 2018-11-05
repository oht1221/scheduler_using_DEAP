
import copy
from job import unit, component_unit, setting_time_unit, Component
from math import ceil

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
        job = copy.deepcopy(job_pool[i])
        indiv_ref.append(job)

    return indiv_ref


def pre_evaluate(standard, CNCs, job_pool, valve_pre_CNCs, LOK_forging_CNCs,
                 LOK_hex_CNCs, initial_times, individual):

    machines = {}
    for i, cnc in enumerate(CNCs, 0):
        cnc_number = int(cnc.getNumber())
        machines[cnc_number] = Machine()

    indiv_ref = refer_individual(individual, job_pool)
    interpreted, unassigned = interpret(machines, indiv_ref, CNCs, valve_pre_CNCs, LOK_forging_CNCs, LOK_hex_CNCs, standard)
    removesTheUnassigned(indiv_ref, unassigned)

    TOTAL_DELAYED_JOBS_COUNT = 0
    TOTAL_DELAYED_TIME = 0

    for job in indiv_ref:
        components = job.getComponents()
        last_component = components[-1] #마지막 공정이 끝난 시간
        job_end_time = last_component.getEndDateTime()
        diff = job.getDue() - (job_end_time + 60*60*24*5) #5일간 다른 공정

        if diff < 0:
            job.delayed()
            TOTAL_DELAYED_JOBS_COUNT += 1
            TOTAL_DELAYED_TIME += (-1) * diff
            for comp in components:
                comp.delayed()

    LAST_JOB_EXECUTION = max([m.getTimeLeft() for m in interpreted.values()])

    raw  = [int(TOTAL_DELAYED_JOBS_COUNT),
                int(TOTAL_DELAYED_TIME),
                int(LAST_JOB_EXECUTION)]

    fitnesses = [int(TOTAL_DELAYED_JOBS_COUNT),
                ceil((TOTAL_DELAYED_TIME) / (60 * 60)), #6시간 단위
                 ceil((LAST_JOB_EXECUTION) / (60 * 60))] #2시간 단위

    individual.assignment = interpreted
    individual.unassigned = unassigned
    individual.raw = raw
    '''for j in unassigned:
        print(j.getWorkno())
    '''
    print(fitnesses)

    return [fitnesses, interpreted]

def interpret(machines, indiv_ref, CNCs, valve_pre_CNCs, LOK_forging_CNCs, LOK_hex_CNCs, standard):
    #for v in machines.values():  # 각 machine에 있는 작업들 제거(초기화)
     #   v.clear()
    unAssigned = []
    CNCs_2jaw = tuple(filter(lambda x: x.getShape() == 0, CNCs))
    CNCs_3jaw = tuple(filter(lambda x: x.getShape() == 1, CNCs))
    CNCs_round = tuple(filter(lambda  x : (x.getShape() == 1 and not (x.getNote() == "코렛")), CNCs))
    CNCs_square = tuple(filter(lambda x : x.getShape() == 0, CNCs))
    CNCs_valve_pre = tuple(filter(lambda x : x.getNumber() in valve_pre_CNCs, CNCs))
    CNCs_LOK_size_forging = tuple(filter(lambda x : x.getNumber() in LOK_forging_CNCs, CNCs))
    CNCs_LOK_size_hex = tuple(filter(lambda x : x.getNumber() in LOK_hex_CNCs, CNCs))


    for i, j in enumerate(indiv_ref): #차후에 component단위로 배정하는 것으로 변경해야함

        result = 0

        if j.getLokFittingSize() == 1:
            if j.getType() == 0:
                result = assign(j, CNCs_LOK_size_forging, machines, unAssigned, standard)
            elif j.getType() == 1:
                result = assign(j, CNCs_LOK_size_hex, machines, unAssigned, standard)

        elif j.getType() == 0:
            result = assign(j, CNCs_2jaw, machines, unAssigned, standard)

        elif j.getType() == 1:
            result = assign(j, CNCs_3jaw, machines, unAssigned, standard)

        elif j.getType() == 2:
            result = assign(j, CNCs_round, machines, unAssigned, standard)

        elif j.getType() == 3:
            result = assign(j, CNCs_square, machines, unAssigned, standard)

        elif j.getType() == 4:
            result = assign(j, CNCs_valve_pre, machines, unAssigned, standard)

        else:
            print("job type error!")

        if result is 0:
            unAssigned.append(j)

    for n in [41, 42]:
        cnc = CNCs[n - 7]
        if len(machines[n].getPending()) != 0:
            for i, comp in enumerate(machines[n].getPending()):
                if i == 0: #최종적으로 남은 pending은 그 앞에 waiting time을 추가해줘야함.
                    assignWaitingTimeComponent(standard, machines[n], cnc, endtime=comp.getPrev().getEndDateTime())
                    print(comp.getJob().getWorkno())
                assignSettingTimeComponent(standard, machines[n], cnc)
                setTimes(comp, standard, machines[n])
                (machines[cnc.getNumber()]).attach(comp)
                comp.assignedTo(cnc)

    return machines, unAssigned

'''
def evaluate(individual, normalization, avgs, params, c = None):
    print(individual.metrics)
    scaled = normalization(individual.metrics, avgs, params, c)
    individual.fitness.values = scaled
    print(scaled)
    return scaled
'''

def assign(job, CNCs, machines, unAssigned, standard):
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

    if len(selected_CNCs) <= 0:  # 조건에 맞는 CNC가 하나도 없으면
        unAssigned.append(job)
        return -1

    components = job.getComponents()

    timeLefts = [(machines[c.getNumber()]).getTimeLeft() for c in selected_CNCs]
    minValue = min(timeLefts)
    minIndex = timeLefts.index(minValue)
    cnc = selected_CNCs[minIndex] # 선택된 cnc들 중 가장 남은시간이 적은 cnc
    cnc_number = cnc.getNumber()
    selected_machine = machines[cnc_number]
    #timeLeft = selected_machine.getTimeLeft()

    if cnc_number in [39, 40] and job.getLokFitting(): #LOK이 39, 40에 걸린 경우 : 2차는 41, 42에서
        #if selected_machine.getTimeLeft() != 0:  # setting time 설정
        assignSettingTimeComponent(standard, selected_machine, cnc)
        setTimes(components[0], standard, selected_machine)
        selected_machine.attach(components[0])
        components[0].assignedTo(cnc)

        cnc = selected_CNCs[minIndex+1] #선택된 CNC들 중에서는 39 바로 다음이 41번, 40번 바로 다음이 42번
        cnc_number = cnc.getNumber()
        selected_machine = machines[cnc_number]

        try:
            for i in range(len(components) - 1):
                #if selected_machine.getTimeLeft() != 0:  # setting time 설정
                if standard + selected_machine.getTimeLeft() < components[i].getEndDateTime():
                    selected_machine.putPending(components[i + 1])
                    continue
                assignSettingTimeComponent(standard, selected_machine, cnc)
                setTimes(components[i + 1], standard, selected_machine)
                selected_machine.attach(components[i + 1])
                components[i + 1].assignedTo(cnc)

        except Exception as ex:
            print("assgining error with job# %s occured \n"%job.getGoodCd(), len(job.getComponents()), ex)

    else:
        for comp in components: #comp1, comp2 연달아 배정(향 후 변경 가능)
            #if selected_machine.getTimeLeft() != 0:  # setting time 설정
            assignSettingTimeComponent(standard, selected_machine, cnc)
            setTimes(comp, standard, selected_machine)
            (machines[cnc.getNumber()]).attach(comp)
            comp.assignedTo(cnc)

    if cnc_number in [41, 42]:
        pendingHead = selected_machine.checkPending(standard)
        while pendingHead is not None:
            assignSettingTimeComponent(standard, selected_machine, cnc)
            setTimes(pendingHead, standard, selected_machine)
            selected_machine.attach(pendingHead)
            pendingHead.assignedTo(cnc)
            pendingHead = selected_machine.checkPending(standard)

    return 1

def assignSettingTimeComponent(standard, selected_machine, cnc):
    setting_time = Component(cycleTime=60 * 45, quantity=1, processCd= None, ifsetting=True)
    setTimes(setting_time, standard, selected_machine)
    selected_machine.attach(setting_time)
    setting_time.assignedTo(cnc)

    return 0


def assignWaitingTimeComponent(standard, selected_machine, cnc, endtime):
    waiting_time = Component(cycleTime= endtime - (selected_machine.getTimeLeft() + standard), quantity=1, processCd=None, ifwaiting = True)
    setTimes(waiting_time, standard, selected_machine)
    selected_machine.attach(waiting_time)
    waiting_time.assignedTo(cnc)

def setTimes(component, standard, selected_machine):
    component_start_time = standard + selected_machine.getTimeLeft()
    component_end_time = component_start_time + component.getTime()  # 45 minutes of setting time
    component.setStartDateTime(component_start_time)
    component.setEndDateTime(component_end_time)

    return 0

class Machine:
    def __init__(self):
        self.assignments = list()
        self.time_left = 0
        self.pending = list()

    def attach(self, component):
        self.assignments.append(component)
        self.time_left += component.getTime()

    def getTimeLeft(self):
        return self.time_left

    def getAssignments(self):
        return self.assignments

    def plusInitialTime(self, initial_time):
        self.time_left += initial_time

    def putPending(self, component):
        self.pending.append(component)

    def getPending(self):
        return self.pending

    def checkPending(self, standard):
        for c in self.pending:
            prev = c.getPrev()
            if standard + self.getTimeLeft() >= prev.getEndDateTime():
                self.pending.remove(c)
                return c
        return None


def removesTheUnassigned(indiv, unassinged):
    for u in unassinged:
        idx = indiv.index(u)
        indiv.pop(idx)

    return unassinged