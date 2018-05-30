from collections import deque
import random
import numpy as np

class Job:
    def __init__(self, workno, good_num, quantity, time ,type = None, size = None,  workdate = None, due = 0):
        self.workno = workno
        self.worodate = workdate
        self.good_num = good_num
        self.timeLeft = sum(time) * quantity # (60*60)*(24)*(5) + (60*60) #타공정 소요시간 + 새셋팅 시간
        self.type = type
        self.size = size
        self.quantity = quantity
        #self.series = []
        self.series  = [Component(time[i], self, quantity) for i in range(len(time))]
        self.due  = due
        self.cnc = None
        self.msg = None
        self.startDate = None
        self.endDate = None

    def ifAllDone(self):
        return np.all([(self.getSeries())[i].ifDone() for i in range(len(self.getSeries()))])

    def update_due(self):
        self.due -= 1

    def getWorkno(self):
        return self.workno

    def getSeries(self):
        return self.series

    def getComponent(self):
        return self.series

    def getSize(self):
        return self.size

    def getGoodNum(self):
        return self.good_num

    def getTime(self):
        self.timeLeft = sum([component.getTime() for component in self.series])
        return self.timeLeft

    def getType(self):
        return self.type

    def getDue(self):
        return self.due

    def assignedTo(self, cnc):
        self.cnc = cnc

    def setMsg(self, msg):
        self.msg = msg


class Component:
    def __init__(self, cycleTime, job, quantity):
        self.cycleTime = cycleTime
        self.done = False
        self.partOf = job
        self.count = 0 #count가 cycletime 만큼 올라가면 제품 하나를 완성했다고 가정
        self.quantity = quantity
        self.timeLeft = cycleTime * quantity
        self.endDateTime = None
        self.startDateTime = None

    def spendTime(self, unitTime):
        self.timeLeft = self.timeLeft - unitTime
        self.counter(unitTime)
        if(self.timeLeft <= 0):
            self.setTime(0)
            self.turnDone()

    def counter(self, unitTime):
        self.count = (self.count + unitTime) % self.cycleTime
        if(self.count == 0):
            self.quantity += -1

    def getTime(self):
        self.timeLeft = self.cycleTime * self.quantity
        return self.timeLeft

    def getStartDateTime(self):
        return self.startDateTime

    def getEndDateTime(self):
        return self.endDateTime

    def ifDone(self):
        return self.done

    def getJob(self):
        return self.partOf

    def turnDone(self):
        self.done = True

    def setTime(self, time):
        self.timeLeft = time

    def setStartDateTime(self, start):
        self.startDateTime = start

    def setEndDateTime(self, end):
        self.endDateTime = end

    def completeOnePiece(self):
        self.count += 1
        self.quantity -= 1

        return self.quantity
"""
class NormalCompoenet(Component):
    def __init__(self, cycleTime, job, quantity):
        super().__init__(cycleTime, job)
        self.quantity = quantity
        self.timeLeft = cycleTime * quantity

class ReplacementComponent(Component):
    def __init__(self, cycleTime, job):
        super().__init__(cycleTime, job)
"""

class unit:
    def __init__(self, job, times = None):
        self.job = job
        self.times = times

    def get_times(self):
        return self.times
    def get_job(self):
        return self.job

    def set_times(self, times):
        self.times = times
        return self.times

class score_ichr:
    def __init__(self, delayed_jobs = None, delayed_time = None, last_job = None,):
        self.delayed_jobs = delayed_jobs
        self.delayed_time = delayed_time
        self.last_job = last_job

    def get_delayed_jobs(self):
        return self.delayed_jobs
    def get_delayed_time(self):
        return self.delayed_time
    def get_last_job(self):
        return self.last_job

    def set_delayed_jobs(self, delayed_jobs):
        self.delayed_jobs = delayed_jobs
        return self.delayed_jobs
    def set_delayed_time(self, delayed_time):
        self.delayed_time = delayed_time
        return self.delayed_time
    def set_last_job(self, last_job):
        self.last_job = last_job
        return self.last_job




