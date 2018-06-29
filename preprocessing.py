from cnc import *
from job import *
import xlrd
import random
import numpy as np
import accessDB
from itertools import permutations
import time


def read_CNCs(input, CNCs):
    workbook = xlrd.open_workbook(input)

    worksheet = workbook.sheet_by_name('기계정보')

    n_cols = worksheet.ncols
    n_rows = worksheet.nrows

    for i in range(2, 41):  # 1, 2, 6, 8, 10, 16, 22번 cnc
        row = worksheet.row_values(i)
        number = float(row[1])
        shape = None
        if str(row[2]) == "2JAW":  # 2JAW 면 shape이 0, 3JAW면 shape이 1
            shape = 0
        elif str(row[2]) == "3JAW":
            shape = 1
        type = str(row[3])
        size = str(row[4])

        if (size.find('~') == -1):
            continue  # '후가공' cnc는 제외
        ground = size.split('~')[0]
        ground = float(ground[1:])

        try:
            ceiling = float(size.split('~')[1])
        except ValueError:
            ceiling = 100.0
        cnc = CNC(number, ground, ceiling, shape, type)
        CNCs.append(cnc)


def initial_assignment(machines):
    cursor = accessDB.AccessDB()
    cursor.execute("""
    declare @THse_CNC_Work_List table (
        [Accunit] [char](3) NULL,
    	[Factory] [char](3) NULL,
  	    [Cnc] [char](6) NULL,
    	[Workdate] [char](8) NULL,
	    [Seq] [char](4) NULL,
	    [Workno] [varchar](20) NULL,
	    [Goodcd] [varchar](8) NULL,
	    [Processcd] [char](2) NULL,
	    [Prodqty] [numeric](18, 0) NULL,
	    [Errqty] [numeric](18, 0) NULL,
	    [Crepno] [char](5) NULL,
	    [Credate] [smalldatetime] NULL,
	    [Modpno] [char](5) NULL,
	    [Moddate] [smalldatetime] NULL)

    insert @THse_CNC_Work_List
    select a.Accunit, a.Factory, a.Cnc, a.Workdate, a.Seq, a.Workno, w.Goodcd, a.Processcd,
           a.Prodqty, a.Errqty, a.Crepno, a.Credate, a.Modpno, a.Moddate
    from THse_Cnc_Machine_Assignment a
    left outer join ( select a.Cnc, a.Workdate, MAX(b.Seq) as Seq
                      from
                      (
                          select a.Cnc, MAX(a.Workdate) as Workdate
                          from THse_Cnc_Machine_Assignment a
                          group by a.Cnc
                      ) a 
                      left outer join THse_Cnc_Machine_Assignment b on a.Cnc = b.Cnc and a.Workdate = b.Workdate
                      group by a.Cnc, a.Workdate ) b on a.Cnc = b.Cnc and a.Workdate = b.Workdate and a.Seq = b.Seq
    left outer join TWorkreport_Han_Eng w on a.Workno = w.Workno
    where b.Cnc is not null
    order by a.Cnc

    select m.MinorNm as [장비명], a.Workno, a.Processcd, w.OrderQty as [작업지시수량], ISNULL(b.Prodqty,0) + ISNULL(b.Errqty,0) as [작업수량], ISNULL(c.Cycletime,0) as [C/T],
        w.DeliveryDate, w.Goodcd,a.Workdate
    from @THse_CNC_Work_List a
    left outer join (    select a.Workno, a.Processcd, SUM(a.Prodqty) as Prodqty, SUM(a.Errqty) as Errqty
                         from TWorkReport_CNC a, @THse_CNC_Work_List b
                         where a.Workdate > '20170101' and a.Workno = b.Workno and a.Processcd = b.Processcd
                         group by a.Workno, a.Processcd    ) b on a.Workno = b.Workno and a.Processcd = b.Processcd
    left outer join (    select ROW_NUMBER() over (partition by a.Goodcd, a.Processcd order by a.Workdate, a.Gubun desc) as _Rank,
                                a.Goodcd, a.Processcd, a.Cycletime
                         from TWorkReport_CNC a, @THse_CNC_Work_List b
                         where a.Goodcd = b.Goodcd ) c on a.Goodcd = c.Goodcd and a.Processcd = c.Processcd and c._Rank = 1
    left outer join TMinor m on a.Cnc = m.MinorCd and m.MinorCd like '293%'
    left outer join TWorkreport_Han_Eng w on a.Workno = w.Workno
    order by m.SortSeq """)

    row = cursor.fetchone()
    while (row):
        cncNo = row[0]
        try:
            cncNo = float((cncNo.split())[0])  # 숫자(-문자) 형식 아닌 spec이 나오면 무시
        except ValueError:
            row = cursor.fetchone()
            continue
        workNo = row[1]
        processcd = row[2].strip()
        orderQty = row[3]
        producedQty = row[4]
        cycleTime = row[5]
        Qty = orderQty - producedQty
        cycle_time = [0, 0, 0]
        if processcd == 'P1':
            cycle_time[0] = int(cycleTime)
        elif processcd == 'P2':
            cycle_time[1] = int(cycleTime)
        elif processcd == 'P3':
            cycle_time[2] = int(cycleTime)
        goodCd = row[7]
        workdate = row[8]

        due_date = row[6]
        due_date_seconds = time.mktime(
            (int(due_date[0:4]), int(due_date[4:6]), int(due_date[6:8]), 12, 0, 0, 0, 0, 0))  # 정오 기준
        due_date_seconds = int(due_date_seconds)

        newJob = Job(workno=workNo, workdate=workdate, good_num=goodCd, time=cycle_time, quantity=Qty,
                     due=due_date_seconds)
        try:
            (machines[cncNo]).append(newJob)
        except KeyError:
            row = cursor.fetchone()
            print("CNC %d은 후가공 전용 " % (cncNo))
            continue

        row = cursor.fetchone()


def make_job_pool(job_pool):
    cursor1 = accessDB.AccessDB()
    cursor2 = accessDB.AccessDB()
    deli_start = str(input("delivery date from: "))
    deli_end = str(input("delivery date until: "))
    cursor1.execute("""
        select  w.workno, w.workdate, w.DeliveryDate, w.GoodCd,i.GoodCd as raw_materialCd, w.OrderQty,
		case when i.Class3 = '061038' then 0 else 1 end as Gubun,
		REPLACE(REPLACE(i.Spec, 'HEX.', ''),'HEX','') as Spec

	    from TWorkreport_Han_Eng w
	    inner join TGood i on w.Raw_Materialcd = i.GoodCd
	    where w.DeliveryDate between """ + deli_start + """ and """ + deli_end + """
	    and w.PmsYn = 'N'
	    and w.ContractYn = '1'
	    and i.Class2 not in ('060002', '060006')
	    and i.Class3 in ('061038', '061039')
        """)
    row = cursor1.fetchone()
    while row:
        workno = row[0]
        workdate = row[1]
        due_date = row[2]
        due_date_seconds = time.mktime(
            (int(due_date[0:4]), int(due_date[4:6]), int(due_date[6:8]), 12, 0, 0, 0, 0, 0))  # 정오 기준
        due_date_seconds = int(due_date_seconds)
        GoodCd = row[3]
        cycle_time = []
        try:
            spec = float((row[7].split('-'))[0])  # 숫자(-문자) 형식 아닌 spec이 나오면 무시
        except ValueError:
            row = cursor1.fetchone()
            continue
        Qty = row[5]
        Gubun = int(row[6])
        search_cycle_time(cursor2, cycle_time, GoodCd, Gubun, deli_start, deli_end)
        newJob = Job(workno=workno, workdate=workdate, good_num=GoodCd, time=cycle_time, type=Gubun, quantity=Qty,
                     due=due_date_seconds, size=spec)
        job_pool.append(newJob)
        row = cursor1.fetchone()

    total_number = len(job_pool)
    print("the total # of job : %d" % (total_number))

    return total_number


def search_cycle_time(cursor, cycle_time, GoodCd, Gubun, deli_start, deli_end):
    flag1 = 0
    flag2 = 0
    if Gubun == 1:
        flag3 = 1
    else:  # Gubun == 0: # Gubun = 0 이면 3차 가공까지
        flag3 = 0

    cursor.execute("""
                    select  max(c.workdate) as workdate, j.DeliveryDate, j.GoodCd, j.OrderQty,
    		        -- ISNULL(c.Prodqty,0) + ISNULL(c.Errqty,0) as Qty,
    		        case when j.Class3 = '061038' then 0 else 1 end as Gubun,
                    REPLACE(REPLACE(j.Spec, 'HEX.', ''),'HEX','')  as Spec,
    			    c.Processcd, c.Cycletime , c.starttime, c.Endtime

    		        from  TWorkReport_CNC c 
    		        inner join
    				(
    				select  w.workno, /*, max(c.workdate) as workdate*/ w.DeliveryDate, w.GoodCd, w.OrderQty, i.Class3, i.Spec
    				from TWorkreport_Han_Eng w
    				inner join TGood i on w.Raw_Materialcd = i.GoodCd
    				where w.DeliveryDate between """ + deli_start + """ and """ + deli_end + """ 
    				and w.PmsYn = 'N'
    				and w.ContractYn = '1'
    				and i.Class2 not in ('060002', '060006')
    				and i.Class3 in ('061038', '061039')
    				) j 
    				 on c.Goodcd = j.GoodCd
    				 where j.Goodcd = """ + GoodCd + """
                    group by j.Goodcd, c.workdate, j.workno, j.DeliveryDate, j.OrderQty, c.Cycletime, c.Processcd,c.starttime, c.Endtime, j.Class3, Spec

                    order by c.workdate DESC
                    """
                   )
    row = cursor.fetchone()
    while (row):
        processcd = row[6].strip()
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


def splitPool(job_pool, normPool, hexPool):
    for i, assignment in enumerate(job_pool):
        if assignment.getType() == 0:
            normPool.append(assignment)

        elif assignment.getType() == 1:
            hexPool.append(assignment)

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