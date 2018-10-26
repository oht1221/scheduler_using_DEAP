import xlwt
import datetime

def print_job_schedule(assignment, start, end, standard, total_number, total_number_unassgiend, schedule_type, endsAt, numDelayed, no_cycle_time, mu, Lambda, cx, mut, rank = 0):
    output = xlwt.Workbook(encoding='utf-8')  # utf-8 인코딩 방식의 workbook 생성
    output.default_style.font.height = 20 * 11  # (11pt) 기본폰트설정 다양한건 찾아보길
    assigned = assignment

    modified = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    color = modified

    worksheet = output.add_sheet("비고")
    worksheet.col(0).width = 400 * 15
    worksheet.col(1).width = 400 * 15
    worksheet.col(2).width = 400 * 15
    worksheet.col(3).width = 400 * 15
    worksheet.col(4).width = 400 * 15
    worksheet.col(5).width = 400 * 15
    worksheet.col(6).width = 400 * 15
    worksheet.col(7).width = 400 * 15

    worksheet.write(0, 0, "기준 시간")
    worksheet.write(0, 1, standard)


    worksheet.write(1, 0, "date_from")
    worksheet.write(1, 1, start)


    worksheet.write(2, 0, "date_until")
    worksheet.write(2, 1, end)

    worksheet.write(3, 0, "총 작업 수 ")
    worksheet.write(3, 1, total_number)

    worksheet.write(4, 0, "배정되지 않은 작업")
    for i in range(len(total_number_unassgiend)):
        worksheet.write(4, 1 + i, total_number_unassgiend[i].getWorkno())

    endsAt = datetime.datetime.fromtimestamp(endsAt).strftime('%Y-%m-%d %H:%M:%S')
    worksheet.write(5, 0, "종료 시간")
    worksheet.write(5, 1, endsAt)

    worksheet.write(6, 0, "납기 불충족 작업 수")
    worksheet.write(6, 1, numDelayed)

    worksheet.write(7, 0, "cycle time 정보 부족")
    for i in range(len(no_cycle_time)):
        worksheet.write(7, 1 + i, no_cycle_time[i])
        worksheet.col(i + 1).width = 400 * 15

    for key, machine in assigned.items():
        row = 0
        worksheet = output.add_sheet(str(key))  # 시트 생성
        worksheet.write(row, 0, "작업지시서 번호")
        worksheet.col(0).width = 256 * 15
        worksheet.write(row, 1, "공정")
        worksheet.col(1).width = 256 * 5
        worksheet.write(row, 2, "품번")
        worksheet.col(2).width = 256 * 20
        worksheet.write(row, 3, "구분")
        worksheet.col(3).width = 256 * 15
        worksheet.write(row, 4, "LOK")
        worksheet.col(4).width = 256 * 5
        worksheet.write(row, 5, "시작")
        worksheet.col(5).width = 256 * 24
        worksheet.write(row, 6, "종료")
        worksheet.col(6).width = 256 * 24
        worksheet.write(row, 7, "납기")
        worksheet.col(7).width = 256 * 24
        worksheet.write(row, 8, "Qty")
        worksheet.col(8).width = 256 * 24
        #worksheet.write(row, 5, str(indexOfMin))
        row += 1
        for comp in machine.getAssignments():
            print_out_unit(comp, row, worksheet, color)
            row += 1

    output.save("./schedules/schedule_%s_%s_%s_%s_%d_%d_%f_%f_%d.xls" % (schedule_type, start, end, standard, mu, Lambda, cx, mut, rank))

    return

def print_out_unit(comp, row, worksheet, color):
    startTime = datetime.datetime.fromtimestamp(comp.getStartDateTime()).strftime('%Y-%m-%d %H:%M:%S')
    endTime = datetime.datetime.fromtimestamp(comp.getEndDateTime()).strftime('%Y-%m-%d %H:%M:%S')

    if comp.isSetting():
        worksheet.write(row, 0, "Setting Time")
        worksheet.write(row, 5, startTime)
        worksheet.write(row, 6, endTime)

    else:
        job = comp.getJob()
        due = datetime.datetime.fromtimestamp(job.getDue()).strftime('%Y-%m-%d %H:%M:%S')
        quantity = job.getQuantity()

        if comp.isDelayed():
            worksheet.write(row, 0, job.getWorkno(), color)
        else:
            worksheet.write(row, 0, job.getWorkno())

        worksheet.write(row, 1, "P%d" % comp.getProcessCd())
        worksheet.write(row, 2, job.getGoodCd())
        worksheet.write(row, 3, job.getType())
        worksheet.write(row, 4, job.getLokFittingSize())
        worksheet.write(row, 5, startTime)
        worksheet.write(row, 6, endTime)
        worksheet.write(row, 7, due)
        worksheet.write(row, 8, quantity)