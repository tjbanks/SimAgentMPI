# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
from SimAgentMPI.Utils import CreateToolTip, Autoresized_Notebook

import tkinter as tk
from tkinter import messagebox,ttk,filedialog,OptionMenu
from SimAgentMPI.tktable import Table
import datetime
from PIL import ImageTk, Image
import os, time

from SimAgentMPI.NewJobWindow import JobEntryBox, Create_Batch_File
from SimAgentMPI.NewServerConfig import ServerEntryBox,SelectServerEditBox
from SimAgentMPI.SimDirectory import SimDirectory
from SimAgentMPI.ServerInterface import ServerInterface
from SimAgentMPI.SimJob import SimJob
from SimAgentMPI.SimServer import ServersFile
from SimAgentMPI.Utils import Batch_File,StoppableThread
from SimAgentMPI.ParametricSweep import ParametricSweep

import threading

class MainWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.window_title = "Sim Agent MPI (University of Missouri - Nair Neural Engineering Laboratory - Tyler Banks)"
        self.about_text = "Written for:\nProfessor Satish Nair's Neural Engineering Laboratory\nat The University of Missouri 2018\n\nDeveloped by: Tyler Banks\n\nContributors:\nFeng Feng\nBen Latimer\nZiao Chen\n\nEmail tbg28@mail.missouri.edu with questions"
        self.warnings_text = "This program was written for testing purposes only.\nBy using this program you assume the risk of accidental data deletion, always backup your data.\nThe author(s) assume no liability for problems that may arise from using this program."
        self.sim_dir = None
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
        
        nb.add(page1, text='Single Jobs')
        #nb.add(page2, text='Parametric Sweep')
        
        #Alternatively you could do parameters_page(page1), but wouldn't get scrolling
        self.bind_page(page1, self.jobs_page)
        self.bind_page(page2, ParametricSweepPage)
        
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
        filemenu.add_command(label="Add Results Folder to .gitignore", command=self.add_to_git_ignore)
        menubar.add_cascade(label="File", menu=filemenu)
        
        servermenu = tk.Menu(menubar, tearoff=0)
        servermenu.add_command(label="Add Server", command=self.add_server)
        servermenu.add_command(label="Edit Server", command=self.edit_server)
        servermenu.add_command(label="Delete Server", command=self.delete_server)
        servermenu.add_separator()
        servermenu.add_command(label="Delete All Jobs on a Server", command=self.delete_all_jobs_server)
        menubar.add_cascade(label='Servers', menu=servermenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Warnings", command=self.warning)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        return menubar
    
    
    def jobs_page(self, root):
        #self.date_format = '%y%m%d-%H%M%S'
        #https://timestamp.online/article/how-to-convert-timestamp-to-datetime-in-python
        self.date_format = '%b %d %y\n%I:%M %p'
        #open project dir
        #print(filedialog.askdirectory())
        
        self.left_frame = tk.Frame(root)
        self.right_frame = tk.Frame(root)
        
        self.directory_frame = tk.LabelFrame(self.left_frame, text="Directory")
        self.jobs_frame = tk.LabelFrame(self.left_frame, text="Jobs")
        self.notes_frame = tk.LabelFrame(self.right_frame, text="Notes")
        self.log_frame = tk.Frame(self.right_frame)
        
        button_width = 15
        self.selected_job_name = None
        
        self.refresh_time = 60
        
        class RefreshThread(StoppableThread):
            def run(self):
                while not self.stopped():
                    #print("Update status thread running")
                    if(self.ref.sim_dir and self.ref.sim_dir.is_update_enabled()):
                        self.ref.sim_dir.update_all_jobs()
                        for i in range(self.ref.table.number_of_rows):
                           self.ref.update_row_info(row=i)
                    #print("sleeping for {} seconds".format(self.refresh_time))
                    for i in range(self.ref.refresh_time): #this is 60 seconds from when we're done updating everything
                        if self.stopped():
                            return
                        time.sleep(1) #use signals, fix later
                return
        
        
        self.refresh_thread = RefreshThread(ref=self)#Strongly untyped, be careful
        self.refresh_thread.setDaemon(True)
        self.refresh_thread.start()
        self.threads.append(self.refresh_thread)
        ###!!!self.refresh_periodically()
        
        
        b = tk.Button(self.directory_frame, text="Select Directory", command=lambda btn=True:self.load_dir(btn=btn), width=button_width)
        b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
        
        self.sim_dir_var = tk.StringVar(root)
        self.sim_dir_var.set("Select a project folder to get started.")
        self.sim_dir_label = tk.Label(self.directory_frame, fg="blue",textvariable=self.sim_dir_var,anchor=tk.W,width=75)
        self.sim_dir_label.grid(column=1,row=0,sticky='news',padx=10,pady=5)
        
        self.b_tool_exclude = tk.Button(self.directory_frame, text="Exclude Folders", command=self.exclude_folders_tool, width=button_width)
        self.b_tool_exclude.grid(pady=5, padx=5, column=2, row=0, sticky="E")
        self.b_tool_exclude.config(state=tk.DISABLED)
        
        self.b_tool_edit = tk.Button(self.directory_frame, text="Edit Custom Tool", command=self.edit_dir_tool, width=button_width)
        self.b_tool_edit.grid(pady=5, padx=5, column=3, row=0, sticky="E")
        self.b_tool_edit.config(state=tk.DISABLED)
        
        self.update_status = tk.BooleanVar()
        self.b_update_check = tk.Checkbutton(self.directory_frame, text="Auto-Update", variable=self.update_status)
        self.b_update_check.grid(row=0,column=4, sticky="we")
        self.update_status.trace("w",self.update_button_enabled)
        self.b_update_check.config(state=tk.DISABLED)
        """=Jobs Frame======================================"""
        
        buttons_frame = tk.LabelFrame(self.jobs_frame, text="")        
        buttons_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        buttons_frame_inner_1 = tk.Frame(buttons_frame)        
        buttons_frame_inner_1.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        buttons_frame_inner_2 = tk.Frame(buttons_frame)        
        buttons_frame_inner_2.grid(column=0,row=1,sticky='news',padx=10,pady=5)
        
        
        self.b_new = tk.Button(buttons_frame_inner_1, text="New Job", command=self.new_job, width=button_width,state=tk.DISABLED)
        self.b_new.grid(pady=0, padx=5, column=1, row=0, sticky="WE")
        
        self.b_clone = tk.Button(buttons_frame_inner_1, text="Clone to New Job", command=self.clone_job, width=button_width,state=tk.DISABLED)
        self.b_clone.grid(pady=0, padx=5, column=2, row=0, sticky="WE")
        
        self.b_edit = tk.Button(buttons_frame_inner_1, text="Edit Job", command=self.edit_job, width=button_width,state=tk.DISABLED)
        self.b_edit.grid(pady=0, padx=5, column=3, row=0, sticky="WE")
        
        self.b_start = tk.Button(buttons_frame_inner_1, text="Start Job", command=self.start_job, width=button_width,state=tk.DISABLED)
        self.b_start.grid(pady=0, padx=5, column=4, row=0, sticky="WE")
        
        self.b_stop = tk.Button(buttons_frame_inner_1, text="Stop Job", command=self.stop_job, width=button_width,state=tk.DISABLED)
        self.b_stop.grid(pady=0, padx=5, column=5, row=0, sticky="WE")
        
        self.b_update = tk.Button(buttons_frame_inner_1, text="Update Status", command=self.update_job, width=button_width,state=tk.DISABLED)
        self.b_update.grid(pady=0, padx=5, column=6, row=0, sticky="WE")
        
        self.b_open = tk.Button(buttons_frame_inner_1, text="Open Results Folder", command=self.open_job_folder, width=button_width,state=tk.DISABLED)
        self.b_open.grid(pady=0, padx=5, column=7, row=0, sticky="WE")
        
        self.b_run_cust = tk.Button(buttons_frame_inner_1, text="Run Custom Tool", command=self.run_custom, width=button_width,state=tk.DISABLED)
        self.b_run_cust.grid(pady=0, padx=5, column=8, row=0, sticky="WE")
        
        self.b_run_cust = tk.Button(buttons_frame_inner_1, text="Run Custom Tool", command=self.run_custom, width=button_width,state=tk.DISABLED)
        self.b_run_cust.grid(pady=0, padx=5, column=8, row=0, sticky="WE")
        
        #Exclude files/folder from upload
        #Delete remote
        #delete local/remote
        #Copy Select Results to Main
        
        #Row 2
        
        self.b_promote = tk.Button(buttons_frame_inner_2, text="Promote Results", command=self.promote_job_files, width=button_width,state=tk.DISABLED)
        self.b_promote.grid(pady=0, padx=5, column=3, row=0, sticky="WE") 
        
        self.b_down_remote = tk.Button(buttons_frame_inner_2, text="Re-Download Files", command=self.download_remote_files, width=button_width,state=tk.DISABLED)
        self.b_down_remote.grid(pady=0, padx=5, column=4, row=0, sticky="WE")
           
        self.b_del_remote = tk.Button(buttons_frame_inner_2, text="Delete Remote Files", command=self.delete_remote_files, width=button_width,state=tk.DISABLED)
        self.b_del_remote.grid(pady=0, padx=5, column=5, row=0, sticky="WE")           
        
        self.b_del_all = tk.Button(buttons_frame_inner_2, text="Delete Job", command=self.delete_job_files, width=button_width,state=tk.DISABLED)
        self.b_del_all.grid(pady=0, padx=5, column=6, row=0, sticky="WE") 
        
        
        
                
            
        self.columns = ["Status","Name", "Server", "Tool/Partition", "Nodes", "Cores", "Start", "Runtime", "Remote ID"]
        self.col_wid = [45, 200, 100, 100, 50, 50, 100, 100, 150]
        
        self.table = Table(self.jobs_frame, self.columns, column_minwidths=self.col_wid,height=400, onselect_method=self.select_row,text_to_img=self.get_status_image_dict())
        self.table.grid(row=1,column=0,padx=10,pady=10)
        self.table.set_data([[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""]])
        #table.cell(0,0, " a fdas fasd fasdf asdf asdfasdf asdf asdfa sdfas asd sadf ")
        #table.grid_propagate(False) #Is this really the only way to get it to a specific size?
            
        #table.insert_row([22,23,24])
        #table.insert_row([25,26,27],index=0)
        
        """=Note Frame======================================"""
        
        self.notes_console = tk.Text(self.notes_frame)
        self.notes_console.config(width= 50, height=18, bg='white',fg='black')
        self.notes_console.grid(column=0, row=0, padx=5, pady=5, sticky='NEWS')
        
        
        """=Logs Frame======================================"""
        
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
        
        
        
        """================================================="""
        
        
        self.left_frame.grid(column=0,row=0,sticky='news')
        self.right_frame.grid(column=1,row=0,sticky='news')
        
        self.directory_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5,columnspan=2)
        self.jobs_frame.grid(column=0,row=1,sticky='news',padx=10,pady=5,columnspan=2)
        self.notes_frame.grid(column=0,row=1,sticky='news',padx=10,pady=5)
        self.log_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        return
    
    def select_row(self, row):
        self.write_notes()
        self.selected_row_num = row
        if row != None:
            name_of_selected = str(self.table.row(row)[1])
        else:
            name_of_selected = ""
        
        job = None
        
        if name_of_selected == "":
            self.notes_console.delete('1.0', tk.END)
            self.log_console.config(state=tk.NORMAL)
            self.log_console.delete('1.0', tk.END)
            self.log_console.config(state=tk.DISABLED)
            
            self.log_console_stdout.config(state=tk.NORMAL)
            self.log_console_stdout.delete('1.0', tk.END)
            self.log_console_stdout.config(state=tk.DISABLED)
            
            self.log_console_stderr.config(state=tk.NORMAL)
            self.log_console_stderr.delete('1.0', tk.END)
            self.log_console_stderr.config(state=tk.DISABLED)
        
        #if name_of_selected == self.selected_job_name:
        #    return
                
        if self.selected_job_name != None or (self.selected_job_name != name_of_selected and name_of_selected != ""): #selecting something different
            job = self.sim_dir.get_job(name_of_selected)
            self.display_job_notes_log(job)
            
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
    
    def on_closing(self,noprompt=False):
        if not self.sim_dir or messagebox.askokcancel("Quit", "Do you want to quit? All running remote jobs will continue to run."):
            self.exitapp = True
            self.root.destroy()
            self.stop_threads()
    
    def stop_threads(self):
        print("stopping threads")
        main_thread = threading.currentThread()
        for t in self.threads:
            if t is not main_thread:
                print('joining {} (If this task hangs a job may be being downloaded)'.format(t.getName()))
                t.stop()
                t.join()
                print('joined {}'.format(t.getName()))
        print("stopping threads complete")
                
    def update_button_enabled(self, *args):
        self.sim_dir.set_update_enabled(self.update_status.get())
        return
    
    def create_batch(self):
        Create_Batch_File(self.root)
        
    def generate_batch_template(self):
        init_dir = None
        if self.sim_dir:
            init_dir = self.sim_dir.sim_directory
        bat = filedialog.asksaveasfilename(defaultextension=".sh", initialdir=init_dir, confirmoverwrite=True)
        try:
            Batch_File(bat).write_demo()
        except Exception as e:
            messagebox.showerror("Error", "Unable to write " + bat + "\n" + e)
        return
        
    def add_to_git_ignore(self):
        if not self.sim_dir:
            messagebox.showinfo("Add to .gitignore", "No directory selected")
            return
        if(messagebox.askquestion("Add to .gitignore", "Do you want to add \"" + SimDirectory.results_folder_name +"/\" to the .gitignore file in " + self.sim_dir.sim_directory + "? If a .gitignore does not exist one will be created.", icon='warning') == 'yes'):
            self.sim_dir.add_results_to_gitignore()
        return
            
    def display_job_notes_log(self, job):
        if job != None:
            self.display_job_notes(job)
            self.display_job_log(job)
            
    def display_job_notes(self, job):
        if job != None:
            notes = job.get_notes()
            self.notes_console.delete('1.0', tk.END)
            self.notes_console.insert(tk.END, notes)
        return
            
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
    
    def write_notes(self):
        if(self.selected_job_name != "" and self.selected_job_name != None):
            job = self.sim_dir.get_job(self.selected_job_name)
            if job:
                job.write_notes(self.notes_console.get("1.0",'end-1c'))
                
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
        
    def exclude_folders_tool(self):
        return
    
    def edit_dir_tool(self):
        if self.sim_dir and self.sim_dir != "":
            Edit_dir_tool(self.root, self.sim_dir)
            
    def run_custom(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        job.run_custom()
        self.update_row_info()
        
            
    def about(self):
        messagebox.showinfo("About", self.about_text, icon='info')
        
    def warning(self):
        messagebox.showinfo("Warning", self.warnings_text, icon='info')
            
    def new_job(self):
        JobEntryBox(self.root, self.sim_dir, oncomplete_callback=self.reload_table)
    
    def clone_job(self):
        job = self.sim_dir.get_job(self.selected_job_name)
        JobEntryBox(self.root, self.sim_dir, oncomplete_callback=self.load_dir, edit_job=job, clone_mode=True)
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
    
    def load_dir(self, btn=False, dir_=None):
        dir_ = None
        if self.sim_dir and not btn:
            dir_ = self.sim_dir.sim_directory
        else:
            dir_ = filedialog.askdirectory()
        if not dir_:
            return
        try:
            
            self.sim_dir = SimDirectory(dir_,initialize=True)
            self.sim_dir_var.set(self.sim_dir.sim_directory)
            self.update_status.set(self.sim_dir.is_update_enabled())
            self.reload_table()         
                
            self.b_new.config(state=tk.NORMAL)
            self.b_tool_edit.config(state=tk.NORMAL)
            self.b_update_check.config(state=tk.NORMAL)
            
            self.refresh_time = self.sim_dir.update_interval_seconds            
                
        except Exception as e:
            print(e)
        
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
    
    def reload_table(self):
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
            
        self.select_row(None)
            
    def update_row_info(self, row=None):
        #print("update_row_info row: {}".format(row))
        #print("update_row_info self.selected_row_num: {}".format(self.selected_row_num))
        if row == None:
            if self.selected_row_num is not None:
                row = self.selected_row_num
            
        name_of_selected = str(self.table.row(row)[1])#If you move around the index of the name it will mess up
        job = self.sim_dir.get_job(name_of_selected)
        job.read_properties()
        
        data = self.row_of_data(job)
        for i, c in enumerate(data):
            #print("updating row {} column {} with {}".format(row,i,c))
            self.table.cell(row,i,c)
        
        self.display_job_notes_log(job) #refresh log too
        self.select_row(self.selected_row_num) #just to refresh the buttons
                
        return
    
    def get_status_image_dict(self):
        return {SimJob.created_status:self.new_img,
                ServerInterface.nsg_status[0]:self.sync_img,ServerInterface.nsg_status[1]:self.cloud_img,ServerInterface.nsg_status[2]:self.check_img,ServerInterface.nsg_status[3]:self.error_img,
                ServerInterface.ssh_status[0]:self.sync_img,ServerInterface.ssh_status[1]:self.cloud_img,ServerInterface.ssh_status[2]:self.check_img,ServerInterface.ssh_status[3]:self.error_img}        
        #The Label widget is a standard Tkinter widget used to display a text or image on the screen.
        #panel = tk.Label(window, image = img)
        return
            
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
    

class ParametricSweepPage(object):

    def __init__(self, root):
        
        button_width = 15
        
        self.root = root
        self.left_frame = tk.Frame(root)
        self.right_frame = tk.Frame(root)
        
        self.directory_frame = tk.LabelFrame(self.left_frame, text="Directory")
        self.sweep_frame = tk.LabelFrame(self.left_frame, text="Parameter Sweep")
        self.jobs_frame = tk.LabelFrame(self.left_frame, text="Sweep Jobs")
        self.notes_frame = tk.LabelFrame(self.right_frame, text="Notes")
        self.log_frame = tk.Frame(self.right_frame)
        
        self.sim_dir = None
        self.sweep_sim_dir = None
        self.selected_job_name = None
        self.selected_row_num = None
        
        
        self.parametric_sweep_state = tk.StringVar(root)
        self.parametric_sweep_state.trace("w",self.ps_state_changed)
        self.ps = None
        self.sweep_picked_default = "<Select a Previous Sweep>"
        self.sweep_picked = tk.StringVar(root)
        self.reset_sweep_picked()
        self.sweep_choices = [""]
        
        self.refresh_time = 60
        
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
        
        #======================================================================
        
        b = tk.Button(self.directory_frame, text="Select Directory", command=lambda btn=True:self.load_dir(btn=btn), width=button_width)
        b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
        
        self.sim_dir_var = tk.StringVar(root)
        self.sim_dir_var.set("Under development.")
        tk.Label(self.directory_frame, fg="blue",textvariable=self.sim_dir_var,anchor=tk.W,width=75).grid(column=1,row=0,columnspan=3)
        
        self.b_tool_exclude = tk.Button(self.directory_frame, text="Exclude Folders", command=self.exclude_folders_tool, width=button_width)
        self.b_tool_exclude.grid(pady=5, padx=5, column=4, row=0, sticky="E")
        self.b_tool_exclude.config(state=tk.DISABLED)
        
        self.b_tool_edit = tk.Button(self.directory_frame, text="Edit Custom Tool", command=self.edit_dir_tool, width=button_width)
        self.b_tool_edit.grid(pady=5, padx=5, column=5, row=0, sticky="E")
        self.b_tool_edit.config(state=tk.DISABLED)
        
        self.update_status = tk.BooleanVar()
        self.b_update_check = tk.Checkbutton(self.directory_frame, text="Auto-Update", variable=self.update_status)
        self.b_update_check.grid(row=0,column=6, sticky="we")
        self.update_status.trace("w",self.update_button_enabled)
        self.b_update_check.config(state=tk.DISABLED)
        
        
        self.buttons_frame_ps = tk.LabelFrame(self.sweep_frame, text="")        
        self.buttons_frame_ps.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        self.buttons_frame_inner_ps = tk.Frame(self.buttons_frame_ps)        
        self.buttons_frame_inner_ps.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        #tk.Label(buttons_frame_inner_ps, text='Sweep',width=15, background='light gray',relief=tk.GROOVE).grid(row=1,column=0,pady=5,padx=5)
        self.b_new = tk.Button(self.buttons_frame_inner_ps, text="Create New Sweep", command=self.new_ps, width=button_width,state=tk.DISABLED)
        self.b_new.grid(pady=0, padx=5, column=0, row=1, sticky="WE")
        
        self.sweep_popupMenu = None
        self.reload_old_sweeps()
        
        self.b_load = tk.Button(self.buttons_frame_inner_ps, text="Load", command=self.load_ps, width=button_width,state=tk.DISABLED)
        self.b_load.grid(pady=0, padx=5, column=2, row=1, sticky="WE")
        
        self.b_delete = tk.Button(self.buttons_frame_inner_ps, text="Delete", command=self.delete_ps, width=button_width,state=tk.DISABLED)
        self.b_delete.grid(pady=0, padx=5, column=3, row=1, sticky="WE")
        
        
        
        buttons_frame_ps = tk.LabelFrame(self.sweep_frame, text="")        
        buttons_frame_ps.grid(column=0,row=1,sticky='news',padx=10,pady=5)
        
        ps_buttons_frame_inner_1 = tk.Frame(buttons_frame_ps)        
        ps_buttons_frame_inner_1.grid(column=0,row=0,sticky='news',padx=10,pady=5)             
        
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
        
        
        
        
        job_buttons_frame = tk.LabelFrame(self.jobs_frame, text="")        
        job_buttons_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        job_buttons_frame_inner_1 = tk.Frame(job_buttons_frame)        
        job_buttons_frame_inner_1.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
        
                
        self.bj_edit = tk.Button(job_buttons_frame_inner_1, text="Edit Job", command=self.edit_job, width=button_width,state=tk.DISABLED)
        self.bj_edit.grid(pady=0, padx=5, column=3, row=0, sticky="WE")
        
        self.bj_start = tk.Button(job_buttons_frame_inner_1, text="Re-Start Job", command=self.start_job, width=button_width,state=tk.DISABLED)
        self.bj_start.grid(pady=0, padx=5, column=4, row=0, sticky="WE")
        
        self.bj_stop = tk.Button(job_buttons_frame_inner_1, text="Stop Job", command=self.stop_job, width=button_width,state=tk.DISABLED)
        self.bj_stop.grid(pady=0, padx=5, column=5, row=0, sticky="WE")
        
        self.bj_update = tk.Button(job_buttons_frame_inner_1, text="Update Status", command=self.update_job, width=button_width,state=tk.DISABLED)
        self.bj_update.grid(pady=0, padx=5, column=6, row=0, sticky="WE")
        
        self.bj_open = tk.Button(job_buttons_frame_inner_1, text="Open Results Folder", command=self.open_job_folder, width=button_width,state=tk.DISABLED)
        self.bj_open.grid(pady=0, padx=5, column=7, row=0, sticky="WE")
        
        self.bj_run_cust = tk.Button(job_buttons_frame_inner_1, text="Run Custom Tool", command=self.run_custom, width=button_width,state=tk.DISABLED)
        self.bj_run_cust.grid(pady=0, padx=5, column=8, row=0, sticky="WE")
        
        
        self.columns = ["Status","Name", "Server", "Tool/Partition", "Nodes", "Cores", "Start", "Runtime", "Remote ID"]
        self.col_wid = [45, 200, 100, 100, 50, 50, 100, 100, 150]
        
        self.table = Table(self.jobs_frame, self.columns, column_minwidths=self.col_wid,height=400, onselect_method=self.select_row,text_to_img=self.get_status_image_dict())
        self.table.grid(row=1,column=0,padx=10,pady=10)
        self.table.set_data([[""],[""],[""],[""]])
        
        
        #======================================================================
        
        
        """=Logs Frame======================================"""
        
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
        nb.add(page1, text='Job Log File')
        log_file(page1)
        #self.bind_page(page1, log_file)
        
        page2 = ttk.Frame(nb)
        nb.add(page2, text='Job Server Output')
        stdout_file(page2)
        #self.bind_page(page2, stdout_file)
        
        page3 = ttk.Frame(nb)
        nb.add(page3, text='Job Server Error')
        stderr_file(page3)
        #self.bind_page(page3, stderr_file)
        
        
        
        """================================================="""
        
        
        
        self.left_frame.grid(column=0,row=0,sticky='news')
        self.right_frame.grid(column=1,row=0,sticky='news')
        
        self.directory_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5,columnspan=2)
        self.sweep_frame.grid(column=0,row=1,sticky='news',padx=10,pady=5,columnspan=2)
        self.jobs_frame.grid(column=0,row=2,sticky='news',padx=10,pady=5,columnspan=2)
        self.notes_frame.grid(column=0,row=1,sticky='news',padx=10,pady=5)
        self.log_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        
    def reload_old_sweeps(self):
        if self.sweep_popupMenu:
            self.sweep_popupMenu.grid_forget()
        self.sweep_popupMenu = OptionMenu(self.buttons_frame_inner_ps, self.sweep_picked, *self.sweep_choices)
        self.sweep_popupMenu.config(width=75,state=tk.DISABLED)
        self.sweep_popupMenu.grid(row = 1, column =1, sticky='WE')
        self.sweep_picked.trace("w",self.on_sweep_changed)
        
    def select_row(self, row):
        self.selected_row_num = row
        if row != None:
            name_of_selected = str(self.table.row(row)[1])
        else:
            name_of_selected = ""
        
        job = None
        
        if name_of_selected == "":
            self.log_console.config(state=tk.NORMAL)
            self.log_console.delete('1.0', tk.END)
            self.log_console.config(state=tk.DISABLED)
            
            self.log_console_stdout.config(state=tk.NORMAL)
            self.log_console_stdout.delete('1.0', tk.END)
            self.log_console_stdout.config(state=tk.DISABLED)
            
            self.log_console_stderr.config(state=tk.NORMAL)
            self.log_console_stderr.delete('1.0', tk.END)
            self.log_console_stderr.config(state=tk.DISABLED)
        
        #if name_of_selected == self.selected_job_name:
        #    return
           
        if not self.sweep_sim_dir:
            return
        
        if self.selected_job_name != None or (self.selected_job_name != name_of_selected and name_of_selected != ""): #selecting something different
            job = self.sweep_sim_dir.get_job(name_of_selected)
            self.display_job_log(job)
            
        """
        ssh_status = ["SSH_sbatch_RUNNING","SSH_sbatch_COMPLETED","SSH_sbatch_DOWNLOADED","SSH_batch_CANCELLED"]
        nsg_status = ["NSG_RUNNING","NSG_COMPLETED","NSG_DOWNLOADED","NSG_CANCELLED"]
        """
        self.selected_job_name = name_of_selected
        if(self.selected_job_name != ""):
            self.bj_clone.config(state=tk.NORMAL)
                        
            if(job.status==SimJob.created_status or job.status==ServerInterface.ssh_status[3] or job.status==ServerInterface.nsg_status[3]):
                self.bj_start.config(state=tk.NORMAL)
                self.bj_edit.config(state=tk.NORMAL)
            else:
                self.bj_start.config(state=tk.DISABLED)
                self.bj_edit.config(state=tk.DISABLED)
                            
            if(job.status==ServerInterface.ssh_status[2] or job.status==ServerInterface.nsg_status[2]):
                self.bj_open.config(state=tk.NORMAL)
                self.bj_run_cust.config(state=tk.NORMAL)
            else:
                self.bj_open.config(state=tk.DISABLED)
                self.bj_run_cust.config(state=tk.DISABLED)
            
            if(job.status==ServerInterface.ssh_status[0] or job.status==ServerInterface.nsg_status[0]):
                self.bj_stop.config(state=tk.NORMAL)
                self.bj_update.config(state=tk.NORMAL)
            else:
                self.bj_stop.config(state=tk.DISABLED)
                self.b_update.config(state=tk.DISABLED)
            
            
        else:
            self.bj_edit.config(state=tk.DISABLED)
            self.bj_start.config(state=tk.DISABLED)
            self.bj_stop.config(state=tk.DISABLED)
            self.bj_update.config(state=tk.DISABLED)
            self.bj_open.config(state=tk.DISABLED)
            self.bj_run_cust.config(state=tk.DISABLED)
        
        #print(str(self.table.row(row)))
    
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
    
    def load_dir(self, btn=None):
        
        dir_ = None
        if self.sim_dir and not btn:
            dir_ = self.sim_dir.sim_directory
        else:
            dir_ = filedialog.askdirectory()
        if not dir_:
            return
        try:
            
            self.sim_dir = SimDirectory(dir_,initialize=True)
            self.sim_dir_var.set(self.sim_dir.sim_directory)
            self.update_status.set(self.sim_dir.is_update_enabled())
            self.reload_table()         
            
            sim_sweeps_dir = os.path.join(self.sim_dir.sim_directory,ParametricSweep.sweeps_folder_name)
            sweeps_dir_files = os.listdir(sim_sweeps_dir)
            self.sweep_choices.clear()
            self.sweep_choices.append("")
            for file in sweeps_dir_files:
                if(os.path.isdir(os.path.join(sim_sweeps_dir,file))):
                    self.sweep_choices.append(file)
            self.reload_old_sweeps()
            
            self.b_new.config(state=tk.NORMAL)
            self.sweep_popupMenu.config(state=tk.NORMAL)
            self.b_tool_edit.config(state=tk.NORMAL)
            self.b_update_check.config(state=tk.NORMAL)
            
            self.refresh_time = self.sim_dir.update_interval_seconds  
            self.reset_sweep_picked()
        except Exception as e:
            print(e)
        
        return
    
    def reset_sweep_picked(self):
        self.sweep_picked.set(self.sweep_picked_default)
    
    def new_ps(self):
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
    
    def update_button_enabled(self, *args):
        self.sim_dir.set_update_enabled(self.update_status.get())
        return
    
    def exclude_folders_tool(self):
        return
    
    def reload_table(self):
        return
    
    def edit_dir_tool(self):
        if self.sim_dir and self.sim_dir != "":
            Edit_dir_tool(self.root, self.sim_dir)
    
    def load_ps(self):
        if self.sim_dir:
            if self.sweep_picked.get() != "" and self.sweep_picked.get() != self.sweep_picked_default:
                self.ps = ParametricSweep(self.sim_dir,self.sweep_picked.get(),external_state_var=self.parametric_sweep_state)
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
    
    """################ JOBS #################"""
    def edit_job(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        JobEntryBox(self.root, self.sweep_sim_dir, oncomplete_callback=self.update_row_info, edit_job=job)
        return
        
    def start_job(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Start Job", "Are you sure you want to start this job?\n\nAll files in " + self.sweep_sim_dir.sim_directory + " will be uploaded to your selected server and the selected file will run. The display may freeze for a few as this action is not threaded.", icon='warning') == 'yes'):
            job.run()
            self.update_row_info()
        return
    
    def update_job(self):
        if(messagebox.askquestion("Update Job", "Do you want to manually update the status of this job? The display may freeze for a few as this action is not threaded.", icon='warning') == 'yes'):
            job = self.sweep_sim_dir.get_job(self.selected_job_name)
            job.update()
            self.update_row_info()
        return
        
    def stop_job(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Stop Job", "Are you sure you want to stop this job?", icon='warning') == 'yes'):
            job.stop()
            self.update_row_info()
        return
    
    def delete_job_files(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Delete Remote Job Files", "Are you sure you want to delete this job? This action is irreversible and removes the files from your local disk and remote server.", icon='warning') == 'yes'):  
            try:
                job.delete_remote()
                self.sweep_sim_dir.delete_job(job)
                self.reload_table()
            except Exception as e:
                messagebox.showerror("Error", "There was an error deleting job files:\n\n" + e)
        return
    
    def download_remote_files(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        if(messagebox.askquestion("Download Remote Job Files", "Are you sure you want to re-download the files on the remote server? This is usually done through the update process automatically. This will overwrite {} and files in the folder {}.\n\n Additionally, this task is NOT threaded and will lock the window until the download has completed.".format(job.file_resultszip, job.dir_results), icon='warning') == 'yes'):
            job.download_remote()
            self.update_row_info()
        return    
    
    def open_job_folder(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        job.open_sim_results_directory()
        return
    
    def run_custom(self):
        job = self.sweep_sim_dir.get_job(self.selected_job_name)
        job.run_custom()
        self.update_row_info()
    
    def get_status_image_dict(self):
        return {SimJob.created_status:self.new_img,
                ServerInterface.nsg_status[0]:self.sync_img,ServerInterface.nsg_status[1]:self.cloud_img,ServerInterface.nsg_status[2]:self.check_img,ServerInterface.nsg_status[3]:self.error_img,
                ServerInterface.ssh_status[0]:self.sync_img,ServerInterface.ssh_status[1]:self.cloud_img,ServerInterface.ssh_status[2]:self.check_img,ServerInterface.ssh_status[3]:self.error_img}        
        #The Label widget is a standard Tkinter widget used to display a text or image on the screen.
        #panel = tk.Label(window, image = img)
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