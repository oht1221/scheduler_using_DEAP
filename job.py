#-*-coding:utf-8-*-

from collections import deque
import random
import numpy as np

class Job:
    def __init__(self, workno, goodNo, goodCd, quantity, time = None ,type = None, size = None, rawNo = None, rawCd = None, due = 0, LOK = None):
        self.workno = workno
        self.goodNo = goodNo
        self.goodCd = goodCd
        self.timeLeft = sum(time) * quantity + 60*60*24*4# (60*60)*(24)*(5) + (60*60) #타공정 소요시간 + 새셋팅 시간
        self.type = type
        self.size = size
        self.rawNo = rawNo
        self.rawCd = rawCd
        self.quantity = quantity
        self.cyctleTime = time
        #self.series = []
        self.series  = [Component(time[i], self, quantity) for i in range(len(time))]
        self.due  = due
        self.cnc = None
        self.msg = None
        self.startDate = None
        self.endDate = None
        self.LOK = LOK

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

    def getGoodCd(self):
        return self.goodCd

    def getGoodNo(self):
        return self.goodNo

    def getTime(self):
        self.timeLeft = sum([component.getTime() for component in self.series])
        return self.timeLeft

    def getType(self):
        return self.type

    def getDue(self):
        return self.due

    def getLOK(self):
        return self.LOK

    def getQuantity(self):
        return self.quantity

    def getCycletime(self):
        return self.cyctleTime

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
        self.cnc = None

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

    def assignedTo(self, cnc):
        self.cnc = cnc

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
    def __init__(self, start_time = None, end_time = None):
        self.start_time = start_time
        self.end_time = end_time
        self.delayed = False

    def isDelayed(self):
        return self.delayed

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_component(self):
        return self.component

    def set_delayed(self):
        self.delayed = True

    def set_start_time(self, start_time):
        self.start_time = start_time
        return self.start_time

    def set_end_time(self, end_time):
        self.end_time = end_time
        return self.end_time

class component_unit(unit):
    def __init__(self, component, start_time = None, end_time = None):
        super(component_unit, self).__init__(start_time, end_time)
        self.component = component

    def get_component(self):
        return self.component

class setting_time_unit(unit):
    def __init__(self, start_time=None, end_time=None):
        super(setting_time_unit, self).__init__(start_time, end_time)
        self.setting = True

    def isSetting(self):
        return self.setting

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




