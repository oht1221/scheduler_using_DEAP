import xlwt

def print_job_schedule(indiv, start, end, standard):
    output = xlwt.Workbook(encoding='utf-8')  # utf-8 인코딩 방식의 workbook 생성
    output.default_style.font.height = 20 * 11  # (11pt) 기본폰트설정 다양한건 찾아보길
    font_style = xlwt.easyxf('font: height 280, bold 1;')  # 폰트 스타일 생성

    schedule = indiv.assignment
    for key, value in schedule.items():
        row = 0
        worksheet = output.add_sheet(str(key))  # 시트 생성
        worksheet.write(row, 0, "작업지시서 번호")
        worksheet.write(row, 1, "공정")
        worksheet.write(row, 2, "품번")
        worksheet.write(row, 3, "시작")
        worksheet.write(row, 4, "종료")
        #worksheet.write(row, 5, str(indexOfMin))
        row += 1
        for i, unit in enumerate(value):
            times = unit.get_times()
            job = unit.get_job()
            for j, time in enumerate(times):
                job_starts_from = time[0]
                job_ends_at = time[1]
                #start = comp.getStartDateTime()
                #end = comp.getEndDateTime()
                worksheet.write(row, 0, job.getWorkno())
                worksheet.write(row, 1, "P%d" % (j + 1))
                worksheet.write(row, 2, job.getGoodNum())
                worksheet.write(row, 3, job_starts_from)
                worksheet.write(row, 4, job_ends_at)
                row += 1
    output.save("./schedules/schedule_greedy_%s_%s_%s.xls"%(start, end, standard))  # 엑셀 파일 저장 및 생성
    return