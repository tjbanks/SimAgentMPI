# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
from SimAgentMPI.Utils import Autoresized_Notebook,CreateToolTip

import tkinter as tk
from tkinter import messagebox,ttk,filedialog,OptionMenu
from SimAgentMPI.tktable import Table
import datetime
from PIL import ImageTk, Image
import os, time, enum

import SimAgentMPI
from SimAgentMPI.NewJobWindow import JobEntryBox, Create_Batch_File
from SimAgentMPI.NewServerConfig import ServerEntryBox,SelectServerEditBox
from SimAgentMPI.SimDirectory import SimDirectory
from SimAgentMPI.ServerInterface import ServerInterface
from SimAgentMPI.SimJob import SimJob
from SimAgentMPI.SimServer import ServersFile
from SimAgentMPI.Utils import Batch_File,StoppableThread,UpdateWindow
from SimAgentMPI.ParametricSweep import ParametricSweep

import threading

class MainWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.window_title = "Sim Agent MPI (University of Missouri - Nair Neural Engineering Laboratory - [Tyler Banks])"
        self.about_text = "Written for:\nProfessor Satish Nair's Neural Engineering Laboratory\nat The University of Missouri 2018\n\nDeveloped by: Tyler Banks\n\nContributors:\nFeng Feng\nBen Latimer\nZiao Chen\n\nEmail tbg28@mail.missouri.edu with questions"
        self.warnings_text = "This program was written for testing purposes only.\nBy using this program you assume the risk of accidental data deletion, always backup your data.\nThe author(s) assume no liability for problems that may arise from using this program."
        self.window_size = '1580x725'
        self.default_status = "Status: Ready"
        self.status_timer = 4.0
        self.root.resizable(1,1)
        
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.root.title(self.window_title)
        self.root.geometry(self.window_size)
        self.threads = []
        
        #self.root.resizable(0,0)
        self.root.config(menu=self.menu_bar(self.root))
        
        self.app_status = tk.StringVar(self.root,'')
        self.reset_app_status()
        
        self.exitapp = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        page2 = ttk.Frame(nb)
        
        nb.add(page1, text='Manage Jobs')
        #nb.add(page2, text='Parametric Sweep')
        nb.add(page2, text='Parameter Tuning')
        
        #Alternatively you could do parameters_page(page1), but wouldn't get scrolling
        jobs_page = self.bind_page(page1, Jobs_Page)
        #para_sweep_page = self.bind_page(page2, PS_Page)
        tuning_page = self.bind_page(page2, Tuning_Page)
        
        self.sim_load = "./SimAgentMPI/Models/100CellLa/"
        self.sim_load = os.path.abspath(self.sim_load)
        
        #jobs_page.force_use_directory("C:\\Users\\Tyler\\Desktop\\CG - Jing\\GC-lv123-newest\\CG Code\\HOC Code")
        jobs_page.set_threads(self.threads)
        #para_sweep_page.set_threads(self.threads)
        
        self.threads.append(jobs_page.start_refresh_thread())
        #self.threads.append(para_sweep_page.start_refresh_thread())
        
        self.display_app_status("Ready")
                
        return
    
    def show(self):
        try:
            print('Load complete. Running...')
            self.root.mainloop()
        except Exception:
            print('Error, closing display loop')
        print('Closing.\n')
        
    def on_closing(self,noprompt=False):
        if messagebox.askokcancel("Quit", "Do you want to quit? All running remote jobs will continue to run."):
            self.exitapp = True
            self.root.destroy()
            self.stop_threads()
            
    def stop_threads(self):
        print("stopping threads")
        main_thread = threading.currentThread()
        for t in self.threads:
            if t is not main_thread:
                print('joining {} (If this task hangs a job may be uploading/downloding results. Please wait to exit cleanly.)'.format(t.getName()))
                t.stop()
                t.join()
                print('joined {}'.format(t.getName()))
        print("stopping threads complete")
        
            
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
        r = gen_frame(f)
        r.pack()
        frame.update()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        return r
    
    def reset_app_status(self):
        self.app_status.set(self.default_status)
        #pass

    def display_app_status(self,str):
        self.app_status.set("Status: "+str)
        #threading.Timer(4.0, self.reset_app_status).start()
        
    def menu_bar(self, root):
            
        menubar = tk.Menu(root)
        
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        #filemenu.add_separator()
        filemenu.add_command(label="Generate a Batch File Template", command=self.generate_batch_template)
        #filemenu.add_command(label="Create New Batch File", command=self.create_batch)#half baked experiment
        filemenu.add_separator()
        #filemenu.add_command(label="Add Results Folder to .gitignore", command=self.add_to_git_ignore)
        filemenu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)
        
        servermenu = tk.Menu(menubar, tearoff=0)
        servermenu.add_command(label="Add Server", command=self.add_server)
        servermenu.add_command(label="Edit Server", command=self.edit_server)
        servermenu.add_command(label="Delete Server", command=self.delete_server)
        servermenu.add_separator()
        servermenu.add_command(label="Delete All Jobs on a Server", command=self.delete_all_jobs_server)
        menubar.add_cascade(label='Servers', menu=servermenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Update", command=self.update_from_github)
        helpmenu.add_command(label="Warnings", command=self.warning)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        return menubar
    
    def update_from_github(self):
        def update_call():
            messagebox.showinfo("Restart Sim Agent MPI", "Sim Agent has been successfully updated. Sim Agent MPI will now close, please restart")
            self.on_closing()
        UpdateWindow(self.root,callback=update_call)
        return
    
    def add_server(self):
        ServerEntryBox(self.root)#,server_id="180521092555")
        
    def edit_server_callback(self, s):
        if s.confirm and s.server_selected.get() != "":
            ServerEntryBox(self.root,server_id=s.server_selected.get())
            
    def edit_server(self):
        SelectServerEditBox(self.root, callback=self.edit_server_callback)
        
    def delete_server_callback(self, s):
        if s.confirm and s.server_selected.get() != "":
            server = s.server_selected.get()
            if (messagebox.askquestion("Delete Server", "Are you sure you want to delete the server entry \""+server+"\"?", icon='warning') == 'yes'):
                servers = ServersFile()
                servers.delete_server(server)
                return
        return
        
    def delete_server(self):
        SelectServerEditBox(self.root, callback=self.delete_server_callback)
        return

    def delete_all_jobs_server_callback(self, s):
        if s.confirm and s.server_selected.get() != "":
            server = s.server_selected.get()
            if (messagebox.askquestion("Delete Server Jobs", "Are you sure you want to delete all remote jobs on server connection \""+server+"\"?", icon='warning') == 'yes'):
                if (messagebox.askquestion("Delete Server Jobs", "Are you absolutely sure? This cannot be undone and may take a moment.", icon='warning') == 'yes'):
                    servers = ServersFile()
                    server = servers.get_server_byname(server)
                    ServerInterface().delete_all_remote_results(server)
        return
    
    def delete_all_jobs_server(self):
        SelectServerEditBox(self.root, callback=self.delete_all_jobs_server_callback)
        return       
            
    def about(self):
        messagebox.showinfo("About", self.about_text, icon='info')
        
    def warning(self):
        messagebox.showinfo("Warning", self.warnings_text, icon='info')
        
    """ General Tools """
    def create_batch(self):
        Create_Batch_File(self.root)
        
    def generate_batch_template(self):
        #init_dir = None
        #if self.dir_loader.sim_dir:
        #    init_dir = self.dir_loader.sim_dir.sim_directory
        bat = filedialog.asksaveasfilename(defaultextension=".sh", confirmoverwrite=True)#initialdir=init_dir,)
        try:
            Batch_File(bat).write_demo()
        except Exception as e:
            messagebox.showerror("Error", "Unable to write " + bat + "\n" + e)
        return
    
class Row(tk.Frame):
        def __init__(self, parent, *args, **kwargs):
            tk.Frame.__init__(self, parent, *args, **kwargs)
            self.parent = parent
            self.root = tk.Frame(self.parent)
            return
        
        def configure(self, file_name, variable, search_for, comment):
            self.v_value = tk.StringVar(self.root)
            self.original_value = tk.StringVar(self.root)
            
            line = SimAgentMPI.Utils.get_line_with(file_name,search_for)
            if line:
                line = line.replace(search_for,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                self.original_value.set(line)
                self.v_value.set(line)
                self.v_value.trace("w", self.save_)
             
            #self.v_value.set(variable)#Not correct
            
            self.search_for = search_for
            
            self.file_name = file_name
            
            frame = tk.Frame(self.root)
            var = tk.Label(frame, text="{} ({})".format(variable,os.path.basename(file_name)) ,width=30,background='light gray',anchor=tk.W)
            var.config(relief=tk.GROOVE)
            var.grid(column=0, row=0, padx=5, sticky='WE') 
            
            val = tk.Entry(frame,textvariable=self.v_value,width=50)
            val.grid(column=1, row=0, sticky='E')
            
            but = tk.Button(frame,text="Reset", command=self.reset)
            but.grid(column=2, row=0, sticky='WE')
            
            CreateToolTip(var,comment)
            frame.pack()
            #self.root.grid(row=0, column=0)
            return self
        
        def pack(self,*args,**kwargs):
            super(Row,self).pack(*args,**kwargs)
            self.root.pack(*args,**kwargs)
        
        def grid(self,*args,**kwargs):
            super(Row,self).grid(*args,**kwargs)
            self.root.grid(*args,**kwargs)
            
        def reset(self, *args):
            self.v_value.set(self.original_value.get())
            return
        def save_(self, *args):
            #SimAgentMPI.Utils.replace(self.file_name, "#SBATCH -p " + "(.*)", "{}{}".format("#SBATCH -p ", simjob.server_mpi_partition),unix_end=True)
            SimAgentMPI.Utils.replace(self.file_name, self.search_for + "(.*)", "{}{}".format(self.search_for, self.v_value.get()),unix_end=True)
    

class Tuning_Page(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.threads = None
        self.sim_load = "./SimAgentMPI/Models/100CellLa/"
        self.sim_load = os.path.abspath(self.sim_load)
        self.create_widgets()
        return
        
    def create_widgets(self):
        self.left_frame = tk.Frame(self.root)
        
        params_frame = tk.LabelFrame(self.left_frame,text="Parameters")
                
        Row(params_frame).configure(os.path.join(self.sim_load,"main.hoc"), "tstop", "tstop = ", "tstop").grid(row=0,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"bg2pyr.mod"), "initW", "\tinitW = ", "Background to pyramidal initial weights").grid(row=1,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"bg2inter.mod"), "initW", "\tinitW = ", "Background to interneuron initial weights").grid(row=2,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"tone2pyrD_new.mod"), "initW", "\tinitW = ", "Tone to pyramidal initial weights").grid(row=3,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"tone2interD_new.mod"), "initW", "\tinitW = ", "Tone to interneuron initial weights").grid(row=4,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"pyrD2pyrD_STFD_new.mod"), "initW", "\tinitW = ", "Pyramidal to pyramidal initial weights").grid(row=5,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"pyrD2interD_STFD.mod"), "initW", "\tinitW = ", "Background to Interneurons initial weights").grid(row=6,pady=10)
        Row(params_frame).configure(os.path.join(self.sim_load,"interD2pyrD_STFD_new.mod"), "initW", "\tinitW = ", "Interneurons to pyramidal initial weights").grid(row=7,pady=10)
        
        params_frame.grid(row=0,column=0,rowspan=100)
        self.left_frame.grid(row=0,column=0)
        return
    
    def pack(self,*args,**kwargs):
        super(Tuning_Page,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Tuning_Page,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)
    
    
class Jobs_Page(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.threads = None
        self.create_widgets()
        return
    
    def create_widgets(self):
        self.left_frame = tk.Frame(self.root)
        self.right_frame = tk.Frame(self.root)
        self.jobs_frame = tk.LabelFrame(self.left_frame, text="Jobs")
        self.directory_frame = tk.LabelFrame(self.left_frame, text="Project Directory")
        self.notes_frame = tk.LabelFrame(self.right_frame, text="Job Notes")
        self.log_frame = tk.Frame(self.right_frame)
        
        button_width = 15
        
        """=Note Frame======================================"""
        
        self.notes = Job_Notes(self.notes_frame)
        self.notes.grid(column=0,row=0)
        
        """=Logs Frame======================================"""
        
        self.consoles = Job_Consoles(self.log_frame)
        self.consoles.grid(column=0,row=0)
        
        """=Jobs Frame======================================"""
        
        self.table = Job_Table(self.jobs_frame, None, button_width=button_width,job_notes=self.notes,job_consoles=self.consoles)#on_select_row=self.display_job_notes_log,on_update_row=self.display_job_notes_log)
        self.table.grid(column=0,row=0)
        
        """=Dir Frame======================================="""
        
        def load_callback(sim_dir):
            self.table.reload_table(dir_=sim_dir)
        self.dir_loader = Dir_Loader(self.directory_frame, on_load_callback=load_callback, button_width=button_width)
        self.dir_loader.grid(column=0,row=0)
        
        
        """================================================="""
        
        self.left_frame.grid(column=0,row=0,sticky='news')
        self.right_frame.grid(column=1,row=0,sticky='news')
        
        self.directory_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5,columnspan=2)
        self.jobs_frame.grid(column=0,row=1,sticky='news',padx=5,pady=5,columnspan=2)
        
        self.log_frame.grid(column=0,row=0,sticky='news',padx=0,pady=5)
        self.notes_frame.grid(column=0,row=1,sticky='news',padx=5,pady=5)
                
        #self.start_refresh_thread()
        
        return
    
    def force_use_directory(self, dir_):
        self.dir_loader.force_use_directory(dir_)
        return self
    
    def set_threads(self,threads):
        self.threads = threads
        self.table.set_threads(self.threads)
    
    def start_refresh_thread(self):
        self.refresh_time = 60
        class RefreshThread(StoppableThread):
            def run(self):
                while not self.stopped():
                    #print("Update status thread running")
                    if(self.ref.dir_loader.sim_dir and self.ref.dir_loader.sim_dir.is_update_enabled()):
                        self.ref.dir_loader.sim_dir.update_all_jobs()
                        for i in range(self.ref.table.table.number_of_rows):
                           self.ref.table.update_row_info(row=i)
                    #print("sleeping for {} seconds".format(self.refresh_time))
                    for i in range(self.ref.refresh_time): #this is 60 seconds from when we're done updating everything
                        if self.stopped():
                            return
                        time.sleep(1) #use signals, fix later
                return
        
        refresh_thread = RefreshThread(ref=self)#Strongly untyped, be careful
        refresh_thread.setDaemon(True)
        refresh_thread.start()
        #self.threads.append(self.refresh_thread)
        return refresh_thread
                        
    def pack(self,*args,**kwargs):
        super(Jobs_Page,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Jobs_Page,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)
    
class Dir_Loader(tk.Frame):

    #def __init__(self, parent, job_table = None, button_width = 15, *args, **kwargs):
    def __init__(self, parent, on_load_callback = None, button_width = 15, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.on_load_callback = on_load_callback
        self.button_width = button_width
        self.sim_dir = None
        self.create_widgets()
        return
    
    def create_widgets(self):
        self.directory_frame = tk.Frame(self.root)
        self.b_select = tk.Button(self.directory_frame, text="Select Directory", command=lambda btn=True:self.load_dir(btn=btn), width=self.button_width)
        self.b_select.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
        
        self.sim_dir_var = tk.StringVar(self.root)
        self.sim_dir_var.set("Select a project folder to get started.")
        self.sim_dir_label = tk.Label(self.directory_frame, fg="blue",textvariable=self.sim_dir_var,anchor=tk.W,width=75)
        self.sim_dir_label.grid(column=1,row=0,sticky='news',padx=10,pady=5)
        
        #self.b_tool_exclude = tk.Button(self.directory_frame, text="Exclude Folders", command=self.exclude_folders_tool, width=self.button_width)
        #self.b_tool_exclude.grid(pady=5, padx=5, column=2, row=0, sticky="E")
        #self.b_tool_exclude.config(state=tk.DISABLED)
        
        self.b_git_exclude = tk.Button(self.directory_frame, text="Gitignore Results", command=self.add_to_git_ignore, width=self.button_width)
        self.b_git_exclude.grid(pady=5, padx=5, column=2, row=0, sticky="E")
        self.b_git_exclude.config(state=tk.DISABLED)
        
        #filemenu.add_command(label="Add Results Folder to .gitignore", command=self.add_to_git_ignore)#Original
        
        self.b_tool_edit = tk.Button(self.directory_frame, text="Edit Custom Tool", command=self.edit_dir_tool, width=self.button_width)
        self.b_tool_edit.grid(pady=5, padx=5, column=3, row=0, sticky="E")
        self.b_tool_edit.config(state=tk.DISABLED)
        
        self.update_status = tk.BooleanVar()
        self.b_update_check = tk.Checkbutton(self.directory_frame, text="Auto-Update", variable=self.update_status)
        self.b_update_check.grid(row=0,column=4, sticky="we")
        self.update_status.trace("w",self.update_button_enabled)
        self.b_update_check.config(state=tk.DISABLED)
        
        self.directory_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5,columnspan=2)
    
    def force_use_directory(self, dir_):
        self.load_dir(directory=dir_)
        self.b_select.config(state=tk.DISABLED)
    
    def update_button_enabled(self, *args):
        self.sim_dir.set_update_enabled(self.update_status.get())
        return    
    
    def exclude_folders_tool(self):
        return
    
    def edit_dir_tool(self):
        if self.sim_dir and self.sim_dir != "":
            Edit_dir_tool(self.root, self.sim_dir)
            
    def add_to_git_ignore(self):
        if not self.sim_dir:
            messagebox.showinfo("Add to .gitignore", "No directory selected")
            return
        if(messagebox.askquestion("Add to .gitignore", "Do you want to add \"" + SimDirectory.results_folder_name +"/\" to the .gitignore file in " + self.sim_dir.sim_directory + "? If a .gitignore does not exist one will be created.", icon='warning') == 'yes'):
            self.sim_dir.add_results_to_gitignore()
        return
            
    def load_dir(self, btn=False, directory=None):
        dir_ = None
        if not directory:
            if self.sim_dir and not btn:
                dir_ = self.sim_dir.sim_directory
            else:
                dir_ = filedialog.askdirectory()
        else:
            dir_ = directory
            
        if not dir_:
            return
        try:
            self.sim_dir = SimDirectory(dir_,initialize=True)
            self.sim_dir_var.set(self.sim_dir.sim_directory)
            self.update_status.set(self.sim_dir.is_update_enabled())
            #if self.job_table:
            #    self.job_table.reload_table(dir_=self.sim_dir)
            if self.on_load_callback:
                self.on_load_callback(self.sim_dir)
            self.b_git_exclude.config(state=tk.NORMAL)
            self.b_tool_edit.config(state=tk.NORMAL)
            self.b_update_check.config(state=tk.NORMAL)
            self.refresh_time = self.sim_dir.update_interval_seconds            
                
        except Exception as e:
            print(e)
        
        return
                 
    def pack(self,*args,**kwargs):
        super(Dir_Loader,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Dir_Loader,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)
        


class Job_Consoles(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.create_widgets()
        return
    
    def create_widgets(self):
        
        self.log_frame = tk.Frame(self.root)
        
        def log_file(root):
            self.log_console = tk.Text(root)
            self.log_console.config(width= 50, height=15, bg='black',fg='light green',state=tk.DISABLED)
            self.log_console.grid(column=0, row=0, padx=5, pady=5, sticky='NEWS')
        
        def stdout_file(root):
            self.log_console_stdout = tk.Text(root)
            self.log_console_stdout.config(width= 50, height=15, bg='black',fg='light green',state=tk.DISABLED)
            self.log_console_stdout.grid(column=0, row=0, padx=5, pady=5, sticky='NEWS')
            
        def stderr_file(root):
            self.log_console_stderr = tk.Text(root)
            self.log_console_stderr.config(width= 50, height=15, bg='black',fg='light green',state=tk.DISABLED)
            self.log_console_stderr.grid(column=0, row=0, padx=5, pady=5, sticky='NEWS')
            
        nb = Autoresized_Notebook(self.log_frame)
        nb.pack(padx=5,pady=5,side="left",fill="both",expand=True)
        
        #Alternatively you could do parameters_page(page1), but wouldn't get scrolling
        page1 = ttk.Frame(nb)
        nb.add(page1, text='Log File')
        log_file(page1)
        #self.bind_page(page1, log_file)
        
        page2 = ttk.Frame(nb)
        nb.add(page2, text='Server Output')
        stdout_file(page2)
        #self.bind_page(page2, stdout_file)
        
        page3 = ttk.Frame(nb)
        nb.add(page3, text='Server Error')
        stderr_file(page3)
        #self.bind_page(page3, stderr_file)
        
        self.log_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5)
    
    def display_job_log(self, job):
        if job != None:
            log = job.get_log()
            self.log_console.config(state=tk.NORMAL)
            self.log_console.delete('1.0', tk.END)
            self.log_console.insert(tk.END, log) 
            self.log_console.see("end")
            self.log_console.config(state=tk.DISABLED)
            
            log_stdout = job.get_log_stdout()
            self.log_console_stdout.config(state=tk.NORMAL)
            self.log_console_stdout.delete('1.0', tk.END)
            self.log_console_stdout.insert(tk.END, log_stdout) 
            self.log_console_stdout.see("end")
            self.log_console_stdout.config(state=tk.DISABLED)
            
            log_stderr = job.get_log_stderr()
            self.log_console_stderr.config(state=tk.NORMAL)
            self.log_console_stderr.delete('1.0', tk.END)
            self.log_console_stderr.insert(tk.END, log_stderr) 
            self.log_console_stderr.see("end")
            self.log_console_stderr.config(state=tk.DISABLED)
        return

    def clear(self):
        self.log_console.config(state=tk.NORMAL)
        self.log_console.delete('1.0', tk.END)
        self.log_console.config(state=tk.DISABLED)
        
        self.log_console_stdout.config(state=tk.NORMAL)
        self.log_console_stdout.delete('1.0', tk.END)
        self.log_console_stdout.config(state=tk.DISABLED)
        
        self.log_console_stderr.config(state=tk.NORMAL)
        self.log_console_stderr.delete('1.0', tk.END)
        self.log_console_stderr.config(state=tk.DISABLED)
    
    def pack(self,*args,**kwargs):
        super(Job_Consoles,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Job_Consoles,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)
        
        
class Job_Notes(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.create_widgets()
        return
    
    def create_widgets(self):
        self.notes_frame = tk.Frame(self.root)
        self.notes_console = tk.Text(self.notes_frame)
        self.notes_console.config(width= 50, height=18, bg='white',fg='black')
        self.notes_console.grid(column=0, row=0, padx=5, pady=5, sticky='NEWS')
        self.notes_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5)
    
    def display_job_notes(self, job):
        if job != None:
            notes = job.get_notes()
            self.notes_console.delete('1.0', tk.END)
            self.notes_console.insert(tk.END, notes)
        return
    
    def clear(self):
        self.notes_console.delete('1.0', tk.END)
        
    def write_notes(self,job):
        job.write_notes(self.notes_console.get("1.0",'end-1c'))
                
    def pack(self,*args,**kwargs):
        super(Job_Notes,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Job_Notes,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)
        

class Job_Table(tk.Frame):
    
    class Job_Button(enum.Enum):
        ALL = 1
        NEW = 2
        CLONE = 3 
        EDIT = 4
        START = 5
        STOP = 6
        UPDATE = 7
        OPENRESULTS = 8
        RUNCUSTOM = 9
        PROMOTE = 10
        DOWNLOAD = 11
        DELETEREMOTE = 12
        DELETELOCAL = 13
        
    def __init__(self, parent, sim_dir, button_width = 15, use_buttons=[Job_Button.ALL], job_notes=None,job_consoles=None,threads=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        
        self.columns = ["Status","Name", "Server", "Tool/Partition", "Nodes", "Cores", "Start", "Runtime", "Remote ID"]
        self.col_wid = [45, 200, 100, 100, 50, 50, 100, 100, 150]
        #https://timestamp.online/article/how-to-convert-timestamp-to-datetime-in-python
        self.date_format = '%b %d %y\n%I:%M %p'
        
        self.sim_dir = sim_dir
        self.button_width = button_width
        self.use_buttons = use_buttons
        self.job_notes = job_notes
        self.job_consoles = job_consoles
        self.threads = threads
        
        self.table = None
        
        self.selected_job_name = None
        
        try:
            #http://www.iconarchive.com/show/small-n-flat-icons-by-paomedia/sign-error-icon.html
            icon_dir = "./SimAgentMPI/icons"
            new = os.path.join(icon_dir,"sun-icon.png")
            check = os.path.join(icon_dir,"sign-check-icon.png")
            error = os.path.join(icon_dir,"sign-error-icon.png")
            sync = os.path.join(icon_dir,"sign-sync-icon.png")
            cloud_down = os.path.join(icon_dir, "cloud-down-icon.png")
    
            #Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
            self.new_img = ImageTk.PhotoImage(Image.open(new))
            self.check_img = ImageTk.PhotoImage(Image.open(check))
            self.error_img = ImageTk.PhotoImage(Image.open(error))
            self.sync_img  = ImageTk.PhotoImage(Image.open(sync))
            self.cloud_img = ImageTk.PhotoImage(Image.open(cloud_down))
            
        except Exception as e:
            print('Difficulty loading icons\n' + e)        
        
        self.create_widgets()
        
        return
            
    def create_widgets(self):
                
        button_width = self.button_width
        self.jobs_frame = tk.Frame(self.root)
        
        buttons_frame = tk.LabelFrame(self.jobs_frame, text="")        
        buttons_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        buttons_frame_inner_1 = tk.Frame(buttons_frame)        
        buttons_frame_inner_1.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        buttons_frame_inner_2 = tk.Frame(buttons_frame)        
        buttons_frame_inner_2.grid(column=0,row=1,sticky='news',padx=10,pady=5)
        
        b = Job_Table.Job_Button
        
        
        self.b_new = tk.Button(buttons_frame_inner_1, text="New Job", command=self.new_job, width=button_width,state=tk.DISABLED)
        if b.NEW in self.use_buttons or b.ALL in self.use_buttons:
            self.b_new.grid(pady=0, padx=5, column=1, row=0, sticky="WE")
        
        self.b_clone = tk.Button(buttons_frame_inner_1, text="Clone to New Job", command=self.clone_job, width=button_width,state=tk.DISABLED)
        if b.CLONE in self.use_buttons or b.ALL in self.use_buttons:
            self.b_clone.grid(pady=0, padx=5, column=2, row=0, sticky="WE")
        
        self.b_edit = tk.Button(buttons_frame_inner_1, text="Edit Job", command=self.edit_job, width=button_width,state=tk.DISABLED)
        if b.EDIT in self.use_buttons or b.ALL in self.use_buttons:
            self.b_edit.grid(pady=0, padx=5, column=3, row=0, sticky="WE")
        
        self.b_start = tk.Button(buttons_frame_inner_1, text="Start Job", command=self.start_job, width=button_width,state=tk.DISABLED)
        if b.START in self.use_buttons or b.ALL in self.use_buttons:
            self.b_start.grid(pady=0, padx=5, column=4, row=0, sticky="WE")
        
        self.b_stop = tk.Button(buttons_frame_inner_1, text="Stop Job", command=self.stop_job, width=button_width,state=tk.DISABLED)
        if b.STOP in self.use_buttons or b.ALL in self.use_buttons:
            self.b_stop.grid(pady=0, padx=5, column=5, row=0, sticky="WE")
        
        self.b_update = tk.Button(buttons_frame_inner_1, text="Update Status", command=self.update_job, width=button_width,state=tk.DISABLED)
        if b.UPDATE in self.use_buttons or b.ALL in self.use_buttons:
            self.b_update.grid(pady=0, padx=5, column=6, row=0, sticky="WE")
        
        self.b_open = tk.Button(buttons_frame_inner_1, text="Open Results Folder", command=self.open_job_folder, width=button_width,state=tk.DISABLED)
        if b.OPENRESULTS in self.use_buttons or b.ALL in self.use_buttons:
            self.b_open.grid(pady=0, padx=5, column=7, row=0, sticky="WE")
        
        self.b_run_cust = tk.Button(buttons_frame_inner_1, text="Run Custom Tool", command=self.run_custom, width=button_width,state=tk.DISABLED)
        if b.RUNCUSTOM in self.use_buttons or b.ALL in self.use_buttons:
            self.b_run_cust.grid(pady=0, padx=5, column=8, row=0, sticky="WE")
                
        #Row 2
                
        self.b_promote = tk.Button(buttons_frame_inner_2, text="Promote Results", command=self.promote_job_files, width=button_width,state=tk.DISABLED)
        if b.PROMOTE in self.use_buttons or b.ALL in self.use_buttons:
            self.b_promote.grid(pady=0, padx=5, column=3, row=0, sticky="WE") 
        
        self.b_down_remote = tk.Button(buttons_frame_inner_2, text="Re-Download Files", command=self.download_remote_files, width=button_width,state=tk.DISABLED)
        if b.DOWNLOAD in self.use_buttons or b.ALL in self.use_buttons:
            self.b_down_remote.grid(pady=0, padx=5, column=4, row=0, sticky="WE")
           
        self.b_del_remote = tk.Button(buttons_frame_inner_2, text="Delete Remote Files", command=self.delete_remote_files, width=button_width,state=tk.DISABLED)
        if b.DELETEREMOTE in self.use_buttons or b.ALL in self.use_buttons:
            self.b_del_remote.grid(pady=0, padx=5, column=5, row=0, sticky="WE")           
        
        self.b_del_all = tk.Button(buttons_frame_inner_2, text="Delete Job", command=self.delete_job_files, width=button_width,state=tk.DISABLED)
        if b.DELETELOCAL in self.use_buttons or b.ALL in self.use_buttons:
            self.b_del_all.grid(pady=0, padx=5, column=6, row=0, sticky="WE") 
            
         
        self.table = Table(self.jobs_frame, self.columns, column_minwidths=self.col_wid,height=400, onselect_method=self.select_row,text_to_img=self.get_status_image_dict())
        self.table.grid(row=1,column=0,padx=5,pady=10)
        self.table.set_data([[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""]])
        #table.cell(0,0, " This is testing a long sentence ")
        #table.insert_row([22,23,24])
        #table.insert_row([25,26,27],index=0)
        
        self.jobs_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5,columnspan=2)
    
    def set_threads(self,threads):
        self.threads = threads
        
    def select_row(self, row):
        if not self.sim_dir:
            return
        if(self.selected_job_name != "" and self.selected_job_name != None):
            job = self.sim_dir.get_job(self.selected_job_name)
            if job:
                if self.job_notes:
                    self.job_notes.write_notes(job)
                    
        self.selected_row_num = row
        if row != None:
            name_of_selected = str(self.table.row(row)[1])
        else:
            name_of_selected = ""
        
        job = None
        
        if name_of_selected == "":
            if self.job_consoles:
                self.job_consoles.clear()
            if self.job_notes:
                self.job_notes.clear()
        
        #if name_of_selected == self.selected_job_name:
        #    return
                
        if self.selected_job_name != None or (self.selected_job_name != name_of_selected and name_of_selected != ""): #selecting something different
            job = self.sim_dir.get_job(name_of_selected)
            if self.job_notes:
                self.job_notes.display_job_notes(job)
            if self.job_consoles:
                self.job_consoles.display_job_log(job)
            
        """
        ssh_status = ["SSH_sbatch_RUNNING","SSH_sbatch_COMPLETED","SSH_sbatch_DOWNLOADED","SSH_batch_CANCELLED"]
        nsg_status = ["NSG_RUNNING","NSG_COMPLETED","NSG_DOWNLOADED","NSG_CANCELLED"]
        """
        self.selected_job_name = name_of_selected
        if(self.selected_job_name != ""):
            self.b_clone.config(state=tk.NORMAL)
            self.b_del_all.config(state=tk.NORMAL)
                        
            if(job.status==SimJob.created_status or job.status==ServerInterface.ssh_status[3] or job.status==ServerInterface.nsg_status[3]):
                self.b_start.config(state=tk.NORMAL)
                self.b_edit.config(state=tk.NORMAL)
            else:
                self.b_start.config(state=tk.DISABLED)
                self.b_edit.config(state=tk.DISABLED)
                
            if(job.status==ServerInterface.ssh_status[1] or job.status==ServerInterface.nsg_status[1] or job.status==ServerInterface.ssh_status[2] or job.status==ServerInterface.nsg_status[2] or job.status==ServerInterface.ssh_status[3] or job.status==ServerInterface.nsg_status[3]):
                self.b_del_remote.config(state=tk.NORMAL)
            else:
                self.b_del_remote.config(state=tk.DISABLED)
                
            if(job.status==ServerInterface.ssh_status[2] or job.status==ServerInterface.nsg_status[2]):
                self.b_open.config(state=tk.NORMAL)
                self.b_run_cust.config(state=tk.NORMAL)
                self.b_down_remote.config(state=tk.NORMAL)
                self.b_promote.config(state=tk.NORMAL)
            else:
                self.b_open.config(state=tk.DISABLED)
                self.b_run_cust.config(state=tk.DISABLED)
                self.b_down_remote.config(state=tk.DISABLED)
                self.b_promote.config(state=tk.DISABLED)
            
            if(job.status==ServerInterface.ssh_status[0] or job.status==ServerInterface.nsg_status[0]):
                self.b_stop.config(state=tk.NORMAL)
                self.b_update.config(state=tk.NORMAL)
            else:
                self.b_stop.config(state=tk.DISABLED)
                self.b_update.config(state=tk.DISABLED)
            
        else:
            self.b_clone.config(state=tk.DISABLED)
            self.b_edit.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_stop.config(state=tk.DISABLED)
            self.b_update.config(state=tk.DISABLED)
            self.b_open.config(state=tk.DISABLED)
            self.b_run_cust.config(state=tk.DISABLED)
            self.b_promote.config(state=tk.DISABLED)
            self.b_down_remote.config(state=tk.DISABLED)
            self.b_del_remote.config(state=tk.DISABLED)
            self.b_del_all.config(state=tk.DISABLED)
      
        #print(str(self.table.row(row)))
    
    def new_job(self):
        JobEntryBox(self.root, self.sim_dir, oncomplete_callback=self.reload_table)
    
    def clone_job(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        JobEntryBox(self.root, self.sim_dir, oncomplete_callback=self.reload_table, edit_job=job, clone_mode=True)
        return
    
    def edit_job(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        JobEntryBox(self.root, self.sim_dir, oncomplete_callback=self.update_row_info, edit_job=job)
        return
        
    def start_job(self):
                
        class StartJobThread(StoppableThread):
            def run(self):
                job.status == ServerInterface.ssh_status[0]
                job.write_properties()
                self.ref.update_row_info()
                job.run()
                self.ref.update_row_info()
                return
        
        job = self.sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Start Job", "Are you sure you want to start this job?\n\nAll files in " + self.sim_dir.sim_directory + " will be uploaded to your selected server and the selected file will run. The display may freeze for a few moments.", icon='warning') == 'yes'):
            start_thread = StartJobThread(ref=self)
            start_thread.setDaemon(True)
            if self.threads:
                self.threads.append(start_thread)
            start_thread.start()
        return
    
    def update_job(self):
        if(messagebox.askquestion("Update Job", "Do you want to manually update the status of this job? The display may freeze for a few as this action is not threaded.", icon='warning') == 'yes'):
            job = self.sim_dir.get_job(self.selected_job_name)
            job.update()
            self.update_row_info()
        return
        
    def stop_job(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Stop Job", "Are you sure you want to stop this job?", icon='warning') == 'yes'):
            job.stop()
            self.update_row_info()
        return
    
    def run_custom(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        job.run_custom()
        self.update_row_info()
        
    def delete_job_files(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Delete Remote Job Files", "Are you sure you want to delete this job? This action is irreversible and removes the files from your local disk. The files will remain on the server and you will have to delete the manually.", icon='warning') == 'yes'):  
            try:
                self.sim_dir.delete_job(job)
                self.reload_table()
            except Exception as e:
                messagebox.showerror("Error", "There was an error deleting job files:\n\n" + e)
        return
    
    def promote_callback(self):
        return
    
    def promote_job_files(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        Promote_Files_Window(self.root,job,callback = self.promote_callback)
        return
    
    def delete_remote_files(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Delete Remote Job Files", "Are you sure you want to delete the files on the remote server?", icon='warning') == 'yes'):
            job.delete_remote()
        return
    
    def download_remote_files(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Download Remote Job Files", "Are you sure you want to re-download the files on the remote server? This is usually done through the update process automatically. This will overwrite {} and files in the folder {}.\n\n Additionally, this task is NOT threaded and will lock the window until the download has completed.".format(job.file_resultszip, job.dir_results), icon='warning') == 'yes'):
            job.download_remote()
            self.update_row_info()
        return    
    
    def open_job_folder(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        job.open_sim_results_directory()
        return    
    
    def row_of_data(self,job):
        part_tool = ""
        server = job.get_server()
        if server:
            jobtype = server.type
            if jobtype == "ssh":
                part_tool = job.server_mpi_partition
            elif jobtype == "nsg":
                part_tool = job.server_nsg_tool
        else:
            part_tool = ""
            
        #datetime.datetime.fromtimestamp(float(str(time.time()))).strftime('%y%m%d-%H%M%S')
        #Out[22]: '180524-203332'
        timeofstart = ""
        if job.sim_start_time != "":
           timeofstart = datetime.datetime.fromtimestamp(float(job.sim_start_time)).strftime(self.date_format)
           
        timedif = ""
        try:
            if job.sim_last_update_time != "" and job.sim_start_time != "":
                _start = datetime.datetime.fromtimestamp(float(job.sim_start_time))
                _update = datetime.datetime.fromtimestamp(float(job.sim_last_update_time))
                elapse = _update - _start
                (m, s) = divmod(elapse.total_seconds(),60)
                (h, m) = divmod(m,60)
                (d, h) = divmod(h,24)
                if int(d) > 0:
                    timedif = timedif+"{}d ".format(int(d))
                if int(h) > 0:
                    timedif = timedif+"{}h ".format(int(h))
                if int(m) > 0:
                    timedif = timedif+"{}m ".format(int(m))
                if int(s) > 0:
                    timedif = timedif+"{}s".format(int(s))
                    
                #timedif = "{}d {}h {}m {}s".format(int(d),int(h),int(m),int(s))
                
        except Exception:
            pass #just blank timedif
        data = [job.status, job.sim_name, job.server_connector, part_tool , job.server_nodes, job.server_cores, timeofstart, timedif,job.server_remote_identifier]
        return data
    
    def reload_table(self, dir_=None):
        
        if dir_:
            self.sim_dir = dir_
        
        self.table.grid_forget()
        self.table = Table(self.jobs_frame, self.columns, column_minwidths=self.col_wid,height=400, onselect_method=self.select_row,text_to_img=self.get_status_image_dict())
        self.table.grid(row=1,column=0,padx=10,pady=10)
        #self.table.set_data([[""],[""],[""],[""]])
        self.sim_dir.sim_jobs.sort(key=lambda x: float(x.created), reverse=True)
        
        if len(self.sim_dir.sim_jobs):
            for job in self.sim_dir.sim_jobs:
                data = self.row_of_data(job)
                self.table.insert_row(data)#,index=0)
        else:
            self.table.set_data([[""],[""],[""],[""]])
        
        self.b_new.config(state=tk.NORMAL)
        
        self.select_row(None)
            
    def update_row_info(self, row=None):
        #print("update_row_info row: {}".format(row))
        #print("update_row_info self.selected_row_num: {}".format(self.selected_row_num))
        update_buttons = False
        if row == None:
            if self.selected_row_num is not None:
                row = self.selected_row_num
                update_buttons = True
        elif row == self.selected_row_num:
            update_buttons = True
            
        name_of_selected = str(self.table.row(row)[1])#If you move around the index of the name it will mess up
        job = self.sim_dir.get_job(name_of_selected)
        
        if not job:
            return
        
        job.read_properties()
        
        data = self.row_of_data(job)
        for i, c in enumerate(data):
            #print("updating row {} column {} with {}".format(row,i,c))
            self.table.cell(row,i,c)
        
        
        
        if update_buttons:
            if self.job_notes:
                self.job_notes.display_job_notes(job)
            if self.job_consoles:
                self.job_consoles.display_job_log(job)
            #self.display_job_notes_log(job) #refresh log too#ORIGINAL
            
            self.select_row(self.selected_row_num) #just to refresh the buttons
                
        return
    
    def get_status_image_dict(self):
        return {SimJob.created_status:self.new_img,
                ServerInterface.nsg_status[0]:self.sync_img,ServerInterface.nsg_status[1]:self.cloud_img,ServerInterface.nsg_status[2]:self.check_img,ServerInterface.nsg_status[3]:self.error_img,
                ServerInterface.ssh_status[0]:self.sync_img,ServerInterface.ssh_status[1]:self.cloud_img,ServerInterface.ssh_status[2]:self.check_img,ServerInterface.ssh_status[3]:self.error_img}        
        #The Label widget is a standard Tkinter widget used to display a text or image on the screen.
        #panel = tk.Label(window, image = img)    
    
    def pack(self,*args,**kwargs):
        super(Job_Table,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Job_Table,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)

            
class Edit_dir_tool(object):
    
    def __init__(self, parent, dir_):
        self.parent = parent
        self.dir_ = dir_
                 
        self.display()
        return
    
    def display(self, server_id=None):            
        top = self.top = tk.Toplevel(self.parent)
        top.geometry('300x140')
        top.resizable(0,0)
        
        self.tool = tk.StringVar(top)
        self.confirm = tk.BooleanVar(top)
        self.confirm.set(False)
        
        self.tool.set(self.dir_.custom_tool)
        
        l = tk.Label(top, text='Write the command as if you were executing\nfrom the project directory on your local machine.\nJobs will execute the command from their results\n directory. Threads are NOT joined back.',width=40)
        l.grid(row=0,column=0,pady=5,padx=5,columnspan=2,rowspan=2)
        
        l = tk.Label(top, text='Custom command',width=15, background='light gray')
        l.grid(row=2,column=0,pady=5,padx=5)
        l.config(relief=tk.GROOVE)
        
        self.name_e = tk.Entry(top,width=25,textvariable=self.tool)
        self.name_e.grid(row=2,column=1,padx=5)
        
        b = tk.Button(top, text="Ok", command=self.ok)
        b.grid(pady=5, padx=5, column=0, row=3, sticky="WE")
        
        b = tk.Button(top, text="Cancel", command=self.cancel)
        b.grid(pady=5, padx=5, column=1, row=3, sticky="WE")
        
        
    def is_valid(self):
        return True
    
    def ok(self):
            self.confirm.set(True)
            if(self.confirm.get() and self.is_valid()):
                self.dir_.custom_tool = self.tool.get()
                self.dir_.write_properties()
                self.top.destroy()
            else:
                messagebox.showinfo("Validation Error",self.valid_message)
                self.top.lift()
            
    def cancel(self):
        self.top.destroy()
        

class Promote_Files_Window(object):
    def __init__(self,root,job,callback):
        self.root = root
        self.job = job
        self.callback = callback
        #filez = filedialog.askopenfilenames(parent=root,title='Choose a file')
        #print(filez)
        messagebox.showinfo("Info","Function to be implemented. (copy results from the results folder to the parent folder)")
        return
    
class Exclude_Files_Window():
    def __init__(self,job,callback):
        self.job = job
        self.callback = callback
        return
    

class Parametric_Sweep_Managment(tk.Frame):

    def __init__(self, parent, on_load_callback = None, button_width= 15, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.on_load_callback = on_load_callback
        self.button_width = button_width
        
        self.sim_dir = None
        self.sweep_sim_dir = None
        
        self.create_widgets()
        return
    
    def create_widgets(self):
        root = self.root
        button_width = self.button_width
        
        #self.sweep_frame = tk.LabelFrame(self.root, text="Parameter Sweep")
            
        self.parametric_sweep_state = tk.StringVar(root)
        self.parametric_sweep_state.trace("w",self.ps_state_changed)
        self.ps = None
        self.sweep_picked_default = "<Select a Previous Sweep>"
        self.sweep_picked = tk.StringVar(root)
        self.reset_sweep_picked()
        self.sweep_choices = [""]
                
        
        self.buttons_frame_ps = tk.Frame(self.root)        
        self.buttons_frame_ps.grid(column=0,row=0,sticky='news',padx=5,pady=5)
        
        self.buttons_frame_inner_ps = tk.Frame(self.buttons_frame_ps)        
        self.buttons_frame_inner_ps.grid(column=0,row=0,sticky='news',padx=5,pady=5)
        
        #tk.Label(buttons_frame_inner_ps, text='Sweep',width=15, background='light gray',relief=tk.GROOVE).grid(row=1,column=0,pady=5,padx=5)
        self.b_new = tk.Button(self.buttons_frame_inner_ps, text="Create New Sweep", command=self.new_ps, width=button_width,state=tk.DISABLED)
        self.b_new.grid(pady=0, padx=5, column=0, row=1, sticky="WE")
        
        self.sweep_popupMenu = None
        self.reload_old_sweeps()
        
        self.b_load = tk.Button(self.buttons_frame_inner_ps, text="Load", command=self.load_ps, width=button_width,state=tk.DISABLED)
        self.b_load.grid(pady=0, padx=5, column=2, row=1, sticky="WE")
        
        self.b_delete = tk.Button(self.buttons_frame_inner_ps, text="Delete", command=self.delete_ps, width=button_width,state=tk.DISABLED)
        self.b_delete.grid(pady=0, padx=5, column=3, row=1, sticky="WE")
        
        
        buttons_frame_ps = tk.LabelFrame(self.root, text="")        
        buttons_frame_ps.grid(column=0,row=1,sticky='news',padx=5,pady=5)
        
        ps_buttons_frame_inner_1 = tk.Frame(buttons_frame_ps)        
        ps_buttons_frame_inner_1.grid(column=0,row=0,sticky='news',padx=5,pady=5)             
        
        self.b_edit = tk.Button(ps_buttons_frame_inner_1, text="Edit Sweep", command=self.edit_ps, width=button_width,state=tk.DISABLED)
        self.b_edit.grid(pady=0, padx=5, column=1, row=0, sticky="WE")
        
        self.b_build = tk.Button(ps_buttons_frame_inner_1, text="Build", command=self.build_ps, width=button_width,state=tk.DISABLED)
        self.b_build.grid(pady=0, padx=5, column=2, row=0, sticky="WE")
        
        self.b_decon = tk.Button(ps_buttons_frame_inner_1, text="Deconstruct", command=self.decon_ps, width=button_width,state=tk.DISABLED)
        self.b_decon.grid(pady=0, padx=5, column=3, row=0, sticky="WE")
        
        self.b_start = tk.Button(ps_buttons_frame_inner_1, text="Start Sweep", command=self.start_ps, width=button_width,state=tk.DISABLED)
        self.b_start.grid(pady=0, padx=5, column=4, row=0, sticky="WE")
        
        self.b_cancel = tk.Button(ps_buttons_frame_inner_1, text="Cancel Sweep", command=self.cancel_ps, width=button_width,state=tk.DISABLED)
        self.b_cancel.grid(pady=0, padx=5, column=5, row=0, sticky="WE")
                
        self.b_open = tk.Button(ps_buttons_frame_inner_1, text="Open Sweep Folder", command=self.open_sweep_folder, width=button_width,state=tk.DISABLED)
        self.b_open.grid(pady=0, padx=5, column=7, row=0, sticky="WE")
        
        self.b_run_cust = tk.Button(ps_buttons_frame_inner_1, text="Run Custom Tool", command=self.custom_run, width=button_width,state=tk.DISABLED)
        self.b_run_cust.grid(pady=0, padx=5, column=8, row=0, sticky="WE")

    def load_sweeps(self):
        self.sweep_choices.clear()
        self.sweep_choices.append("yep")
        return
    
    def reload_old_sweeps(self):
        if self.sweep_popupMenu:
            self.sweep_popupMenu.grid_forget()
        self.sweep_popupMenu = OptionMenu(self.buttons_frame_inner_ps, self.sweep_picked, *self.sweep_choices)
        self.sweep_popupMenu.config(width=75,state=tk.DISABLED)
        self.sweep_popupMenu.grid(row = 1, column =1, sticky='WE')
        self.sweep_picked.trace("w",self.on_sweep_changed)
        
    def set_current_sim_dir(self,sim_dir):
        self.sim_dir=sim_dir
        
        self.load_sweeps()
        self.reload_old_sweeps()
        self.reset_sweep_picked()
        
        self.sweep_popupMenu.config(state=tk.NORMAL)
        self.b_new.config(state=tk.NORMAL)
        
    def reset_sweep_picked(self):
        self.sweep_picked.set(self.sweep_picked_default)
    
    def new_ps(self):
        if self.sim_dir:
            self.ps = ParametricSweep(self.sim_dir,"testsweep",external_state_var=self.parametric_sweep_state)
        return
    
    def on_sweep_changed(self, *args):
        #print(self.sweep_picked.get())
        if self.sweep_picked.get() != "" and self.sweep_picked.get() != self.sweep_picked_default:
            self.b_load.config(state=tk.NORMAL)
            self.b_delete.config(state=tk.NORMAL)
            #self.load_ps() #IF YOU DON'T WANT TO MANUALLY RELOAD UNCOMMENT THIS
        else:
            self.b_load.config(state=tk.DISABLED)
            self.b_delete.config(state=tk.DISABLED)
            self.parametric_sweep_state.set("")
        
        return
    
    def load_ps(self):
        if self.sim_dir:
            if self.sweep_picked.get() != "" and self.sweep_picked.get() != self.sweep_picked_default:
                self.ps = ParametricSweep(self.sim_dir,self.sweep_picked.get(),external_state_var=self.parametric_sweep_state)
                if self.on_load_callback:
                    self.on_load_callback(SimDirectory(self.ps.sweep_dir_working,initialize=True))
            else:
                #clear all options/windows
                pass
        return
    
    def delete_ps(self):
        return
    
    def edit_ps(self):
        if self.ps:
            pass
        return
    
    def build_ps(self):
        if self.ps:
            self.ps.build()
        return
    
    def decon_ps(self):
        if self.ps:
            self.ps.deconstruct()
        return
    
    def start_ps(self):
        if self.ps:
            self.ps.submit()
        return
    
    def cancel_ps(self):
        if self.ps:
            self.ps.cancel()
        return
    
    def open_sweep_folder(self):
        return
    
    def custom_run(self):
        return
 
    '''
    
    (PS_CREATE) --(PS_BUILD)--> (PS_READY) --(PS_SUBMITTING) <-> (PS_RUNNING) --> (PS_COMPLETE)
          ^                         V                                V
          |<---(PS_DECONSTRUCT)-----|                                |
                       ^                                             |
                       |------ (PS_CANCELLED) <-- (PS_CANCELLING) ---|
          
    
    state = ["PS_CREATE", "PS_BUILD", "PS_READY", "PS_DECONSTRUCT",
             "PS_SUBMITTING", "PS_RUNNING", "PS_CANCELLING", "PS_CANCELLED",
             "PS_COMPLETE"]
    '''
    def ps_state_changed(self, *args):
        if self.parametric_sweep_state.get() == "":
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[0]:   #PS_CREATE
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.NORMAL)
            self.b_build.config(state=tk.NORMAL)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[1]: #PS_BUILD
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[2]: #PS_READY
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.NORMAL)
            self.b_start.config(state=tk.NORMAL)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[3]: #PS_DECONSTRUCT
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[4]: #PS_SUBMITTING
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.NORMAL)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[5]: #PS_RUNNING
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.NORMAL)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[6]: #PS_CANCELLING
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[7]: #PS_CANCELLED
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.NORMAL)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
            
        elif self.parametric_sweep_state.get() == ParametricSweep.state[8]: #PS_COMPLETE
            self.b_new.config(state=tk.NORMAL)
            self.b_edit.config(state=tk.DISABLED)
            self.b_build.config(state=tk.DISABLED)
            self.b_decon.config(state=tk.DISABLED)
            self.b_start.config(state=tk.DISABLED)
            self.b_cancel.config(state=tk.DISABLED)
        return
        
    def pack(self,*args,**kwargs):
        super(Parametric_Sweep_Managment,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(Parametric_Sweep_Managment,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)    

    
    
class PS_Page(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.root = tk.Frame(self.parent)
        self.threads = None
        self.create_widgets()
        return
    
    def create_widgets(self):
        self.left_frame = tk.Frame(self.root)
        self.right_frame = tk.Frame(self.root)
        
        self.directory_frame = tk.LabelFrame(self.left_frame, text="Project Directory")
        self.ps_frame = tk.LabelFrame(self.left_frame, text="Parametric Sweep")
        self.jobs_frame = tk.LabelFrame(self.left_frame, text="Sweep Jobs")
        self.ps_stats_frame = tk.LabelFrame(self.right_frame, text="Parameter Sweep Information")
        self.log_frame = tk.Frame(self.right_frame)
        
        button_width = 15
        
        """=PS Stats Frame======================================"""
        
        #self.notes = Job_Notes(self.notes_frame)
        #self.notes.grid(column=0,row=0)
        
        """=Logs Frame======================================"""
        
        self.consoles = Job_Consoles(self.log_frame)
        self.consoles.grid(column=0,row=0)
        
        """=Jobs Frame======================================"""
        b = Job_Table.Job_Button
        btns = [b.EDIT, b.START, b.STOP, b.UPDATE, b.OPENRESULTS, b.RUNCUSTOM]
        self.table = Job_Table(self.jobs_frame, None, use_buttons=btns,button_width=button_width,job_notes=None,job_consoles=self.consoles)#on_select_row=self.display_job_notes_log,on_update_row=self.display_job_notes_log)
        self.table.grid(column=0,row=0)
        
        
        """=PS Frame========================================"""
        def load_ps_callback(sim_dir):
            if sim_dir:
                self.table.reload_table(dir_=sim_dir)
            
        self.para_sweeper = Parametric_Sweep_Managment(self.ps_frame, on_load_callback=load_ps_callback, button_width=button_width)
        self.para_sweeper.grid(column=0,row=0)
        
        """=Dir Frame======================================="""
        
        def load_callback(sim_dir):
            if sim_dir:
                self.para_sweeper.set_current_sim_dir(sim_dir)
                self.para_sweeper.load_ps()
            
        self.dir_loader = Dir_Loader(self.directory_frame, on_load_callback=load_callback, button_width=button_width)
        self.dir_loader.grid(column=0,row=0)
        
        
        """================================================="""
        
        self.left_frame.grid(column=0,row=0,sticky='news')
        self.right_frame.grid(column=1,row=0,sticky='news')
        
        self.directory_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5,columnspan=2)
        self.ps_frame.grid(column=0,row=1,sticky='news',padx=5,pady=5,columnspan=2)
        self.jobs_frame.grid(column=0,row=2,sticky='news',padx=5,pady=5,columnspan=2)
        
        self.ps_stats_frame.grid(column=0,row=0,sticky='news',padx=5,pady=5)
        self.log_frame.grid(column=0,row=1,sticky='news',padx=0,pady=5)
        
        return
    
    def force_use_directory(self, dir_):
        self.dir_loader.force_use_directory(dir_)
        return self
    
    def set_threads(self,threads):
        self.threads = threads
        self.table.set_threads(self.threads)
        
    def start_refresh_thread(self):
        self.refresh_time = 60
        class RefreshThread(StoppableThread):
            def run(self):
                while not self.stopped():
                    #print("Update status thread running")
                    if(self.ref.dir_loader.sim_dir and self.ref.dir_loader.sim_dir.is_update_enabled()):
                        self.ref.dir_loader.sim_dir.update_all_jobs()
                        for i in range(self.ref.table.table.number_of_rows):
                           self.ref.table.update_row_info(row=i)
                    #print("sleeping for {} seconds".format(self.refresh_time))
                    for i in range(self.ref.refresh_time): #this is 60 seconds from when we're done updating everything
                        if self.stopped():
                            return
                        time.sleep(1) #use signals, fix later
                return
        
        refresh_thread = RefreshThread(ref=self)#Strongly untyped, be careful
        refresh_thread.setDaemon(True)
        refresh_thread.start()
        return refresh_thread
                        
    def pack(self,*args,**kwargs):
        super(PS_Page,self).pack(*args,**kwargs)
        self.root.pack(*args,**kwargs)
            
    def grid(self,*args,**kwargs):
        super(PS_Page,self).grid(*args,**kwargs)
        self.root.grid(*args,**kwargs)
    