# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
from Utils import CreateToolTip, Autoresized_Notebook

import tkinter as tk
from tkinter import messagebox,ttk,filedialog
from tktable import Table

from NewJobWindow import JobEntryBox
from NewServerConfig import ServerEntryBox
from SimDirectory import SimDirectory

import threading

class MainWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.window_title = "Sim Agent MPI (University of Missouri - Nair Neural Engineering Laboratory - Banks)"
        self.about_text = "Written for:\nProfessor Satish Nair's Neural Engineering Laboratory\nat The University of Missouri\n\nWritten by: Tyler Banks\n\nContributors:\nFeng Feng\nBen Latimer\nZiao Chen\n\nEmail tbg28@mail.missouri.edu with questions"
        
        self.window_size = '1220x600'
        self.default_status = "Status: Ready"
        self.status_timer = 4.0
        
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.root.title(self.window_title)
        self.root.geometry(self.window_size)
        
        #self.root.resizable(0,0)
        self.root.config(menu=self.menu_bar(self.root))
        
        self.app_status = tk.StringVar(self.root,'')
        self.reset_app_status()
        
        print('Starting. Please wait...')
        self.style = ttk.Style()
        try:
            self.style.theme_create( "colored", parent="alt", settings={
                    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                    "TNotebook.Tab": {
                        "configure": {"padding": [5, 2], "background": "#D9D9D9" },
                        "map":       {"background": [("selected", "#C0C0E0")],
                                      "expand": [("selected", [1, 1, 1, 0])] } } } )
        
            self.style.theme_create( "largertheme", parent="alt", settings={
                    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                    "TNotebook.Tab": {
                        "configure": {"padding": [5, 2] },
                        "map":       {
                                      "expand": [("selected", [1, 1, 1, 0])] } } } )
            self.style.theme_use("colored")
        except Exception:
            print('Style loaded previously. Continuing.')
        
        frame1 = tk.Frame(self.root)
        frame1.grid(row=0,column=0,sticky='news')
        frame1.columnconfigure(0,weight=1)
        frame1.columnconfigure(0,weight=1)
        frame2 = tk.Frame(self.root)
        frame2.grid(row=1,column=0,sticky='news')
        
        nb = Autoresized_Notebook(frame1)
        nb.pack(padx=5,pady=5,side="left",fill="both",expand=True)
        
        bottom_status_bar = tk.Frame(frame2)
        bottom_status_bar.grid(row=0,column=0,padx=5,pady=2)#,fill=tk.X,expand=True)
        
        label = tk.Label(bottom_status_bar,textvariable=self.app_status)
        label.pack(expand=True)
    
        page1 = ttk.Frame(nb)
        
        nb.add(page1, text='Manage Jobs')
        
        #Alternatively you could do parameters_page(page1), but wouldn't get scrolling
        self.bind_page(page1, self.jobs_page)
        
        self.display_app_status("Ready")
                
        return
    
    def show(self):
        try:
            print('Load complete. Running...')
            self.root.mainloop()
        except Exception:
            print('Error, closing display loop')
        print('Closing.\n')
        
    def bind_page(self, page, gen_frame):
        #### Scrollable Frame Window ####
        #https://stackoverflow.com/questions/42237310/tkinter-canvas-scrollbar
        frame = tk.Frame(page, bd=2)
        frame.pack(side="left",fill="both",expand=True)
        
        yscrollbar = tk.Scrollbar(frame)
        yscrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        xscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM,fill=tk.X)
        
        canvas = tk.Canvas(frame, bd=0,
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set,)
        
        xscrollbar.config(command=canvas.xview)
        yscrollbar.config(command=canvas.yview)
        
        f=tk.Frame(canvas)
        canvas.pack(side="left",fill="both",expand=True)
        canvas.create_window(0,0,window=f,anchor='nw')
        ###############################
        gen_frame(f)
        frame.update()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def reset_app_status(self):
        self.app_status.set(self.default_status)

    def display_app_status(self,str):
        self.app_status.set("Status: "+str)
        threading.Timer(4.0, self.reset_app_status).start()
        
    def menu_bar(self, root):
            
        menubar = tk.Menu(root)
        
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Add Server", command=self.add_server)
        #filemenu.add_command(label="Save", command=hello)
        #filemenu.add_separator()
        #filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        return menubar
    
    
    def jobs_page(self, root):
        
        #open project dir
        #print(filedialog.askdirectory())
        directory_frame = tk.LabelFrame(root, text="Directory")
        jobs_frame = tk.LabelFrame(root, text="Jobs")
        notes_frame = tk.LabelFrame(root, text="Job Notes")
        log_frame = tk.LabelFrame(root, text="Job Log")
        button_width = 15
        
        
        b = tk.Button(directory_frame, text="Select Directory", command=self.load_dir, width=button_width)
        b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
        
        self.sim_dir_var = tk.StringVar(root)
        self.sim_dir_label = tk.Label(directory_frame, fg="blue",textvariable=self.sim_dir_var)
        self.sim_dir_label.grid(column=1,row=0,sticky='news',padx=10,pady=5)
            
        """=Jobs Frame======================================"""
        
        buttons_frame = tk.LabelFrame(jobs_frame, text="")        
        buttons_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        
        
        b = tk.Button(buttons_frame, text="New Job", command=self.new_job, width=button_width)
        b.grid(pady=5, padx=5, column=1, row=0, sticky="WE")
        
        b = tk.Button(buttons_frame, text="Clone to New Job", command=self.new_job, width=button_width)
        b.grid(pady=5, padx=5, column=2, row=0, sticky="WE")
        
        b = tk.Button(buttons_frame, text="Edit Job", command=self.new_job, width=button_width)
        b.grid(pady=5, padx=5, column=3, row=0, sticky="WE")
        
        b = tk.Button(buttons_frame, text="Start Job", command=self.new_job, width=button_width)
        b.grid(pady=5, padx=5, column=4, row=0, sticky="WE")
        
        b = tk.Button(buttons_frame, text="Stop Job", command=self.new_job, width=button_width)
        b.grid(pady=5, padx=5, column=5, row=0, sticky="WE")
        
        b = tk.Button(buttons_frame, text="Open Job Results", command=self.new_job, width=button_width)
        b.grid(pady=5, padx=5, column=6, row=0, sticky="WE")
        
        def printrow(row):
            print(str(table.row(row)))
            
        columns = ["Name", "Status", "Server", "Tool/Partition", "Nodes", "Cores", "Runtime", "Start", "Remote ID"]
        col_wid = [200, 75, 100, 100, 50, 50, 100, 100, 150]
        table = Table(jobs_frame, columns, column_minwidths=col_wid,height=300, onselect_method=printrow)
        
        table.grid(row=1,column=0,padx=10,pady=10)
    
        table.set_data([[""],[""],[""],[""],[""],[""],[""],[""],[""]])
        #table.cell(0,0, " a fdas fasd fasdf asdf asdfasdf asdf asdfa sdfas asd sadf ")
        #table.grid_propagate(False) #Is this really the only way to get it to a specific size?
            
        table.insert_row([22,23,24])
        table.insert_row([25,26,27],index=0)
        
        """=Note Frame======================================"""
        
        
        
        
        """=Logs Frame======================================"""
        
        
        """================================================="""
        
        
        directory_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5,columnspan=2)
        jobs_frame.grid(column=0,row=1,sticky='news',padx=10,pady=5,columnspan=2)
        notes_frame.grid(column=0,row=2,sticky='news',padx=10,pady=5)
        log_frame.grid(column=1,row=2,sticky='news',padx=10,pady=5)
        
        return

    def add_server(self):
        ServerEntryBox(self.root)#,server_id="180521092555")
            
    def about(self):
        messagebox.showinfo("About", self.about_text, icon='info')
            
    def new_job(self):
        new_job = JobEntryBox(self.root, self.sim_dir)
        if(new_job.confirm and new_job.is_valid()):
            simjob = new_job.to_simjob()
            simjob.create_sim_directory()
            simjob.write_properties()
            self.sim_dir.add_new_job(simjob)
            return
        return
    
    def load_dir(self):
            dir_ = filedialog.askdirectory()
            if not dir_:
                return
            try:
                self.sim_dir = SimDirectory(dir_,initialize=True)
                self.sim_dir_var.set(self.sim_dir.sim_directory)
            except Exception as e:
                return
            return
