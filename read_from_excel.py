import xlrd, xlwt
import datetime
import sys
from tkinter import filedialog
from tkinter import *
import time
from evaluation import Machine
from job import *
from accessDB import *
from preprocessing import search_cycle_time
from displays_results import print_out_unit

root = Tk()
indiv = []
work_numbers = []

machines = {}

def inputFile():
    root.filename = filedialog.askopenfilename(initialdir = "./schedules",
                                               title = 'choose your schdule',
                                               filetypes = (('excel files', '*.xlsx'),
                                                            ('excel files', '*.xls'))
                                               )

def inputVariables():
    workno = input_workno.get()
    due = input_due.get()

    due_date_seconds = time.mktime(
        (int(due[0:4]), int(due[4:6]), int(due[6:8]), 12, 0, 0, 0, 0, 0))  # 정오 기준
    due_date_seconds = int(due_date_seconds)

    goodNo = input_goodNo.get()
    goodCd = input_goodCd.get()
    qty = input_qty.get()
    cursor = AccessDB()
    cycle_time = []
    gubun = input_gubun.get()
    search_cycle_time(cursor, cycle_time, goodCd)
    print(sum(cycle_time) * 300  + 60*60*24*4)
    new_job = Job(workno=workno, goodCd=goodCd, type=gubun, quantity=qty, time=cycle_time,
                              due=due_date_seconds)



def read_schedule(input):
    workbook = xlrd.open_workbook(input)
    worksheet = workbook.sheet_by_name('비고')
    row = worksheet.row_values(0)
    standard = row[1]
    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)
    print(standard)

    i = 1
    worksheet = workbook.sheet_by_index(i)

    while worksheet is not None:
        M = Machine()
        machines[worksheet.name] = M
        print(worksheet.name)

        assignment = M.getAssignments()
        n_row = worksheet.nrows

        for r in range(n_row - 1):

            row = worksheet.row_values(r + 1)
            workno = row[0]
            start = row[5]
            end = row[6]
            start_date_seconds = time.mktime(
                (int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13]), int(start[14:16]),
                 int(start[17:19]), 0, 0, 0))
            start_date_seconds = int(start_date_seconds)

            end_date_time = time.mktime(
                (int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13]), int(start[14:16]),
                 int(start[17:19]), 0, 0, 0))
            end_date_time = int(end_date_time)

            if workno == 'Setting Time':
                setting_time = Component(cycleTime=60 * 45, quantity=1, processCd= None, ifsetting=True)
                setting_time.setStartDateTime(start_date_seconds)
                setting_time.setEndDateTime(end_date_time)
                M.attach(setting_time)
                #setting_time.assignedTo(cnc)
                continue

            processCd = int((row[1])[1])
            goodCd = row[2]
            print(goodCd)
            gubun = row[3]
            due_date = row[7]
            qty = row[8]
            due_date_seconds = time.mktime(
                (int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]), 12, 0, 0, 0, 0, 0))  # 정오 기준
            due_date_seconds = int(due_date_seconds)

            if work_numbers.count(workno) == 0:
                work_numbers.append(workno)
                times = [0, 0, 0]
                new_job = Job(workno=workno, goodCd=goodCd, type=gubun, quantity=qty, time=times,
                              due=due_date_seconds)
                indiv.append(new_job)

            idx = work_numbers.index(workno)
            job = indiv[idx]
            new_component = Component(0, qty, processCd, job = job)
            new_component.setStartDateTime(start_date_seconds)
            new_component.setEndDateTime(end_date_time)
            job.setComponent(processCd, new_component)
            M.attach(new_component)

        i += 1 # 다음 sheet
        try:
            worksheet = workbook.sheet_by_index(i)
        except Exception:
            break

btn1 = Button(root, text = "스케줄 선택", command = inputFile)
btn1.grid(row = 1)
btn2 = Button(root, text = "완료", command = inputVariables)
btn2.bind(inputVariables)
btn2.grid(row = 8)

workno = StringVar()
due = StringVar()
goodNo = StringVar()
qty = IntVar()

input_workno = Entry(root, width = 20, text = "작업 지시서 번호")
input_due = Entry(root, width = 20, text = "납기(YYYYMMDD)")
input_goodNo = Entry(root, width = 20, text = "품번(숫자, 문자)")
input_goodCd = Entry(root, width = 20, text = "품번 코드(숫자)")
input_qty = Entry(root, width = 20, text = "수량")
input_gubun = Entry(root, width = 20, text = "타입구분")

lbl_workno = Label(root,  width = 15, text = "작업 지시서 번호")
lbl_due = Label(root, width = 15, text = "납기(YYYYMMDD)")
lbl_goodNo = Label(root, width = 15, text = "품번(숫자, 문자)")
lbl_goodCd = Label(root, width = 15, text = "품번 코드(숫자)")
lbl_qty = Label(root, width = 15, text = "수량")
lbl_gubun = Label(root, width = 15, text = "타입구분")

input_workno.grid(row = 2, column = 2)
input_due.grid(row = 3, column = 2)
input_goodNo.grid(row = 4, column = 2)
input_goodCd.grid(row = 5, column = 2)
input_qty.grid(row = 6, column = 2)
input_gubun.grid(row = 7, column = 2)


lbl_workno.grid(row = 2, column = 1)
lbl_due.grid(row = 3, column = 1)
lbl_goodNo.grid(row = 4, column = 1)
lbl_goodCd.grid(row = 5, column = 1)
lbl_qty.grid(row = 6, column = 1)
lbl_gubun.grid(row = 7, column = 1)

root.mainloop()


#read_schedule(root.filename)

'''
modified = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
color = modified
output = xlwt.Workbook(encoding='utf-8')


for key, machine in machines.items():
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
    # worksheet.write(row, 5, str(indexOfMin))
    row += 1
    for comp in machine.getAssignments():
        print_out_unit(comp, row, worksheet, color)
        row += 1

output.save("./schedules/test.xls")


#read_schedule(input)
'''
