from job import *

class CNC:
    def __init__(self, number = ' ', ground = ' ', ceiling = ' ', shape = ' ', type = ' '):
        self.number = number
        self.ground = ground
        self.ceiling = ceiling
        self.shape = shape
        self.type = type
        self.jobQ = deque()
        self.timeLeft = 0

    def print_info(self):
        print("CNC No. : %s\nSize : %s ~ %s\nshape : %s\ntype : %s\n"%(self.number,
                                                                        self.ground,
                                                                        self.ceiling,
                                                                        self.shape,
                                                                        self.type))
    def print_state(self):
        i = 0
        for j in self.jobQ:
            i = (i + 1) % 5
            print('|  ')
            #print(j.getNumber(), end=' (')
            #for n in range(len(j.getSeries())):
            #    print(j.getComponent(n).ifDone(), end = ' ')
            #print(end = ') ')
            print (j.getTime())
            print('  |')
            if(i == 0): print(' ')
        print(' ')
        print(self.get_timeLeft())
        print('\n')

    def enQ(self, in_progress, *element):
        if len(self.get_jobQ()) == 0:
            in_progress.appendleft(element[0])
        if type(element[0]) is Job:
            self.jobQ.appendleft(element[0])
            self.update_timeLeft(element[0])

        if type(element[0]) is Component:
            self.jobQ.appendleft(element[0])
            self.update_timeLeft(element[0])



    def deQ(self):
        self.jobQ.pop()

    def update_timeLeft(self, element):
        self.timeLeft += element.getTime()

    def get_jobQ(self):
        return self.jobQ

    def get_timeLeft(self):
        self.timeLeft = sum([job.getTime() for job in self.jobQ])
        return int(self.timeLeft)

    def getGround(self):
        return self.ground

    def getCeiling(self):
        return self.ceiling

    def getNumber(self):
        return self.number

    def getShape(self):
        return self.shape

    def inProcess(self):
        j = self.jobQ[-1]
        for i in range(3):
            c = j.getComponent[i]
            if not c.ifDone():
                return c

    def update_due(self):
        for job in self.jobQ:
            job.update_due()

    def on_time(self, assignment):
        return assignment.getDue() - self.get_timeLeft() + assignment.getTime()