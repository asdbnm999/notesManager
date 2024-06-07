from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from psycopg2 import *

root = Tk()
root.geometry('800x600')
root.resizable(width=False, height=False)


class GUI:
    def __init__(self):
        self.conn = connect(dbname='notes', user='postgres', password='35121076', host='127.0.0.1')
        self.cur = self.conn.cursor()
        self.lastId = 0
        self.bgImage = PhotoImage(file='purpBg.png')
        self.canvas = Canvas(root, width=900, height=600)
        self.bg = self.canvas.create_image((0, 0), anchor='nw', image=self.bgImage, )
        self.notesText = self.canvas.create_text((40, 40), anchor='nw',
                                                 text=f'Задачи:{self.getAllNotes(outInfo='string')}',
                                                 font='TimesNewRoman 14', fill='white')
        self.newNoteEntry = Entry(root, width=60, )
        self.sendNoteButton = Button(root, text='OK', bg='#7c29d0', activebackground='#b27fe5', command=self.addNote)
        self.sendNoteButton.place(x=380, y=556)
        self.newNoteEntry.place(x=10, y=560)
        self.idList = ttk.Combobox(root, width=3, values=self.ids)
        self.idList.place(x=410, y=558)
        self.delNoteBut = Button(root, width=3, height=1, text='DEL', font='TimesNewRoman 8',
                                 bg='#7c29d0', activebackground='#b27fe5', command=self.delNote)
        self.delNoteBut.place(x=460, y=556)
        self.createTxtBut = Button(root, width=3, height=1, text='TXT', font='TimesNewRoman 8',
                                   bg='#7c29d0', activebackground='#b27fe5', command=self.createTxt)
        self.createDocxBut = Button(root, width=3, height=1, text='TXT', font='TimesNewRoman 8',
                                   bg='#7c29d0', activebackground='#b27fe5', command=self.createDocx)
        self.createPdfBut = Button(root, width=3, height=1, text='TXT', font='TimesNewRoman 8',
                                   bg='#7c29d0', activebackground='#b27fe5', command=self.createPdf)
        self.createTxtBut.place(x=490, y=556)
        self.canvas.pack()

    def addNote(self):
        global newNote

        if self.newNoteEntry.get():
            newNote = str(self.newNoteEntry.get())
            self.cur.execute(f"INSERT INTO notes (id, note) "
                             f"VALUES ({self.lastId}, '{newNote}');")
            self.conn.commit()
            self.canvas.itemconfig(self.notesText, text=f'Задачи:{self.getAllNotes(outInfo='string')}')
            self.newNoteEntry.delete(0, 200)
            self.canvas.update()
            self.idList.config(values=self.ids)
        else:
            mb.showerror('ОШИБКА!', 'Пустое поле!')

    def delNote(self):
        if self.idList.get() and self.idList.get() in self.ids:
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
        self.getAllNotes(outInfo=)

    def createDocx(self):
        pass

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


if __name__ == '__main__':
    tManager = GUI()
    root.mainloop()