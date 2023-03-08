from fat32_directory import *
#from partition_boot_sector_ntfs import *
import tkinter
from tkinter import *
from tkinter import Tk, Text, TOP, BOTH, X, N, LEFT, scrolledtext, messagebox
from tkinter import Frame, Label, Entry
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import win32api
import os

# Colors
WHITE = '#FFFFFF'
BLACK = '#000000'
DARK = '#4D455D'
PINK = '#FF7483'
PURPLE = '#7F74B9'
LIGHT = '#F5E9CF'
LIGHT_BLUE = '#E9EFFF'
BLUE = '#0052C0'
YELLOW = '#FFCC8A'

getApp={".doc":"Microsoft Word",
        ".docx":"Microsoft Word",
        ".pdf":"Adobe Reader, Microsoft Edge,...",
        ".tex":"LaTeX",
        ".xls":"Microsoft Excel",
        ".xlsx":"Microsoft Excel",
        ".ppt":"Microsoft PowerPoint",
        ".pptx":"Microsoft PowerPoint",
        ".bmp":"Microsoft Photos",
        ".png":"Microsoft Photos",
        ".jpeg":"Microsoft Photos",
        ".jpg":"Microsoft Photos",
        ".mp3":"Window Media Player",
        ".wav":"Window Media Player",
        ".psd":"Adobe Photoshop",
        ".mp4":"Microsoft Movies & TV, Window Media Player,...",
        ".avi":"Microsoft Movies & TV, Window Media Player,...",
        ".mov":"Microsoft Movies & TV, Window Media Player,...",
        ".rar":"Rar, 7-zip,...",
        ".7z":"Rar,7-Zip,...",
        ".zip":"Rar,7-Zip,...",
        ".exe":"Command prompt",
        ".html":"Microsoft Edge",
        ".htm":"Microsoft Edge"
}


class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        ### root
        self.treeOfDirectory = None

        self.parent = parent
        self.initUI()


    def Screen(self, screen):
        # Title Frame
        textFrame = Frame(screen, bg=LIGHT_BLUE)
        textFrame.pack(fill=X)

        projectTxt = Label(textFrame, text="MANAGE FILE SYSTEM ON WINDOWS", font=("yu gothic ui", 18, 'bold'),
                     bg=LIGHT_BLUE, fg=BLUE, width=34)
        projectTxt.pack(anchor=N, padx=5, pady=20)

        # Function frame
        functionFrame = Frame(screen, bg=LIGHT_BLUE)
        functionFrame.pack()

        label1 = Label(functionFrame, text='Drive Selection', font=("yu gothic ui", 14, 'bold'), fg=BLACK, bg=LIGHT_BLUE)
        label1.pack(side=LEFT, padx=10, pady=20)

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

        selected_drive = tkinter.StringVar()
        combobox = ttk.Combobox(functionFrame, textvariable=selected_drive)
        combobox['value'] = drives
        combobox['state'] = 'readonly'
        combobox.pack(side=LEFT, padx=10, pady=25)
        combobox.bind("<<ComboboxSelected>>", self.callback)

        # Information frame
        informationFrame = Frame(screen, bg=LIGHT_BLUE)
        informationFrame.pack(fill=BOTH, expand=True)
        button = tkinter.Button(functionFrame, text='Boot Sector', font=("yu gothic ui", 10), bg=PURPLE, activeforeground=WHITE,
                                activebackground=YELLOW, command=lambda: self.Boot_Sector(selected_drive, informationFrame))
        button.pack(side=LEFT, padx=10, pady=25)

        button2 = tkinter.Button(functionFrame, text='Directory', font=("yu gothic ui", 10), bg=PINK, activeforeground=WHITE,
                                activebackground=YELLOW, command=lambda: self.Directory(selected_drive, informationFrame))
        button2.pack(side=LEFT, padx=10, pady=25)

        # Image frame
        imgFrame = Frame(screen, bg=LIGHT_BLUE)
        imgFrame.pack(fill=BOTH, expand=True)
    
        imgFrame.img = Image.open("./materials/computer.png")

        icon = ImageTk.PhotoImage(imgFrame.img)
        label = Label(imgFrame, image=icon, bg=LIGHT_BLUE)
        label.image = icon
        label.pack(anchor='s',side =RIGHT, padx=20, pady=0)

        # teacherTxt = Label(imgFrame, text="Teacher: Le Viet Long", font=("yu gothic ui", 14), bg=LIGHT_BLUE)
        # teacherTxt.pack(anchor='s', side=LEFT, padx=5, pady=20)

    
        imgFrame.member = Image.open("./materials/member.png")

        icon = ImageTk.PhotoImage(imgFrame.member)
        label = Label(imgFrame, image=icon, bg=LIGHT_BLUE)
        label.image = icon
        label.pack(anchor='s',side =LEFT, padx=15, pady=30)

        memberTxt = "Members:   Huynh Duc Thien    \nLe Anh Thu - Nguyen Minh Dat\n  Phan Thanh An - Nguyen Hi Huu"
        memberTxt = Label(imgFrame, text=memberTxt, font=("yu gothic ui", 13), bg=LIGHT_BLUE)
        memberTxt.pack(anchor='s', side=LEFT, padx=0, pady=25)

    def Boot_Sector(self,selected_drive, frame):
        drive = selected_drive.get()
        if drive == "":
            tkinter.messagebox.showerror(title="Error", message="No drive was chosen! Please choose a drive.")
            return
        # print(drive)
        list = frame.pack_slaves()
        for l in list:
            l.destroy()
        label = Label(frame, text="BIOS Parameter Block information", font=("Cambria", 12), bg=LIGHT_BLUE)
        label.pack(anchor=N, padx=5, pady=5)
        if (win32api.GetVolumeInformation(drive)[4]=='FAT32'):
            # print(drive)
            data = BootSector(drive[0])
            txt = data.showInfo()
            text = Text(frame, font=("Cambria", 12), bg=LIGHT_BLUE, spacing1=4, relief=FLAT)
            text.insert(END, txt)
            text.pack(side=LEFT, padx=80, pady=10)
        if (win32api.GetVolumeInformation(selected_drive.get())[4]=='NTFS'):
            path = "\\\.\\"
            for i in range(0, len(drive) - 1):
                path += drive[i]
            print(path)
            # boots = BootSectorNTFS(None, 0, 512, path)
            # txt = boots.show_infor()
            text = Text(frame, font=("Cambria", 12), bg=LIGHT_BLUE, spacing1=4, relief=FLAT)
            text.insert(END, txt)
            text.pack(side=LEFT, padx=50, pady=10)


    def open_children(self,parent):
        self.tree.item(parent, open=True)
        for child in self.tree.get_children(parent):
            self.open_children(child)

    def handleOpenEvent(self,event):
        self.open_children(self.tree.focus())

    ####....Directory
    def getPath(self, item, path):
        parent_iid = self.tree.parent(item)
        if parent_iid:
            temp = self.tree.item(parent_iid)['text']
            return self.getPath(parent_iid, "\\" + self.tree.item(item, "text") + path)
        return "\\" + self.tree.item(item, "text") + path

    def OnDoubleClick(self, event):
        item = self.tree.selection()
        print("you clicked on", self.tree.item(item, "text"))
        file_name, file_extension = os.path.splitext(self.tree.item(item, "text"))
        file_extension = file_extension.lower()
        if file_extension == ".txt":
            path = ''
            path = self.getPath(item, path)
            path = path[1:len(path)]
            path = open(path, 'r', encoding='utf-8')
            data = path.read()
            path.close()
            window = Tk()
            window.title(self.tree.item(item, "text"))
            window.geometry("300x300+300+300")
            text = Text(window, font=("Cambria", 12), bg=LIGHT_BLUE, spacing1=4, relief=FLAT)
            text.insert(END, data)
            text.pack()
            window.mainloop()
        else:
            path = ''
            path = self.getPath(item, path)
            path = path[1:len(path)]
            if file_extension=="":
                return
            try:
                extension=getApp[file_extension]
            except:
                tkinter.messagebox.showwarning(title="Warning",message="Couldn't find the appropriate app to open this file.")
            else:
                msgBox=tkinter.messagebox.askyesno (title="Recommend application", message="This file can be opened with "+extension+".Do you want to open?")
                if msgBox:
                    print("Open:",path)
                    os.startfile(path)

    def OnSelection(self, text):
        item = self.tree.selection()
        print("you clicked on", self.tree.item(item, "text"))
        path = ''
        path = self.getPath(item, path)
        path = path[1 : len(path)]
        # good until here
        # print(path)
        property = self.treeOfDirectory.getPropertyFromPath(self.treeOfDirectory.children, path)
        text.delete("1.0", END)
        text.insert(END, property)

    def insertDirectory(self, root, disk):
        id = self.tree.insert('', 'end', text=disk, open=False)
        self.insertChild(root,id)

    def insertChild(self, root, id):
        children = root.getChildrenList()
        if (len(children) > 0):
            for child in children:
                index = self.tree.insert(id, 'end', text=child.getFileName(), open=False)
                if child.getAttribute() == DIRECTORY:
                    self.insertChild(child,index)

    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)

    def Directory(self, selected_drive, frame):
        drive = selected_drive.get()
        if drive == "":
            tkinter.messagebox.showerror(title="Error", message="No drive was chosen! Please choose a drive.")
            return

        window = tkinter.Toplevel()
        window.geometry("250x40")
        window.title('Notification')
        Message(window,text="Waiting a second......", padx=30, pady=50).pack()
        window.update()

        # get tree information
        path = ""
        if (win32api.GetVolumeInformation(drive)[4] == 'FAT32'):
            path = "\\\.\\"
            for i in range(0, len(drive) - 1):
                path += drive[i]
            # bootSectorData = BootSectorFAT32().readBootSector(path)
            # pbr_fat = PbrFat(bootSectorData)
            # pbr_fat.readFat()
            # fat_table = FatTable(path, pbr_fat)
            # dir = fat_table.getRootDirectory()
            # fat_table.getDirectory(dir)
            # self.treeOfDirectory = Root(fat_table.getDir())
            self.treeOfDirectory = Root(drive[0])
        if (win32api.GetVolumeInformation(selected_drive.get())[4] == 'NTFS'):
            path = "\\\.\\"
            for i in range(0, len(drive) - 1):
                path += drive[i]
            boots = BootSectorNTFS(None, 0, 512, path)
            MFTable = MFT(filename=path, offset=boots.mft_offset)
            MFTable.preload_entries()
            # myTree = RootNTFS(MFTable.entries)
            self.treeOfDirectory = RootNTFS(MFTable.entries, path)
        list = frame.pack_slaves()
        for l in list:
            l.destroy()
        splitter = tk.PanedWindow(frame, orient=tk.HORIZONTAL)
        # Left-side
        frame_left = tk.Frame(splitter)
        self.tree = ttk.Treeview(frame_left, selectmode='browse')
        ysb = ttk.Scrollbar(frame_left, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(frame_left, orient='horizontal', command=self.tree.xview)
        # Right-side
        frame_right = tk.Frame(splitter)
        text = scrolledtext.ScrolledText(frame_right, font=("Cambria", 12), bg=LIGHT_BLUE, spacing1=4, relief=FLAT)

        # overall layout
        splitter.add(frame_left)
        splitter.add(frame_right)
        splitter.pack(fill=tk.BOTH, expand=1)
        # left-side widget layout
        self.tree.grid(row=0, column=0, sticky='NSEW')
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        # left-side frame's grid config
        frame_left.columnconfigure(0, weight=1)
        frame_left.rowconfigure(0, weight=1)
        # right-side widget layout
        text.pack(padx=10, pady=10, fill="both")

        self.tree.configure(yscrollcommand=lambda f, l: self.autoscroll(ysb, f, l),
                            xscrollcommand=lambda f, l: self.autoscroll(xsb, f, l))

        self.insertDirectory(self.treeOfDirectory.getRoot(), path[4:len(path)])
        window.destroy()
        self.tree.bind('<<TreeviewOpen>>', self.handleOpenEvent)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.tree.bind("<ButtonRelease-1>", lambda envent: self.OnSelection(text))

    def callback(self,eventObject):
         return eventObject.widget.get()
        # print(dir(eventObject))

    def initUI(self):
        self.style = ttk.Style()

        self.style.theme_create("yummy", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": WHITE}},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 1], "background": WHITE},
                "map": {"background": [("selected", LIGHT_BLUE)],
                        "expand": [("selected", [1, 1, 1, 0])]}}})

        self.pack(fill=BOTH, expand=True)
        self.style.theme_use("yummy")
        tab_control = ttk.Notebook(self)

        screen = Frame(tab_control, background=LIGHT_BLUE)
        screen.pack()

        tab_control.add(screen, text="FAT-NTFS Project")
        self.Screen(screen)
        tab_control.pack(expand=1, fill='both')

root = Tk()
root.title("Operating System")
root.geometry("800x600+100+100")
root.iconbitmap('./materials/cat.ico')  
app = App(root)
root.mainloop()