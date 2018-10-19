from cnc import *
from job import *
import xlrd
import random
import numpy as np
import accessDB
from itertools import permutations
import time
import copy

def read_CNCs(input, CNCs):
    workbook = xlrd.open_workbook(input)

    worksheet = workbook.sheet_by_name('기계정보')

    n_cols = worksheet.ncols
    n_rows = worksheet.nrows

    for i in range(2, 47):  # 1, 2, 6, 8, 10, 16, 22번 cnc
        row = worksheet.row_values(i)
        number = int(row[1])
        shape = None
        if str(row[2]) == "2JAW":  # 2JAW 면 shape이 0, 3JAW면 shape이 1
            shape = 0
        elif str(row[2]) == "3JAW":
            shape = 1
        type = str(row[3])
        size = str(row[4])
        note = str(row[5])

        if size.find('~') == -1:
            continue  # '후가공' cnc는 제외
        ground = size.split('~')[0]
        ground = float(ground[1:])

        try:
            ceiling = float(size.split('~')[1])
        except ValueError:
            ceiling = 1000.0

        cnc = CNC(number, ground, ceiling, shape, type, note)
        CNCs.append(cnc)

    return

def make_job_pool(job_pool, start, end):
    cursor1 = accessDB.AccessDB()
    cursor2 = accessDB.AccessDB()
    deli_start = copy.deepcopy(start)
    deli_end = copy.deepcopy(end)
    cursor1.execute("""
              select a.Workno, g.GoodNo, i.GoodNo as 'RawMaterialNo', g.GoodCd, i.GoodCd as 'RawMaterialCd',
            a.OrderQty, a.DeliveryDate, 
            --case when i.Class3 = '061038' then '단조' else 'HEX' end as Gubun,
            case when m3.minorNm = 'Forging' then 0
			when m3.minorNm = 'Hex Bar' then 1
			when m3.minorNm = 'Round Bar' then 2
			when m3.MinorNm = 'Square Bar' then 3
			when m3.MinorNm = 'VALVE 선작업' then 4 end as RawMaterialGubun,
            --    소재사이즈
            ISNULL(i.Size, 0) as RawMaterialSize,
            --    LOK FITTING 유무
            case when g.Class3 = '061001' then 'Y' else 'N' end as LOKFITTINGYN,
            --    LOK FITTING  일때 반제품 품번 사이즈에 따른 기계배정
            case when g.Class3 = '061001' and ((LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),3) = '-1-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),3) = '-2-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),3) = '-3-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),4) = '-2M-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),4) = '-3M-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),4) = '-4M-')) then 'Y' else 'N' end as LOKFITTINGSIZEYN
     from TWorkreport_Han_Eng a
     inner join TGood g on a.Goodcd = g.GoodCd
     inner join TGood i on a.Raw_Materialcd = i.GoodCd
     left outer join TMinor m3 on i.Class3 = m3.MinorCd
     left outer join TMinor m4 on g.Class4 = m4.MinorCd
     where DeliveryDate between """ + deli_start + """ and """ + deli_end + """
       and PmsYn = 'N'
       and ContractYn = '1'
       --    단조    Hex Bar    Round Bar    Square Bar    VALVE 선작업
       and i.Class3 in ('061038', '061039', '061040', '061048', '061126')
     order by i.Class3, i.GoodNo, i.Size

        """)
    row = cursor1.fetchone()
    while row:
        workno = row[0]
        GoodNo = row[1]
        rawMaterialNo = row[2]
        rawMaterialCd = row[4]
        due_date = row[6]

        due_date_seconds = time.mktime(
            (int(due_date[0:4]), int(due_date[4:6]), int(due_date[6:8]), 12, 0, 0, 0, 0, 0))  # 정오 기준
        due_date_seconds = int(due_date_seconds)
        GoodCd = row[3]
        cycle_time = []
        rawMaterialSize = float(row[8])
        no_cycle_time = []
        '''try:
            spec = float((row[8].split('-'))[0])  # 숫자(-문자) 형식 아닌 spec이 나오면 무시
        except ValueError:
            row = cursor1.fetchone()
            continue 
        '''
        Qty = row[5]
        Gubun = row[7]

        if row[9] == 'Y':
            LOKFITTING = 1
        elif row[9] == 'N':
            LOKFITTING = 0

        if row[10] == 'Y':
            LOKFITTINGSIZE = 1
        elif row[10] == 'N':
            LOKFITTINGSIZE = 0

        search_cycle_time(cursor2, cycle_time, GoodCd)

        if sum(cycle_time) * Qty > 60 * 60 * 24 * 4 or sum(cycle_time) == 0: #CNC 공정 만으로 4일 이상 걸리는 작업, 사이클 타임 0 인 작업 제외
            row = cursor1.fetchone()
            no_cycle_time.append(GoodCd)
            continue

        newJob = Job(workno=workno, goodNo=GoodNo, goodCd = GoodCd, time=cycle_time, type=Gubun, quantity=Qty,
                            due=due_date_seconds, rawNo = rawMaterialNo, rawCd = rawMaterialCd,
                     size=rawMaterialSize, LOKFITTING = LOKFITTING, LOKFITTINGSIZE = LOKFITTINGSIZE)

        job_pool.append(newJob)
        row = cursor1.fetchone()

    total_number = len(job_pool)
    print("the total # of jobs: %d"%(total_number))
    return total_number, no_cycle_time


def search_cycle_time(cursor, cycle_time, GoodCd):

    flag1 = 0
    flag2 = 0
    flag3 = 0
    '''
    if Gubun == 1:
        flag3 = 1
    else:  # Gubun == 0: # Gubun = 0 이면 3차 가공까지
        flag3 = 0
        
    '''
    cursor.execute("""select  TWRC.Goodcd, TWRC.Workno, TWRC.Cnc,TWRC.Seq, TWRC.Processcd, TWRC.Prodqty, TWRC.Errqty,  
        TWRC.Cycletime, max(TWRC.Workdate) as workdate, TWRC.Starttime, TWRC.Endtime
        from 
        (select Workno, Workdate, Acceptno, DeliveryDate , Goodcd, OrderQty
        from TWorkreport_Han_Eng 
        where Goodcd = """ + GoodCd + """  ) a
        inner join TWorkReport_CNC TWRC on  TWRC.Goodcd = a.Goodcd
        group by TWRC.Goodcd, TWRC.Workno, TWRC.Cnc,TWRC.Seq, TWRC.Processcd, TWRC.Prodqty, TWRC.Errqty,
        TWRC.Cycletime, TWRC.Workdate, TWRC.Starttime, TWRC.Endtime  
        order by  TWRC.workdate DESC --TWHE.Starttime """
                   )
    row = cursor.fetchone()

    while row:

        processcd = row[4].strip()
        if processcd == 'P1' and flag1 == 0:
            cycle_time.append(int(row[7]))
            flag1 = 1
        elif processcd == 'P2' and flag2 == 0:
            cycle_time.append(int(row[7]))
            flag2 = 1
        elif processcd == 'P3' and flag3 == 0:
            cycle_time.append(int(row[7]))
            flag3 = 1

        if flag1 == 1 and flag2 == 1 and flag3 == 1:
            break

        row = cursor.fetchone()

    try:
        cycle_time.remove(0)
    except Exception:
        pass



def schedule(CNCs, job_pool, machines):
    total_delayed_time = 0
    total_delayed_jobs_count = 0
    last_job_execution = 0
    unAssigned = []
    '''for cnc in CNCs:
        machines[cnc.getNumber()] = list()'''

    avg_time = sum(list(job.getTime() for job in job_pool)) / len(job_pool)

    normPool = list()
    hexPool = list()
    splitPool(job_pool, normPool, hexPool)
    # normPool.sort(key=lambda x: x.getDue())
    # hexPool.sort(key=lambda x: x.getDue())
    normPool = permutation(normPool)
    hexPool = permutation(hexPool)
    # normPool = permutations(normPool,len(normPool))
    # hexPool = permutations(hexPool,len(hexPool))
    normCNCs = list(filter(lambda x: x.getShape() == 0, CNCs))
    hexCNCs = list(filter(lambda x: x.getShape() == 1, CNCs))
    # sortedNormPool = sorted(normPool, key = lambda j : j.getDue())
    # sortedHexPool = sorted(hexPool, key = lambda j: j.getDue())
    standard = input("schedule starts on : ")
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    standard = int(standard)
    print("----standard----")
    print(standard)
    print("----standard----")
    for i, j in enumerate(normPool):

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
        # cnc.enQ(j, in_progress=in_progress)
        (machines[cnc.getNumber()]).append(j)
        j.assignedTo(cnc)
        # ready_pool.appendleft(j)
        # job_pool.remove(j)
        notice = "a new job(" + str(j.getGoodNum()) + ") asggined to CNC #(" + \
                 str(cnc.getNumber()) + ")!\n"

        time_left_of_cnc = sum([j.getTime() for j in machines[cnc.getNumber()]])
        if last_job_execution < time_left_of_cnc:
            last_job_execution = time_left_of_cnc

        diff = j.getDue() - (time_left_of_cnc + j.getTime() + standard)
        print('----------')
        print(j.getDue())
        if diff < 0:
            notice += "(" + str((-1) * diff) + "more time units needed to meet duetime)\n"
            total_delayed_jobs_count += 1
            total_delayed_time += (-1) * diff
        j.setMsg(notice)

    for i, j in enumerate(hexPool):
        selected_CNCs = []
        for c in hexCNCs:
            if (c.getGround() <= j.getSize() <= c.getCeiling()):  # size 맞는 CNC는 모두 찾음
                selected_CNCs.append(c)

        timeLefts = [sum([j.getTime() for j in machines[c.getNumber()]]) for c in selected_CNCs]
        minValue = min(timeLefts)
        minIndex = timeLefts.index(minValue)
        cnc = selected_CNCs[minIndex]
        # cnc.enQ(j, in_progress=in_progress)
        (machines[cnc.getNumber()]).append(j)
        j.assignedTo(cnc)
        # ready_pool.appendleft(j)
        # job_pool.remove(j)
        notice = "a new job(" + str(j.getGoodNum()) + ") asggined to CNC #(" + \
                 str(cnc.getNumber()) + ")!\n"

        time_left_of_cnc = sum([j.getTime() for j in machines[cnc.getNumber()]])
        if last_job_execution < time_left_of_cnc:
            last_job_execution = time_left_of_cnc

        diff = j.getDue() - (time_left_of_cnc + j.getTime() + standard)
        print('----------')
        print(j.getDue())
        if diff < 0:
            notice += "(" + str((-1) * diff) + "more time units needed to meet duetime)\n"
            total_delayed_jobs_count += 1
            total_delayed_time += (-1) * diff
        j.setMsg(notice)

    msg = [total_delayed_time, total_delayed_jobs_count, last_job_execution, machines]
    return msg

'''
def assign(CNCs, job_pool, ready_pool, in_progress):  # CNC에 job들을 분배하는 함수

    total_delayed_time = 0
    total_delayed_jobs_count = 0
    last_job_execution = 0
    avg_time = sum(list(job.getTime() for job in job_pool)) / len(job_pool)

    normPool = []
    hexPool = []
    splitPool(job_pool, normPool, hexPool)
    normPool.sort(key=lambda x: x.getDue())
    hexPool.sort(key=lambda x: x.getDue())
    # normPool = permutations(normPool,len(normPool))
    # hexPool = permutations(hexPool,len(hexPool))
    normCNCs = list(filter(lambda x: x.getShape() == 0, CNCs))
    hexCNCs = list(filter(lambda x: x.getShape() == 1, CNCs))
    # sortedNormPool = sorted(normPool, key = lambda j : j.getDue())
    # sortedHexPool = sorted(hexPool, key = lambda j: j.getDue())

    for i, j in enumerate(normPool):

        selected_CNCs = []

        for c in normCNCs:
            if (float(c.getGround()) <= float(j.getSize()) < float(c.getCeiling())):  # size 맞는 CNC는 모두 찾음
                selected_CNCs.append(c)

        timeLefts = [c.get_timeLeft() for c in selected_CNCs]
        minValue = min(timeLefts)
        minIndex = timeLefts.index(minValue)
        cnc = selected_CNCs[minIndex]
        cnc.enQ(j, in_progress=in_progress)
        j.assignedTo(cnc)
        ready_pool.appendleft(j)
        job_pool.remove(j)
        notice = "a new job(" + str(j.getGoodNum()) + ") asggined to CNC #(" + \
                 str(cnc.getNumber()) + ")!\n"

        if last_job_execution < cnc.get_timeLeft():
            last_job_execution = cnc.get_timeLeft()
        diff = cnc.on_time(j)
        if diff < 0:
            notice += "(" + str((-1) * diff) + "more time units needed to meet duetime)\n"
            total_delayed_jobs_count += 1
            total_delayed_time += (-1) * diff
        j.setMsg(notice)

    for i, j in enumerate(hexPool):
        selected_CNCs = []
        for c in hexCNCs:
            if (float(c.getGround()) <= float(j.getSize()) < float(c.getCeiling())):  # size 맞는 CNC는 모두 찾음
                selected_CNCs.append(c)

        timeLefts = [c.get_timeLeft() for c in selected_CNCs]
        minValue = min(timeLefts)
        minIndex = timeLefts.index(minValue)
        cnc = selected_CNCs[minIndex]
        cnc.enQ(j, in_progress=in_progress)
        ready_pool.appendleft(j)
        job_pool.remove(j)
        notice = "a new job(" + str(j.getGoodNum()) + ") asggined to CNC #(" + \
                 str(cnc.getNumber()) + ")!\n"

        if last_job_execution < cnc.get_timeLeft():
            last_job_execution = cnc.get_timeLeft()
        diff = cnc.on_time(j)
        if diff < 0:
            notice += "(" + str((-1) * diff) + "more time units needed to meet duetime)\n"
            total_delayed_jobs_count += 1
            total_delayed_time += (-1) * diff
        j.setMsg(notice)

    msg = [total_delayed_time, total_delayed_jobs_count, last_job_execution]
    return msg
'''


def update(CNCs, unitTime, ready_pool, in_progress):
    for c in CNCs:
        try:
            job = c.get_jobQ()[-1]
        except IndexError as e:
            # print(e)
            continue
        for i in range(len(job.getSeries())):
            component = job.getComponent(i)
            if not component.ifDone():  # 3개의 콤포넌트 중 아W직 안끝난 것이 나오면
                component.spendTime(unitTime)  # 주어진 unitTime만큼 뺌
                break
            if (i == len(job.getSeries()) - 1):  ##마지막 콤포넌트까지 모두 done이면
                if (job.ifAllDone()):  # job의 함수를 통해 한번더 검사하고
                    c.deQ()  # job을 jobQ에서 뺀다.
                    in_progress.appendleft((c.get_jobQ())[-1])  # inprogress에 넣고
                    ready_pool.remove((c.get_jobQ())[-1])  # reaypool에서는 뺀다


def splitPool(job_pool, norm, hex, round, square, valve_pre):
    for i, assignment in enumerate(job_pool):
        if assignment.getType() == 0:
            norm.append(assignment)

        elif assignment.getType() == 1:
            hex.append(assignment)

        elif assignment.getType() == 2:
            round.append(assignment)

        elif assignment.getType() == 3:
            square.append(assignment)

        elif assignment.getType() == 4:
            valve_pre.append(assignment)

    return 0


def permutation(pool):
    per = list()
    while (len(pool) != 0):
        i = random.randrange(0, len(pool))
        newElement = pool.pop(i)
        per.append(newElement)
    return per


def sort(pool):
    sorted(pool, key=lambda unit: unit.get_job().getDue())

