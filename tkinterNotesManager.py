from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox as mb
from psycopg2 import *
from docx import Document

root = Tk()
root.geometry('800x600')
root.resizable(width=False, height=False)


class GUI:
    def __init__(self):
        # connect db
        self.conn = connect(dbname='notes', user='postgres', password='35121076', host='127.0.0.1')
        self.cur = self.conn.cursor()
        # last added id
        self.lastId = 0
        # bg image
        self.bgImage = PhotoImage(file='purpBg.png')
        self.canvas = Canvas(root, width=900, height=600)
        self.bg = self.canvas.create_image((0, 0), anchor='nw', image=self.bgImage, )
        # main text
        self.notesText = self.canvas.create_text((40, 40), anchor='nw',
                                                 text=f'Задачи:{self.getAllNotes(outInfo='string')}',
                                                 font='TimesNewRoman 14', fill='white')
        # new task's field
        self.newNoteEntry = Entry(root, width=60)
        self.newNoteEntry.place(x=10, y=560)
        # add note in db button
        self.addNoteButton = Button(root, text='OK', bg='#7c29d0', activebackground='#b27fe5', command=self.addNote)
        self.addNoteButton.place(x=380, y=556)
        # deleting list
        self.idList = ttk.Combobox(root, width=3, values=self.ids)
        self.idList.place(x=410, y=558)
        # delete from db button
        self.delNoteBut = Button(root, width=3, height=1, text='DEL', font='TimesNewRoman 8',
                                 bg='#7c29d0', activebackground='#b27fe5', command=self.delNote)
        self.delNoteBut.place(x=460, y=556)
        # save txt file button
        self.createTxtBut = Button(root, width=3, height=1, text='TXT', font='TimesNewRoman 8',
                                   bg='#7c29d0', activebackground='#b27fe5', command=self.createTxt)
        self.createTxtBut.place(x=490, y=556)
        # select docx file button
        self.createDocxBut = Button(root, width=5, height=1, text='DOCX', font='TimesNewRoman 8',
                                    bg='#7c29d0', activebackground='#b27fe5', command=self.createDocx)
        self.createDocxBut.place(x=520, y=556)

        self.canvas.pack()

    def addNote(self):
        """db record script"""
        global newNote

        if self.newNoteEntry.get():
            # adding to db
            newNote = str(self.newNoteEntry.get())
            self.cur.execute(f"INSERT INTO notes (id, note) "
                             f"VALUES ({self.lastId}, '{newNote}');")
            self.conn.commit()
            # update main text
            self.canvas.itemconfig(self.notesText, text=f'Задачи:{self.getAllNotes(outInfo='string')}')
            self.newNoteEntry.delete(0, 200)
            # update deleting list
            #self.canvas.update()
            self.idList.config(values=self.ids)
        else:
            mb.showerror('ОШИБКА!', 'Пустое поле!')

    def delNote(self):
        print(self.ids)
        if self.idList.get() and int(self.idList.get()) in self.ids:
            self.cur.execute("DELETE FROM notes "
                             f"WHERE id = {int(self.idList.get())};")
            self.conn.commit()

            self.notes, self.ids = self.getAllNotes(outInfo='tuples')
            self.cur.execute("DROP TABLE notes;"
                             "CREATE TABLE notes"
                             "("
                             "Id SERIAL PRIMARY KEY,"
                             "Note CHARACTER VARYING(200)"
                             ");")
            self.conn.commit()
            for tId in range(1, len(self.notes) + 1):
                self.cur.execute(f"INSERT INTO notes "
                                 f"VALUES ({tId}, '{self.notes[tId - 1]}')")
                self.conn.commit()
            self.canvas.itemconfig(self.notesText, text=f'Задачи:{self.getAllNotes(outInfo='string')}')
            self.idList.delete(0, 200)
            self.idList.config(values=self.ids)
            self.canvas.update()
        elif not self.idList.get():
            mb.showerror('ОШИБКА!', 'Пустое поле!')
        elif self.idList.get() not in self.ids:
            mb.showerror('ОШИБКА!', 'Введен неверный\n'
                                    'номер!')

    def createTxt(self):
        self.creatingTxtWin = Toplevel(root, bg='#b27fe5')
        Label(self.creatingTxtWin, text='Сохранение в формате ".txt"', bg='#b27fe5').pack()
        Button(self.creatingTxtWin, text='Выбрать место сохранения...', bg='#b27fe5',
               command=lambda: self.selectDirectory(fileType='txt')).pack()
        Label(self.creatingTxtWin, text='Введите имя нового файла:', bg='#b27fe5').pack()
        entryFileName = Entry(self.creatingTxtWin)
        entryFileName.pack()
        Button(self.creatingTxtWin, text='Создать', bg='#b27fe5',
               command=lambda: self.createTxtFile(fileName=entryFileName.get())).pack()

    def createDocx(self):
        self.creatingDocxWin = Toplevel(root, bg='#b27fe5')
        Label(self.creatingDocxWin, text='Сохранение в формате ".docx"', bg='#b27fe5').pack()
        Button(self.creatingDocxWin, text='Выбрать место сохранения...', bg='#b27fe5',
               command=lambda: self.selectDirectory(fileType='docx')).pack()
        Label(self.creatingDocxWin, text='Введите имя нового файла:', bg='#b27fe5').pack()
        entryFileName = Entry(self.creatingDocxWin)
        entryFileName.pack()
        Button(self.creatingDocxWin, text='Создать', bg='#b27fe5',
               command=lambda: self.createDocxFile(fileName=entryFileName.get())).pack()


    def createPdf(self):
        pass

    def getAllNotes(self, outInfo):
        self.cur.execute('SELECT * FROM notes;')
        self.conn.commit()
        notesTuples = self.cur.fetchall()
        self.notesStr = ''
        self.notes = []
        self.ids = []
        for noteTuple in notesTuples:
            self.notesStr += f'\n   {noteTuple[0]}. {noteTuple[1]}'
            self.lastId = noteTuple[0]
            self.notes.append(noteTuple[1])
            self.ids.append(noteTuple[0])
        self.lastId += 1

        if outInfo == 'string':
            return self.notesStr
        elif outInfo == 'tuples':
            return self.notes, self.ids

    def selectDirectory(self, fileType):
        self.directory = filedialog.askdirectory()
        if fileType == 'txt':
            self.creatingTxtWin.lift(root)
        elif fileType == 'docx':
            self.creatingDocxWin.lift(root)

    def createTxtFile(self, fileName):
        if self.getAllNotes(outInfo='string'):
            notes = self.getAllNotes(outInfo='string')
            try:
                txtFile = open(file=f'{self.directory}/{fileName}.txt', mode='w+', encoding="utf-8")
                txtFile.writelines(notes)
                txtFile.close()
                self.creatingTxtWin.destroy()

            except:
                mb.showerror('ОШИБКА', 'Не выбрана директория\nили название файла')
                self.createTxt()

    def dataForDocx(self):
        self.notes, self.ids = self.getAllNotes(outInfo='tuples')
        data = []
        for index in range(len(self.ids)):
            data.append((self.ids[index], self.notes[index]))

        data = tuple(data)
        return data

    def createDocxFile(self, fileName):
        if self.getAllNotes(outInfo='string'):
            doc = Document()

            table = doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'

            row = table.rows[0].cells
            row[0].text = '№'
            row[1].text = 'Заметка'

            for id, note in self.dataForDocx():
                row = table.add_row().cells
                row[0].text = str(id)
                row[1].text = note
            try:
                doc.save(f'{self.directory}/{fileName}.docx')
                self.creatingDocxWin.destroy()

            except:
                mb.showerror('ОШИБКА', 'Не выбрана директория\nили название файла')
                self.createDocx()


if __name__ == '__main__':
    tManager = GUI()
    root.mainloop()
