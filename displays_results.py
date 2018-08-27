import xlwt
import datetime

def print_job_schedule(indiv, start, end, standard, schedule_type, rank = 0):
    output = xlwt.Workbook(encoding='utf-8')  # utf-8 인코딩 방식의 workbook 생성
    output.default_style.font.height = 20 * 11  # (11pt) 기본폰트설정 다양한건 찾아보길
    assignment = indiv.assignment
    modified = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    color = modified
    worksheet = output.add_sheet("비고")
    worksheet.write(0, 0, "기준 시간")
    worksheet.write(0, 1, standard)
    worksheet.col(0).width = 256 * 15
    worksheet.write(1, 0, "date_from")
    worksheet.write(1, 1, start)
    worksheet.col(1).width = 256 * 15
    worksheet.write(2, 0, "date_until")
    worksheet.write(2, 1, end)
    worksheet.col(2).width = 256 * 15
    for key, value in assignment.items():
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
        for i, unit in enumerate(value):
            times = unit.get_times()
            job = unit.get_job()
            due = unit.job.getDue()
            #type = unit.job.getType()
            quantity = unit.job.getQuantity()
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
                worksheet.write(row, 2, job.getGoodNo())
                worksheet.write(row, 3, job.getType())
                worksheet.write(row, 4, job.getLOK())
                worksheet.write(row, 5, job_starts_from)
                worksheet.write(row, 6, job_ends_at)
                worksheet.write(row, 7, datetime.datetime.fromtimestamp(due).strftime('%Y-%m-%d %H:%M:%S'))
                worksheet.write(row, 8, quantity)
                row += 1
    output.save("./schedules/schedule_%s_%s_%s_%s_%d.xls"%(schedule_type, start, end, standard, rank))  # 엑셀 파일 저장 및 생성

    return