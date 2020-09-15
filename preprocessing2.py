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

def dbConnectionCheck():

    while (1):
        try:
            database = "hansun" #input("database name : ")
            username = "Han_Eng_Back"#input("user name : ")
            password = "HseAdmin1991"#input("password : ")
            cursor_test = accessDB.AccessDB(database, username, password)

        except Exception as e:

            print(e)
            print("데이터베이스 접속 실패! 로그인 정보를 다시 입력해주세요.")

        else:
            cursor_test.close()
            print("데이터베이스 접속 성공! ")
            break
    return database, username, password

def dbConnectionCheck_Deployment(database, username, password):


    try:
        cursor_test = accessDB.AccessDB(database, username, password)

    except Exception as e:
        print(e)
        print("데이터베이스 접속 실패! 로그인 정보를 다시 입력해주세요.")

    cursor_test.close()

    return database, username, password

def make_job_pool(job_pool, start, end, database, username, password, cut = 1000000000, partition_size = 1000000000):
    cursor_job = accessDB.AccessDB(database, username, password)
    cursor_cycletime = accessDB.AccessDB(database, username, password)
    deli_start = copy.deepcopy(start)
    deli_end = copy.deepcopy(end)
    no_cycle_time = []
    print("작업 지시서 정보 받아오는 중...")

    cursor_job.execute(""" select a.Workno, g.GoodNo,  g.GoodCd, i.GoodCd as 'RawMaterialCd',
            a.OrderQty , a.DeliveryDate, 
            --case when i.Class3 = '061038' then '단조' else 'HEX' end as Gubun,
            case when m3.minorNm = 'Forging' then 0
			when m3.minorNm = 'Hex Bar' then 1
			when m3.minorNm = 'Round Bar' then 2
			when m3.MinorNm = 'Square Bar' then 3
			when m3.MinorNm = 'VALVE 선작업' then 4 end as RawMaterialGubun,
            --    소재사이즈
            ISNULL(i.Size, 0) as RawMaterialSize,
            --    LOK FITTING 유무
            case when g.Class3 = '061001' then 'Y' else 'N' end as LOKFITTINGYN, --LOK FITTING
            --    LOK FITTING  일때 반제품 품번 사이즈에 따른 기계배정
            case when g.Class3 = '061001' and ((LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),3) = '-1-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),3) = '-2-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),3) = '-3-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),4) = '-2M-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),4) = '-3M-') or
                                               (LEFT(REPLACE(g.GoodNo, RTRIM(m4.MinorNm),''),4) = '-4M-')) then 'Y' else 'N' end as LOKFITTINGSIZEYN, a.CloseDate, a.Credate, a.Moddate
     from TWorkreport_Han_Eng a
     inner join TGood g on a.Goodcd = g.GoodCd
     inner join TGood i on a.Raw_Materialcd = i.GoodCd
     left outer join TMinor m3 on i.Class3 = m3.MinorCd
     left outer join TMinor m4 on g.Class4 = m4.MinorCd

     where DeliveryDate between '20180711' and '20180718'
        and PmsYn = 'N'
        and ContractYn = '1' 

       --    단조    Hex Bar    Round Bar    Square Bar    VALVE 선작업
       and i.Class3 in ('061038', '061039', '061040', '061048', '061126')
	   --and ( tc.Processcd = 'P1' or tc.Processcd = 'P2' or tc.Processcd = 'P3')
	 order by DeliveryDate""")
    row = cursor_job.fetchone()

    while row:
        workno = row[0]
        GoodNo = (row[1]).replace(" ", "")
        GoodCd = row[3]
        Gubun = row[7]
        rawMaterialNo = row[2]
        rawMaterialCd = row[4]
        due_date = row[6]
        due_date_seconds = time.mktime(
            (int(due_date[0:4]), int(due_date[4:6]), int(due_date[6:8]), 10, 0, 0, 0, 0, 0))  # 오후4시 기준
        due_date_seconds = int(due_date_seconds)
        Qty = row[5]
        if Qty > 5000: continue

        rawMaterialSize = float(row[8])

        cycle_time = search_cycle_time(cursor_cycletime, GoodCd)
        '''sum(cycle_time) * Qty > 60 * 60 * 24 * 4 or '''

        if len(cycle_time) == 0:
            no_cycle_time.append([workno, GoodCd, GoodNo])
            if Gubun == 0 or Gubun == 3 or Gubun == 4:
                cycle_time = [150, 150, 150]
            elif Gubun == 1 or Gubun == 2:
                cycle_time = [150, 150]



        '''try:
            spec = float((row[8].split('-'))[0])  # 숫자(-문자) 형식 아닌 spec이 나오면 무시
        except ValueError:
            row = cursor1.fetchone()
            continue 
        '''

        LOKFITTING = 0
        if row[9] == 'Y':  #LOK인지 아닌지 구분
            LOKFITTING = 1

        LOKFITTINGSIZE = 0
        if row[10] == 'Y':  #LOK중에서 1,2,3, 2m,3m,4m인지 확인
            LOKFITTINGSIZE = 1

        if Qty > cut:
            while Qty > 0:
                if Qty < cut:
                    qty_part = Qty
                else:
                    qty_part = min(partition_size, Qty)
                Qty -= qty_part
                newJob = Job(workno=workno, goodNo=GoodNo, goodCd=GoodCd, time=cycle_time, type=Gubun, quantity=qty_part,
                             due=due_date_seconds, rawNo=rawMaterialNo, rawCd=rawMaterialCd,
                             size=rawMaterialSize, LOKFITTING=LOKFITTING, LOKFITTINGSIZE=LOKFITTINGSIZE, seperation=True)
                job_pool.append(newJob)

        else:
            newJob = Job(workno=workno, goodNo=GoodNo, goodCd=GoodCd, time=cycle_time, type=Gubun, quantity=Qty,
                     due=due_date_seconds, rawNo=rawMaterialNo, rawCd=rawMaterialCd,
                     size=rawMaterialSize, LOKFITTING=LOKFITTING, LOKFITTINGSIZE=LOKFITTINGSIZE)
            job_pool.append(newJob)

        row = cursor_job.fetchone()

    total_number = len(job_pool)
    print("the total # of jobs: %d"%(total_number))
    print("the total # of no cycle time : %d"%len(no_cycle_time))
    print("---------------------------------------------------------")
    for n in no_cycle_time:
        print(n[0], n[1], n[2])

    print("---------------------------------------------------------")
    return total_number, no_cycle_time


def search_cycle_time(cursor, GoodCd):

    flag1 = 0
    flag2 = 0
    flag3 = 0
    '''
    if Gubun == 1:
        flag3 = 1
    else:  # Gubun == 0: # Gubun = 0 이면 3차 가공까지
        flag3 = 0
        
    '''
    cycle_time = []
    cursor.execute("""select  g.GoodNo, TWRC.Goodcd, TWRC.Workno, TWRC.Processcd, TWRC.Cycletime, TWRC.Workdate
    from TWorkreport_CNC TWRC 
	    inner join TGood g on g.GoodCd = TWRC.Goodcd
    where g.GoodCd = """ + GoodCd + """ and (TWRC.Processcd = 'P1' or TWRC.Processcd = 'P2' or TWRC.Processcd = 'P3' )
    order by TWRC.Workdate DESC""")

    row = cursor.fetchone()

    while row:

        processcd = row[3].strip()
        if processcd == 'P1':
            if int(row[4]) != 0 and flag1 == 0:
                cycle_time.append(int(row[4]))
                flag1 = 1
        elif processcd == 'P2':
            if int(row[4]) != 0 and flag2 == 0:
                cycle_time.append(int(row[4]))
                flag2 = 1
        elif processcd == 'P3':
            if int(row[4]) != 0 and flag3 == 0:
                cycle_time.append(int(row[4]))
                flag3 = 1

        if flag1 == 1 and flag2 == 1 and flag3 == 1:
            break

        row = cursor.fetchone()

    try:
        i = 1
        while(1):
            cycle_time.remove(0)
            print("%s includes zero cycle time #%d!\n"%GoodCd, i)
            i+=1
    except Exception:
        pass
    return cycle_time

def getLeftOver(database, username, password):
    initial_times = dict()
    cursor = accessDB.AccessDB(database, username, password)
    cursor.execute(
    """
    SET NOCOUNT ON;
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
	    [Moddate] [smalldatetime] NULL
    ) 

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


    select m.MinorNm as [장비명], a.Workno, a.Processcd, w.OrderQty as [작업지시수량], ISNULL(b.Prodqty,0) + ISNULL(b.Errqty,0) as [작업수량], ISNULL(c.Cycletime,0) as [C/T]
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
    order by m.SortSeq
     """)

    row = cursor.fetchone()

    i = 1
    while (row):
        cncNo = row[0]
        try:
            cncNo = int((cncNo.split())[0])  # 숫자(-문자) 형식 아닌 spec이 나오면 무시
            if cncNo == [14, 26, 27, 28, 29, 30, 31]:  # 후가공 CNC
                row = cursor.fetchone()
                continue
        except ValueError:
            row = cursor.fetchone()
            continue

        orderQty = row[3]
        producedQty = row[4]
        cycleTime = row[5]
        leftQty = max(0, orderQty - producedQty)
        leftover = int(leftQty * cycleTime)
        initial_times[cncNo] = leftover
        '''
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
            print("CNC %d은 후가공 전용 " %(cncNo))
            continue
        '''
        row = cursor.fetchone()
    cursor.close()

    return initial_times

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

