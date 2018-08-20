import xlrd
import job
input = '.\schedules\schedule_greedy_20180601_20180615_20180528_0.xls'
machines = {}
def read_from_excel(input, machine = None):
    workbook = xlrd.open_workbook(input)
    CNC_number = float(1)
    worksheets = workbook.sheets()
    for i, sheet in enumerate(worksheets):
        #n_cols = sheet.ncols
        n_rows = sheet.nrows
        prev_workno = 0
        machines[i+1]
        for j in range(1, n_rows):
            row = sheet.row_values(j)
            workno = row[0]
            if prev_workno == workno:
                continue
            prev_workno = workno
            Goodcd = row[2]
            start = row[3]
            end = row[4]
            due = row[5]
            quantity = row[6]
            new = job(workno, Goodcd, quantity = quantity)

read_from_excel(input)






'''
def make_job_pool(job_pool, start, end):
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
        if sum(cycle_time) * Qty > 60 * 60 * 24 * 3 or sum(cycle_time) == 0: #CNC 공정 만으로 4일 이상 걸리는 작업, 사이클 타임 0 인 작업 제외
            row = cursor1.fetchone()
            continue
        newJob = Job(workno=workno, workdate=workdate, good_num=GoodCd, time=cycle_time, type=Gubun, quantity=Qty,
                     due=due_date_seconds, size=spec)
        job_pool.append(newJob)
        row = cursor1.fetchone()

    total_number = len(job_pool)
    print("the total # of job : %d" % (total_number))

    return total_number
'''

'''
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

'''
'''
def print_job_schedule(indiv, start, end, standard, schedule_type, rank = 0):
    output = xlwt.Workbook(encoding='utf-8')  # utf-8 인코딩 방식의 workbook 생성
    output.default_style.font.height = 20 * 11  # (11pt) 기본폰트설정 다양한건 찾아보길
    assignment = indiv.assignment
    modified = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    color = modified
    for key, value in assignment.items():
        row = 0
        worksheet = output.add_sheet(str(key))  # 시트 생성
        worksheet.write(row, 0, "작업지시서 번호")
        worksheet.col(0).width = 256 * 15
        worksheet.write(row, 1, "공정")
        worksheet.col(1).width = 256 * 5
        worksheet.write(row, 2, "품번")
        worksheet.col(2).width = 256 * 15
        worksheet.write(row, 3, "시작")
        worksheet.col(3).width = 256 * 24
        worksheet.write(row, 4, "종료")
        worksheet.col(4).width = 256 * 24
        worksheet.write(row, 5, "납기")
        worksheet.col(5).width = 256 * 24
        #worksheet.write(row, 5, str(indexOfMin))
        row += 1
        for i, unit in enumerate(value):
            times = unit.get_times()
            job = unit.get_job()
            due = unit.job.getDue()
            type = unit.job.getType()
            for j, time in enumerate(times):
                job_starts_from = time[0]
                job_ends_at = time[1]
                #start = comp.getStartDateTime()
                #end = comp.getEndDateTime()
                if unit.isDelayed():
                    worksheet.write(row, 0, job.getWorkno(), color)
                else:
                    worksheet.write(row, 0, job.getWorkno())
                worksheet.write(row, 1, "P%d" % (j + 1))
                worksheet.write(row, 2, job.getGoodNum())
                worksheet.write(row, 3, job_starts_from)
                worksheet.write(row, 4, job_ends_at)
                worksheet.write(row, 5, datetime.datetime.fromtimestamp(due).strftime('%Y-%m-%d %H:%M:%S'))
                worksheet.write(row, 6, type)
                row += 1
    output.save("./schedules/schedule_%s_%s_%s_%s_%d.xls"%(schedule_type, start, end, standard, rank))  # 엑셀 파일 저장 및 생성

    return
'''