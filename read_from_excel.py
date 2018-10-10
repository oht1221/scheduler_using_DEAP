import xlrd, xlwt
import datetime
import sys
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
import time
from evaluation import Machine
from job import *
from accessDB import *
from preprocessing import search_cycle_time, read_CNCs
from displays_results import *
import copy

VALVE_PRE_CNCs = [1, 2, 3, 32, 33, 34, 37, 38, 44]
LOK_FORGING_CNCs = [10, 15]
LOK_HEX_CNCs = [8, 9, 11, 12, 13]
indiv = []
work_numbers = []
CNCs = []
read_CNCs('./장비정보.xlsx', CNCs)

machines = {}
new_job = None
date_from = 0
date_until = 0
standard = 0
num_unassigned = 0
num_assigned = 0

CNCs_2jaw = list(filter(lambda x: x.getShape() == 0, CNCs))
CNCs_3jaw = list(filter(lambda x: x.getShape() == 1, CNCs))
CNCs_round = list(filter(lambda x: (x.getShape() == 1 and not (x.getNote() == "코렛")), CNCs))
CNCs_square = list(filter(lambda x: x.getShape() == 0, CNCs))
CNCs_valve_pre = list(filter(lambda x: x.getNumber() in VALVE_PRE_CNCs, CNCs))
CNCs_LOK_size_forging = list(filter(lambda x: x.getNumber() in LOK_FORGING_CNCs, CNCs))
CNCs_LOK_size_hex = list(filter(lambda x: x.getNumber() in LOK_HEX_CNCs, CNCs))

root = Tk()




def insert(CNC_list, insertion, due):
    selected_machines = dict()
    for c in CNC_list:
        selected_machines[float(c.getNumber())] = machines[float(c.getNumber())]

    diff_smallest = 99999999999999999

    best = None
    for num, machine in selected_machines.items():
        assignments = machine.getAssignments()
        position = 0
        insertion_comp_start = standard + 0
        while 1:
            new_assignments = copy.deepcopy(assignments)
            new_insertion = copy.deepcopy(insertion)
            step = 0
            for insertion_comp in new_insertion:
                extension = insertion_comp.getTime()
                for pushed_back_comp in new_assignments[(position + step):]:  # insertion position 뒤에있는 component들 extension만큼 뒤로 밀어냄
                    pushed_back_comp.setStartDateTime(pushed_back_comp.getStartDateTime() + extension)
                    pushed_back_comp.setEndDateTime(pushed_back_comp.getEndDateTime() + extension)


                insertion_comp.setStartDateTime(insertion_comp_start)
                insertion_comp.setEndDateTime(insertion_comp_start + insertion_comp.getTime())
                insertion_comp_start = insertion_comp.getEndDateTime()
                new_assignments.insert(position + step, insertion_comp)
                step += 1

            if (new_insertion[-1]).getEndDateTime() > due: #새 작업의 납기 못 지키게 되면 다른 machine으로
                break

            diff = 0
            for comp in new_assignments[(position + step):]:
                if not comp.isSetting():
                    diff += (-1) * min((comp.getJob()).getDue() - comp.getEndDateTime(), 0)

            if diff < diff_smallest:  # diff 더 작은 작업 배치로 바꿈
                diff_smallest = diff
                best = new_assignments
                cnc_num = num

            position += 2
            if position >= len(assignments) - 1: # 마지막 포지션까지 왔으면
                break
            insertion_comp_start = assignments[position].getStartDateTime()

    if best is not None:
        for comp in best:
            startTime = datetime.datetime.fromtimestamp(comp.getStartDateTime()).strftime('%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.fromtimestamp(comp.getEndDateTime()).strftime('%Y-%m-%d %H:%M:%S')

            if not comp.isSetting():
                print(comp.getJob().getWorkno() + " " + str(startTime) + " " + str(endTime))
            else:
                print("setting time", startTime, endTime)
            print("")
        print("new job has been assigned to cnc# : %d"%cnc_num)
        machines[cnc_num].assignments = best
        return 1

    else:
        return -1

def makeInsertion(job):

    insertion = list()
    for comp in job.getComponents():
        insertion.append(comp)
        setting_time = Component(cycleTime=60 * 45, quantity=1, processCd=None, ifsetting=True)
        insertion.append(setting_time)

    return insertion

def insertAndCheck(new_job):

    TOTAL_DELAYED_JOBS_COUNT = 0
    TOTAL_DELAYED_TIME = 0
    insertion = makeInsertion(new_job)
    if len(insertion) <= 1:
        messagebox.showerror("Warning!", "해당 품번 코드의 사이클 타임 정보를 읽어올 수 없습니다.")
        return

    status = 0

    if new_job.getLokFittingSize() == 1:
        if new_job.getType() == 0:
            status = insert(CNCs_LOK_size_forging, insertion, new_job.getDue())

        elif new_job.getType() == 1:
            status = insert(CNCs_LOK_size_hex, insertion, new_job.getDue())

    elif new_job.getType() == 0:
        status = insert(CNCs_2jaw, insertion, new_job.getDue())

    elif new_job.getType() == 1:
        status = insert(CNCs_3jaw, insertion, new_job.getDue())

    elif new_job.getType() == 2:
        status = insert(CNCs_round, insertion, new_job.getDue())

    elif new_job.getType() == 3:
        status = insert(CNCs_square, insertion, new_job.getDue())

    elif new_job.getType() == 4:
        status = insert(CNCs_valve_pre, insertion, new_job.getDue())

    else:
        print("job type error!")

    return status


def readFile():
    root.filename = filedialog.askopenfilename(initialdir = "./schedules",
                                               title = 'choose your schdule',
                                               filetypes = (('excel files', '*.xlsx'),
                                                            ('excel files', '*.xls'))
                                               )
    read_schedule(root.filename)

    messagebox.showinfo("message", "파일 읽기 완료!")

def print_new_schedule(assignment, total_number, total_number_unassgiend, added):
    output = xlwt.Workbook(encoding='utf-8')  # utf-8 인코딩 방식의 workbook 생성
    output.default_style.font.height = 20 * 11  # (11pt) 기본폰트설정 다양한건 찾아보길
    modified = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    color = modified

    worksheet = output.add_sheet("비고")
    worksheet.write(0, 0, "기준 시간")
    worksheet.write(0, 1, standard)
    worksheet.col(0).width = 256 * 15

    worksheet.write(1, 0, "date_from")
    worksheet.write(1, 1, date_from)
    worksheet.col(1).width = 256 * 15

    worksheet.write(2, 0, "date_until")
    worksheet.write(2, 1, date_until)
    worksheet.col(2).width = 256 * 15

    worksheet.write(3, 0, "배정된 작업 수 ")
    worksheet.write(3, 1, num_assigned + 1)
    worksheet.col(3).width = 1024 * 15

    worksheet.write(4, 0, "배정되지 않은 작업 수")
    try:
        worksheet.write(4, 1, num_unassigned)
    except Exception:
        pass

    worksheet.col(4).width = 1024 * 15

    worksheet.write(5, 0, "cycle time 정보 부족")

    worksheet.col(5).width = 512 * 15

    for key, machine in assignment.items():
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
    file_name = (root.filename.split('.')[0] + "_added_" + added) + ".xls"
    output.save(file_name)
    return


def inputVariablesAndInsertJob():

    global standard
    if standard == 0:
        messagebox.showerror("Warning!", "스케줄을 먼저 선택하셔야합니다.")
        return
    workno = input_workno.get()
    due = input_due.get()

    due_date_seconds = time.mktime(
        (int(due[0:4]), int(due[4:6]), int(due[6:8]), 12, 0, 0, 0, 0, 0))  # 정오 기준
    due_date_seconds = int(due_date_seconds)

    #goodNo = input_goodNo.get()
    goodCd = input_goodCd.get()
    qty = int(input_qty.get())
    cursor = AccessDB()
    cycle_time = []
    gubun = int(input_gubun.get())

    search_cycle_time(cursor, cycle_time, goodCd)

    new_job = Job(workno=workno, goodCd=goodCd, type=gubun, quantity=qty, time=cycle_time,
                              due=due_date_seconds)

    status = insertAndCheck(new_job)

    if status == -1:
        messagebox.showerror("Warning!", "납기를 만족시킬 수 없습니다.")
    if status == 1:
        print_new_schedule(machines, num_assigned, num_unassigned, new_job.getWorkno())



def read_schedule(input):
    workbook = xlrd.open_workbook(input)
    worksheet = workbook.sheet_by_name('비고')

    global standard
    global num_unassigned
    global date_from
    global date_until
    global num_assigned

    row = worksheet.row_values(0)
    standard = row[1]
    row = worksheet.row_values(1)
    date_from = row[1]
    row = worksheet.row_values(2)
    date_until = row[1]
    row = worksheet.row_values(3)
    num_assigned = row[1]
    row = worksheet.row_values(4)
    num_unassigned = row[1]

    standard = (lambda x: int(time.time()) if (x == 'now') else time.mktime(
        (int(x[0:4]), int(x[4:6]), int(x[6:8]), 12, 0, 0, 0, 0, 0)))(standard)


    i = 1
    worksheet = workbook.sheet_by_index(i)

    while worksheet is not None:
        M = Machine()
        machines[float(worksheet.name)] = M
        n_row = worksheet.nrows

        for r in range(n_row - 1):

            row = worksheet.row_values(r + 1)
            workno = row[0]
            goodCd = row[2]
            start = row[5]
            end = row[6]
            start_date_seconds = time.mktime(
                (int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13]), int(start[14:16]),
                 int(start[17:19]), 0, 0, 0))
            start_date_seconds = int(start_date_seconds)

            end_date_time = time.mktime(
                (int(end[0:4]), int(end[5:7]), int(end[8:10]), int(end[11:13]), int(end[14:16]),
                 int(end[17:19]), 0, 0, 0))
            end_date_time = int(end_date_time)

            if workno == 'Setting Time':
                setting_time = Component(cycleTime=60 * 45, quantity=1, processCd= None, ifsetting=True)
                setting_time.setStartDateTime(start_date_seconds)
                setting_time.setEndDateTime(end_date_time)
                M.attach(setting_time)
                #setting_time.assignedTo(cnc)
                continue

            processCd = int((row[1])[1])
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

    print("파일 입력 완료!")

btn1 = Button(root, text = "스케줄 선택", command = readFile)
btn2 = Button(root, text = "완료", command = inputVariablesAndInsertJob)


workno = StringVar()
due = StringVar()
goodNo = StringVar()
qty = IntVar()

input_workno = Entry(root, width = 20, text = "작업 지시서 번호")
input_due = Entry(root, width = 20, text = "납기(YYYYMMDD)")
#input_goodNo = Entry(root, width = 20, text = "품번(숫자, 문자)")
input_goodCd = Entry(root, width = 20, text = "품번 코드(숫자)")
input_qty = Entry(root, width = 20, text = "수량")
input_gubun = Entry(root, width = 20, text = "타입구분")

lbl_workno = Label(root,  width = 15, text = "작업 지시서 번호")
lbl_due = Label(root, width = 15, text = "납기(YYYYMMDD)")
#lbl_goodNo = Label(root, width = 15, text = "품번(숫자, 문자)")
lbl_goodCd = Label(root, width = 15, text = "품번 코드(숫자)")
lbl_qty = Label(root, width = 15, text = "수량")
lbl_gubun = Label(root, width = 15, text = "타입구분")
lbl_show_state = Label(root)


btn1.grid(row = 1)

lbl_workno.grid(row = 2, column = 1)
input_workno.grid(row = 2, column = 2)

lbl_due.grid(row = 3, column = 1)
input_due.grid(row = 3, column = 2)

#lbl_goodNo.grid(row = 4, column = 1)
#input_goodNo.grid(row = 4, column = 2)

lbl_goodCd.grid(row = 4, column = 1)
input_goodCd.grid(row = 4, column = 2)

lbl_qty.grid(row = 5, column = 1)
input_qty.grid(row = 5, column = 2)

lbl_gubun.grid(row = 6, column = 1)
input_gubun.grid(row = 6, column = 2)

lbl_show_state.grid(row = 7)

btn2.grid(row = 8)

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

