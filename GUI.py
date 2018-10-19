from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
#import evolution

'''
class myApp:
    def __init__(self, parent):
        self.myparent = parent
        self.initUI()
        self.lbl_start.place(x = -10, y = 10)
        self.input_start.place(x = 20 , y= 10)

        self.lbl_standard.place(x = -10, y = 30)
        self.input_standard.place(x = 20, y = 30)

        # lbl_goodNo.grid(row = 4, column = 1)
        # input_goodNo.grid(row = 4, column = 2)

        self.lbl_NGEN.place(x = -10, y = 50)
        self.input_NGEN.place(x = 20, y = 50)

        self.btn1.place(x = 130, y = 80)

    def initUI(self):
        self.start = StringVar()
        self.standard = StringVar()
        self.end = "29991212"
        self.NGEN = IntVar()
        self.btn1 = Button(self.myparent,
                           text="스케줄 생성",
                           command=self.action_btn1)
        self.input_start = Entry(self.myparent, width=30, text="납기 시작 일자  ")
        self.input_standard = Entry(self.myparent, width=30, text="배정 기준일  ")
        # input_goodNo = Entry(root, width = 20, text = "품번(숫자, 문자)")
        self.input_NGEN = Entry(self.myparent, width=30, text="반복 횟수  ")

        self.lbl_start = Label(self.myparent, width=15, text="납기 시작 일자")
        self.lbl_standard = Label(self.myparent, width=15, text="배정 기준일")
        self.lbl_NGEN = Label(self.myparent, width=15, text="반복 횟수")


    def accpetVariables(self):
        self.start = self.input_start.get()
        self.standard = self.input_standard.get()
        self.NGEN = self.input_NGEN.get()

        return 0

    def printInputs(self):
        print(self.start, "\n", self.standard, "\n", self.NGEN, "\n")

        return 0

    def action_btn1(self):
        self.accpetVariables()
        self.printInputs()
        return 0



#btn2 = Button(root, text = "완료", command = inputVariablesAndInsertJob)


'''






if __name__ == "__main__":
    def accpetVariables():
        start = input_start.get()
        standard = input_standard.get()
        NGEN = input_NGEN.get()

        return 0


    def printInputs():
        print(start, "\n", standard, "\n", NGEN, "\n")
        return 0


    def action_btn1():
        accpetVariables()
        printInputs()
        return 0

    root = Tk()
    root.geometry("300x150+300+300")

    start = StringVar()
    standard = StringVar()
    end = "29991212"
    NGEN = IntVar()

    start = StringVar()
    standard = StringVar()
    end = "29991212"
    NGEN = IntVar()

    btn1 = Button(root,
                       text="스케줄 생성",
                       command=action_btn1)
    input_start = Entry(root, width=30, text="납기 시작 일자  ")
    input_standard = Entry(root, width=30, text="배정 기준일  ")
    # input_goodNo = Entry(root, width = 20, text = "품번(숫자, 문자)")
    input_NGEN = Entry(root, width=30, text="반복 횟수  ")

    lbl_start = Label(root, width=15, text="납기 시작 일자")
    lbl_standard = Label(root, width=15, text="배정 기준일")
    lbl_NGEN = Label(root, width=15, text="반복 횟수")
    lbl_start.grid(row = 1, column = 1)
    input_start.grid(row = 1, column = 2)

    lbl_standard.grid(row = 2, column = 1)
    input_standard.grid(row = 2, column = 2)

    # lbl_goodNo.grid(row = 4, column = 1)
    # input_goodNo.grid(row = 4, column = 2)

    lbl_NGEN.grid(row = 3, column = 1)
    input_NGEN.grid(row = 3, column = 2)

    btn1.place(x=130, y=80)

    root.mainloop()






