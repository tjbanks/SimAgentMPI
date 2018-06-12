# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
import os
import tkinter as tk
from tkinter import filedialog,OptionMenu,messagebox
import time, datetime

from SimAgentMPI.SimServer import ServersFile
from SimAgentMPI.NewServerConfig import ServerEntryBox
from SimAgentMPI.ServerInterface import ServerInterface
from SimAgentMPI.SimJob import SimJob
from SimAgentMPI.Utils import AutocompleteEntry,CreateToolTip
from SimAgentMPI.ParametricSweep import ParameterContainer, ParametricSweep
import SimAgentMPI

class JobEntryBox:
        
        def __init__(self, parent, sim_directory, job_name=None, sim_job_copy=None, oncomplete_callback=None, edit_job=None, clone_mode=False):
            self.window_title = "New Job"
            if edit_job:
                self.window_title = "Edit Job"
            if clone_mode:
                self.window_title = "Clone Job"
                
            self.parent = parent
            self.sim_directory = sim_directory
            self.oncomplete_callback = oncomplete_callback
            self.edit_job = edit_job
            self.clone_mode = clone_mode
            self.valid_message = "Unspecified error, see console output"
            
            
            if(not job_name):
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%y%m%d%H%M%S')
                job_name = sim_directory.sim_directory_relative + "-" + st
            
            self.job_name = job_name
            self.simjob = None
            
            top = self.top = tk.Toplevel(self.parent)
            icon = os.path.abspath("SimAgentMPI/icons/sa_icon.ico")
            self.top.iconbitmap(r'{}'.format(icon))
            self.name = tk.StringVar(top)
            self.name.set(self.job_name)
            
            self.notes = tk.StringVar(top)
            self.status = tk.StringVar(top)
            self.batch_file = tk.StringVar(top)
            self.update_interval = tk.StringVar(top)
            self.update_interval.set("60")
            self.server_connector = tk.StringVar(top)
            self.server_nodes = tk.StringVar(top)
            self.server_cores = tk.StringVar(top)
            self.server_out = tk.StringVar(top)
            self.server_err = tk.StringVar(top)
            self.server_nsg_tool = tk.StringVar(top)
            self.server_ssh_tool = tk.StringVar(top)
            self.server_nsg_python = tk.IntVar(top)
            self.server_mpi_partition = tk.StringVar(top)
            self.server_max_runtime = tk.StringVar(top)
            self.server_max_runtime.set("1")
            #self.server_email = tk.StringVar(top)
            self.server_status_email = tk.BooleanVar(top)
            self.server_status_email.set(True)
            self.server_delete_remote_on_finish = tk.BooleanVar(top)
            self.server_delete_remote_on_finish.set(True)
            self.confirm = tk.BooleanVar(top)
            self.confirm.set(False)
            
            
            if edit_job:
                self.name.set(edit_job.sim_name)
                self.batch_file.set(edit_job.batch_file)
                self.update_interval.set(edit_job.update_interval)
                self.server_connector.set(edit_job.server_connector)
                self.server_nodes.set(edit_job.server_nodes)
                self.server_cores.set(edit_job.server_cores)
                self.server_out.set(edit_job.server_stdout_file)
                self.server_err.set(edit_job.server_stderr_file)
                self.server_nsg_tool.set(edit_job.server_nsg_tool)
                self.server_ssh_tool.set(edit_job.server_ssh_tool)
                self.server_nsg_python.set(edit_job.server_nsg_python)
                self.server_mpi_partition.set(edit_job.server_mpi_partition)
                self.server_max_runtime.set(edit_job.server_max_runtime)
                self.server_status_email.set(edit_job.server_status_email)
                self.server_delete_remote_on_finish.set(edit_job.sim_delete_remote_on_finish)
                
                if clone_mode:
                    self.name.set(edit_job.sim_name+"_clone")
            
            
            self.display()
            return
        
        def display(self):            
            top = self.top
            #top.geometry('375x435')
            top.resizable(0,0)
            top.title(self.window_title)
           
            
            def on_server_type_change(type_):
                if(type_ == "nsg"):
                    conn_option_frame.grid_forget()
                    nsgconn_option_frame.grid(column=0,row=14,sticky='news',padx=10,pady=5,columnspan=3)
                elif(type_ == "ssh"):
                    nsgconn_option_frame.grid_forget()
                    conn_option_frame.grid(column=0,row=15,sticky='news',padx=10,pady=5,columnspan=3)
                else:
                    conn_option_frame.grid_forget()
                    nsgconn_option_frame.grid_forget()
                    
                return
            
            def select_batch():
                self.batch_file.set(os.path.basename(filedialog.askopenfilename(initialdir=self.sim_directory.sim_directory)))
                self.top.lift()
                return
            
            def new_batch(*args):
                Create_Batch_File(self.top)
                return
        
        
            def new_server():
                ServerEntryBox(self.top, confirm_callback=set_server_choices)
                #Refresh options
                
                # on change dropdown value
            def change_dropdown(*args):
                server_name = self.server_connector.get()
                
                if(server_name==""):
                    on_server_type_change("")
                    return
                servers = ServersFile()
                s = servers.get_server_byname(server_name)
                #get the connection and check if it's a ssh / nsg
                if s:
                    on_server_type_change(s.type)
                
            def change_dropdown_nsg_tool(*args):
                return
            
            def change_dropdown_ssh_tool(*args):
                return
            
            
            def validate(action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
                if text in ' ':
                    return False
                else:
                    return True
                
            self.server_choicedrop = None
            def set_server_choices():
                self.server_choices = self.get_connections()
                if self.server_choicedrop is not None:
                    self.server_choicedrop.grid_forget()
                self.server_choicedrop = OptionMenu(general_option_frame, self.server_connector, *self.server_choices)
                self.server_choicedrop.grid(row = 5, column =1)
                
            
            vcmd = (top.register(validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
            
            toptext = "New Remote Job"
            if self.edit_job:
                toptext = "Edit Job"
            if self.clone_mode:
                toptext = "Clone Job"
            
            tk.Label(top, text=toptext).grid(row=0,column=0,sticky="WE",pady=15, columnspan=3)
            
            general_option_frame = tk.LabelFrame(top, text="General")
            
            tk.Label(general_option_frame, text='Sim Job Name',width=15, background='light gray', relief=tk.GROOVE).grid(row=1,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(general_option_frame,width=25,textvariable=self.name,validate='key', validatecommand=vcmd)
            self.name_e.grid(row=1,column=1,padx=5,columnspan=1)
            
            if self.edit_job:
                self.name_e.config(state=tk.DISABLED)
            if self.clone_mode:
                self.name_e.config(state=tk.NORMAL)
            
            tk.Label(general_option_frame, text='Server Connection',width=15, background='light gray',relief=tk.GROOVE).grid(row=5,column=0,pady=5,padx=5,columnspan=1)
            set_server_choices()
            
            self.server_connector.trace('w', change_dropdown)
            b = tk.Button(general_option_frame, text="New", command=new_server)
            b.grid(pady=5, padx=5, column=2, row=5, sticky="WE",columnspan=1)
            
            general_option_frame.grid(column=0,row=2,sticky='news',padx=10,pady=5,columnspan=3)
            
            conn_option_frame = tk.LabelFrame(top, text="SSH Connection Parameters")
            nsgconn_option_frame = tk.LabelFrame(top, text="NSG Connection Parameters")
            
            if self.edit_job:
                change_dropdown()#In case we're editing
            ###SSH###
            
            tk.Label(conn_option_frame, text='Tool',width=15, background='light gray',relief=tk.GROOVE).grid(row=1,column=0,pady=5,padx=5)
            self.ssh_tool_choices = ServerInterface().get_ssh_tools()
            popupMenu = OptionMenu(conn_option_frame, self.server_ssh_tool, *self.ssh_tool_choices)
            popupMenu.grid(row = 1, column =1)
            self.server_ssh_tool.trace('w', change_dropdown_ssh_tool)
                    
            tk.Label(conn_option_frame, text='Batch File',width=15, background='light gray',relief=tk.GROOVE).grid(row=2,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(conn_option_frame,width=25,textvariable=self.batch_file,state=tk.DISABLED)
            self.name_e.grid(row=2,column=1,padx=5,columnspan=1)
            b = tk.Button(conn_option_frame, text="Select", command=select_batch).grid(pady=5, padx=5, column=2, row=2, sticky="WE",columnspan=1)
            self.batch_file.trace('w', self.change_batch)
            #b = tk.Button(conn_option_frame, text="New", command=new_batch).grid(pady=5, padx=5, column=3, row=2, sticky="WE",columnspan=1)
            
            
            tk.Label(conn_option_frame, text='Partition',width=15, background='light gray',relief=tk.GROOVE).grid(row=3,column=0,pady=5,padx=5)
            self.host_e = tk.Entry(conn_option_frame,width=25,textvariable=self.server_mpi_partition)
            self.host_e.grid(row=3,column=1,padx=5)
            
            tk.Label(conn_option_frame, text='Nodes',width=15, background='light gray',relief=tk.GROOVE).grid(row=4,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(conn_option_frame,width=25,textvariable=self.server_nodes)
            self.name_e.grid(row=4,column=1,padx=5,columnspan=1)
            
            tk.Label(conn_option_frame, text='Cores',width=15, background='light gray',relief=tk.GROOVE).grid(row=5,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(conn_option_frame,width=25,textvariable=self.server_cores)
            self.name_e.grid(row=5,column=1,padx=5,columnspan=1)
            
            tk.Label(conn_option_frame, text='Max Run (hours)',width=15, background='light gray',relief=tk.GROOVE).grid(row=6,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(conn_option_frame,width=25,textvariable=self.server_max_runtime)
            self.name_e.grid(row=6,column=1,padx=5,columnspan=1)
            
            tk.Label(conn_option_frame, text='Delete Remote Files',width=15, background='light gray',relief=tk.GROOVE).grid(row=7,column=0,pady=5,padx=5)
            dcb1 = tk.Checkbutton(conn_option_frame, text="", variable=self.server_delete_remote_on_finish)
            dcb1.grid(row=7,column=1,padx=5, sticky='W')
            #CreateToolTip(dcb1,text="Delete the files on the remote server upon completion. This is a recommended setting")
            
                        
            ####NSG###
            
            tk.Label(nsgconn_option_frame, text='Tool',width=15, background='light gray',relief=tk.GROOVE).grid(row=2,column=0,pady=5,padx=5)
            self.nsg_tool_choices = self.get_nsg_tools()
            popupMenu = OptionMenu(nsgconn_option_frame, self.server_nsg_tool, *self.nsg_tool_choices)
            popupMenu.grid(row = 2, column =1)
            self.server_nsg_tool.trace('w', change_dropdown_nsg_tool)
            
            tk.Label(nsgconn_option_frame, text='Main Run File',width=15, background='light gray',relief=tk.GROOVE).grid(row=3,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.batch_file,state=tk.DISABLED)
            self.name_e.grid(row=3,column=1,padx=5,columnspan=1)
            b = tk.Button(nsgconn_option_frame, text="Select", command=select_batch).grid(pady=5, padx=5, column=2, row=3, sticky="WE",columnspan=1)
            
            tk.Label(nsgconn_option_frame, text='Nodes',width=15, background='light gray',relief=tk.GROOVE).grid(row=4,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.server_nodes)
            self.name_e.grid(row=4,column=1,padx=5,columnspan=1)
            
            tk.Label(nsgconn_option_frame, text='Cores',width=15, background='light gray',relief=tk.GROOVE).grid(row=5,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.server_cores)
            self.name_e.grid(row=5,column=1,padx=5,columnspan=1)
            
            tk.Label(nsgconn_option_frame, text='Max Run (hours)',width=15, background='light gray',relief=tk.GROOVE).grid(row=6,column=0,pady=5,padx=5,columnspan=1)
            self.name_e = tk.Entry(nsgconn_option_frame,width=25,textvariable=self.server_max_runtime)
            self.name_e.grid(row=6,column=1,padx=5,columnspan=1)
                        
            tk.Label(nsgconn_option_frame, text='Uses Python',width=15, background='light gray',relief=tk.GROOVE).grid(row=7,column=0,pady=5,padx=5)
            tk.Checkbutton(nsgconn_option_frame, text="", variable=self.server_nsg_python).grid(row=7,column=1,padx=5, sticky='W')
            
            tk.Label(nsgconn_option_frame, text='Send Status Emails',width=15, background='light gray',relief=tk.GROOVE).grid(row=8,column=0,pady=5,padx=5)
            tk.Checkbutton(nsgconn_option_frame, text="", variable=self.server_status_email).grid(row=8,column=1,padx=5, sticky='W')
            
            
            tk.Label(nsgconn_option_frame, text='Delete Remote Files',width=15, background='light gray',relief=tk.GROOVE).grid(row=9,column=0,pady=5,padx=5)
            dcb = tk.Checkbutton(nsgconn_option_frame, text="", variable=self.server_delete_remote_on_finish)
            dcb.grid(row=9,column=1,padx=5, sticky='W')
            #CreateToolTip(dcb,text="Delete the files on the remote server upon completion. This is a recommended setting")
            #Return
                        
            button_frame = tk.Frame(top)
            button_frame.grid(row=20,column=0,columnspan=3)
            
            b = tk.Button(button_frame, text="Ok", command=self.ok)
            b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
            
            b = tk.Button(button_frame, text="Cancel", command=self.cancel)
            b.grid(pady=5, padx=5, column=1, row=0, sticky="WE")
            
        
        def change_batch(self, *args):
                if self.batch_file.get() == "":
                    return
                
                batch_f = os.path.join(self.sim_directory.sim_directory,self.batch_file.get())
                part = "#SBATCH -p "
                nodes = "#SBATCH -N "
                cores = "#SBATCH -n "
                
                batch_part = SimAgentMPI.Utils.get_line_with(batch_f,part)
                batch_nodes = SimAgentMPI.Utils.get_line_with(batch_f,nodes)
                batch_cores = SimAgentMPI.Utils.get_line_with(batch_f,cores)
               
                                
                if batch_part:
                    batch_part = batch_part.replace(part,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                    self.server_mpi_partition.set(batch_part) 
                if batch_nodes:
                    batch_nodes = batch_nodes.replace(nodes,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                    self.server_nodes.set(batch_nodes)
                if batch_cores:
                    batch_cores = batch_cores.replace(cores,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                    self.server_cores.set(batch_cores)    
                
                    
                part = "#SBATCH --partition="
                nodes = "#SBATCH --nodes="
                cores = "#SBATCH --ntasks="
                
                
                batch_part = SimAgentMPI.Utils.get_line_with(batch_f,part)
                batch_nodes = SimAgentMPI.Utils.get_line_with(batch_f,nodes)
                batch_cores = SimAgentMPI.Utils.get_line_with(batch_f,cores)
                
                                
                if batch_part:
                    batch_part = batch_part.replace(part,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                    self.server_mpi_partition.set(batch_part) 
                if batch_nodes:
                    batch_nodes = batch_nodes.replace(nodes,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                    self.server_nodes.set(batch_nodes)
                if batch_cores:
                    batch_cores = batch_cores.replace(cores,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                    self.server_cores.set(batch_cores)
                    
                self.update_outerr_file_batch()
                    
                return
            
        def update_outerr_file_batch(self):
            if self.batch_file.get() == "":
                return
            
            batch_f = os.path.join(self.sim_directory.sim_directory,self.batch_file.get())
            
            out = "#SBATCH -o "
            err = "#SBATCH -e "
            
           
            batch_out = SimAgentMPI.Utils.get_line_with(batch_f,out)
            batch_err = SimAgentMPI.Utils.get_line_with(batch_f,err)
                         
            if batch_out:
                batch_out = batch_out.replace(out,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                self.server_out.set(batch_out)
            if batch_err:
                batch_err = batch_err.replace(err,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                self.server_err.set(batch_err)
                
            out = "#SBATCH --output="
            err = "#SBATCH --error="
           
            batch_out = SimAgentMPI.Utils.get_line_with(batch_f,out)
            batch_err = SimAgentMPI.Utils.get_line_with(batch_f,err)
                            
            
            if batch_out:
                batch_out = batch_out.replace(out,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                self.server_out.set(batch_out)
            if batch_err:
                batch_err = batch_err.replace(err,"").rstrip("\n\r").rstrip("\r").rstrip("\n").split("#")[0].strip()
                self.server_err.set(batch_err)
                
            return
            
        def verify_good(self):
            if (' ' in self.name.get()) == True:
                self.valid_message = "Name cannot contain spaces. (Issues with paths)"
                return False
            if self.server_connector.get() == '':
                self.valid_message = "Select a valid Server Connection."
                return False
            
            servers = ServersFile()
            s = servers.get_server_byname(self.server_connector.get())
            #get the connection and check if it's a ssh / nsg
            if not s:
                self.valid_message = "Server Connection not found, select or create a new one."
                return False
            type_ = s.type
            if type_ == "":
                self.valid_message = "Server Connection invalid, edit connector."
                return False
            
            if type_ == "nsg":
                if self.server_nsg_tool.get() == '':
                    self.valid_message = "Select a valid NSG Tool."
                    return False
            
                if self.batch_file.get() == '':
                    self.valid_message = "Select a valid Main Run File."
                    return False
                    
            if type_ == "ssh":
            
                if self.server_ssh_tool.get() == '':
                    self.valid_message = "Select a valid Tool."
                    return False
                if self.batch_file.get() == '':
                    self.valid_message = "Select a valid Batch File."
                    return False
                if self.server_mpi_partition.get() == '':
                    self.valid_message = "Enter a valid MPI Partition."
                    return False
            
            
            if self.server_nodes.get() == '' or self.server_nodes.get() == '0':
                self.valid_message = "Number of server nodes invalid, choose a number greater than 0."
                return False
            
            if self.server_cores.get() == '' or self.server_cores.get() == '0':
                self.valid_message = "Number of server cores invalid, choose a number greater than 0."
                return False
            
            if self.server_max_runtime.get() == '' or self.server_max_runtime.get() == '0':
                self.valid_message = "Max Run time invalid, chose a max run time greater than 0."
                return False
                
            
            return True
        
        
        def get_connections(self):            
            servers = ServersFile().servers
            names = [""]
            for s in servers:
                names.append(s.name)
            return names
        
        def get_nsg_tools(self):
            return ServerInterface().get_nsg_tools()
        
        def is_valid(self):
            return self.verify_good()
            
            
        
        def to_simjob(self, edit=False):
            simjob = None
            if edit and not self.clone_mode:
                simjob = self.edit_job
            else:
                simjob = SimJob(self.sim_directory, self.name.get())
            
            
            simjob.batch_file = self.batch_file.get()
            simjob.update_interval = self.update_interval.get()
            simjob.server_connector = self.server_connector.get()
            simjob.server_nodes = self.server_nodes.get()
            simjob.server_cores = self.server_cores.get()
            simjob.server_stdout_file = self.server_out.get()
            simjob.server_stderr_file = self.server_err.get()
            simjob.server_nsg_tool = self.server_nsg_tool.get()
            simjob.server_ssh_tool = self.server_ssh_tool.get()
            simjob.server_nsg_python = str(self.server_nsg_python.get())
            simjob.server_mpi_partition = self.server_mpi_partition.get()
            simjob.server_max_runtime = self.server_max_runtime.get()
            simjob.server_status_email = self.server_status_email.get()
            simjob.sim_delete_remote_on_finish = self.server_delete_remote_on_finish.get()
                                    
            return simjob
        
        def ok(self):
            self.confirm.set(True)
            if(self.confirm.get() and self.is_valid()):
                self.update_outerr_file_batch()
                if self.edit_job and not self.clone_mode:
                    simjob = self.to_simjob()
                    simjob.write_properties()
                    #simjob.append_log("Job edited")
                else:
                    #simjob.create_sim_directory()
                    simjob = self.to_simjob()
                    simjob.write_properties()
                    simjob.append_log("Job created")
                    self.sim_directory.add_new_job(simjob)
                if(self.oncomplete_callback):
                    self.oncomplete_callback()
                self.top.destroy()
            else:
                messagebox.showinfo("Validation Error",self.valid_message)
                self.top.lift()
            
        def cancel(self):
            self.top.destroy()


class Create_Batch_File(object):
    
    def __init__(self, parent, server=None, callback=None):
        self.parent = parent
        self.server = server
        self.window_title = "Select Server"
        self.confirm = False
        self.callback = callback
        self.modules_avail = []
        self.mod_frames = []
        self.mod_vals = []
        self.mod_num = 0
        self.display()
        
    def display(self):
        top = self.top = tk.Toplevel(self.parent)
        #top.geometry('340x175')
        top.resizable(1,1)
        top.title(self.window_title)
        
        servers = ServersFile().servers
        names = [""]
        
        for server in servers:
            names.append(server.name)
        
        main_frame = tk.Frame(self.top)
        main_frame.grid(pady=5, padx=5, column=0,row=0, sticky='NEWS')
        
        self.server_selected = tk.StringVar(main_frame)
        #tk.Label(main_frame, text='Load Modules from Server',width=15, background='light gray',relief=tk.GROOVE).grid(row=0,column=0,pady=5,padx=5)
        popupMenu = OptionMenu(main_frame, self.server_selected, *names)
        popupMenu.grid(row = 0, column =1)
        b = tk.Button(main_frame, text="Load Modules from Server", command=self.get_modules)
        b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
        
        module_frame = tk.Frame(main_frame)
        module_frame.grid(column = 0, row=2)
        
        b = tk.Button(main_frame, text="New Module", command=lambda x=module_frame:self.new_module(x))
        b.grid(pady=5, padx=5, column=0, row=1, sticky="WE")
        
        b = tk.Button(main_frame, text="Ok", command=self.ok)
        b.grid(pady=5, padx=5, column=0, row=400, sticky="WE")
        
        b = tk.Button(main_frame, text="Cancel", command=self.cancel)
        b.grid(pady=5, padx=5, column=1, row=400, sticky="WE")
        
    def new_module(self, parent):
        frame = tk.Frame(parent)
        entry = AutocompleteEntry(frame, self.modules_avail, listboxLength=6, width=32, window_frame=tk.Tk())
        b = tk.Button(frame, text="X", command=lambda x=self.mod_num:self.on_delete_module(x))
        entry.grid(row=0,column=0)
        b.grid(row=0,column=1)
        self.mod_frames.append(frame)
        self.mod_vals.append(entry)
        frame.grid(row=self.mod_num, column=0)
        self.mod_num = self.mod_num+1
        return 
        
    def get_modules(self):
        #self.server_selected
        list_ = [ 'Dora Lyons (7714)', 'Hannah Golden (6010)', 'Walker Burns (9390)', 'Dieter Pearson (6347)', 'Allen Sullivan (9781)', 'Warren Sullivan (3094)', 'Genevieve Mayo (8427)', 'Igor Conner (4740)', 'Ulysses Shepherd (8116)', 'Imogene Bullock (6736)', 'Dominique Sanchez (949)', 'Sean Robinson (3784)', 'Diana Greer (2385)', 'Arsenio Conrad (2891)', 'Sophia Rowland (5713)', 'Garrett Lindsay (5760)', 'Lacy Henry (4350)', 'Tanek Conley (9054)', 'Octavia Michael (5040)', 'Kimberly Chan (1989)', 'Melodie Wooten (7753)', 'Winter Beard (3896)', 'Callum Schultz (7762)', 'Prescott Silva (3736)', 'Adena Crane (6684)', 'Ocean Schroeder (2354)', 'Aspen Blevins (8588)', 'Allegra Gould (7323)', 'Penelope Aguirre (7639)', 'Deanna Norman (1963)', 'Herman Mcintosh (1776)', 'August Hansen (547)', 'Oscar Sanford (2333)', 'Guy Vincent (1656)', 'Indigo Frye (3236)', 'Angelica Vargas (1697)', 'Bevis Blair (4354)', 'Trevor Wilkinson (7067)', 'Kameko Lloyd (2660)', 'Giselle Gaines (9103)', 'Phyllis Bowers (6661)', 'Patrick Rowe (2615)', 'Cheyenne Manning (1743)', 'Jolie Carney (6741)', 'Joel Faulkner (6224)', 'Anika Bennett (9298)', 'Clayton Cherry (3687)', 'Shellie Stevenson (6100)', 'Marah Odonnell (3115)', 'Quintessa Wallace (5241)', 'Jayme Ramsey (8337)', 'Kyle Collier (8284)', 'Jameson Doyle (9258)', 'Rigel Blake (2124)', 'Joan Smith (3633)', 'Autumn Osborne (5180)', 'Renee Randolph (3100)', 'Fallon England (6976)', 'Fallon Jefferson (6807)', 'Kevyn Koch (9429)', 'Paki Mckay (504)', 'Connor Pitts (1966)', 'Rebecca Coffey (4975)', 'Jordan Morrow (1772)', 'Teegan Snider (5808)', 'Tatyana Cunningham (7691)', 'Owen Holloway (6814)', 'Desiree Delaney (272)', 'Armand Snider (8511)', 'Wallace Molina (4302)', 'Amela Walker (1637)', 'Denton Tillman (201)', 'Bruno Acevedo (7684)', 'Slade Hebert (5945)', 'Elmo Watkins (9282)', 'Oleg Copeland (8013)', 'Vladimir Taylor (3846)', 'Sierra Coffey (7052)', 'Holmes Scott (8907)', 'Evelyn Charles (8528)', 'Steel Cooke (5173)', 'Roth Barrett (7977)', 'Justina Slater (3865)', 'Mara Andrews (3113)', 'Ulla Skinner (9342)', 'Reece Lawrence (6074)', 'Violet Clay (6516)', 'Ainsley Mcintyre (6610)', 'Chanda Pugh (9853)', 'Brody Rosales (2662)', 'Serena Rivas (7156)', 'Henry Lang (4439)', 'Clark Olson (636)', 'Tashya Cotton (5795)', 'Kim Matthews (2774)', 'Leilani Good (5360)', 'Deirdre Lindsey (5829)', 'Macy Fields (268)', 'Daniel Parrish (1166)', 'Talon Winters (8469)' ]
        self.modules_avail = list_
        return 
    def on_delete_module(self, mod):
        self.mod_frames[mod].grid_forget()
        self.mod_vals[mod].set("")
        
    def ok(self):
        self.confirm = True
        self.top.destroy()
        if self.callback:
            self.callback(self)
        
    def cancel(self):
        self.top.destroy()
        
        return
    
class SweepNew():
    
    def __init__(self, parent,sim_dir,callback=None,button_width=15):
        self.window_title = "Create Range"
        self.top = tk.Toplevel(parent)
        self.parent = parent
        
        self.sim_dir = sim_dir
        icon = os.path.abspath("SimAgentMPI/icons/sa_icon.ico")
        self.top.iconbitmap(r'{}'.format(icon))
        self.confirm = False
        self.callback=callback  
        self.button_width = button_width
        self.verify_message = ""
        
        self.display()
        return
    
    def display(self):   
        #top.geometry('375x435')
        self.top.resizable(1,1)
        
        self.name = tk.StringVar(self.top)
        
        tk.Label(self.top, text='Name',width=15, background='light gray',relief=tk.GROOVE).grid(row=2,column=0,pady=5,padx=5)
        self.name_e = tk.Entry(self.top,width=25,textvariable=self.name)
        self.name_e.grid(row=2,column=1,padx=5)
        
        self.b_submit = tk.Button(self.top, text="Ok", command=self.ok, width=self.button_width)
        self.b_submit.grid(pady=5, padx=5, column=0, row=13, sticky="WE",rowspan=1)
        self.b_submit.config(state=tk.NORMAL)
        
        self.b_cancel = tk.Button(self.top, text="Cancel", command=self.cancel, width=self.button_width)
        self.b_cancel.grid(pady=5, padx=5, column=1, row=13, sticky="WE",rowspan=1)
        self.b_cancel.config(state=tk.NORMAL)
        
    def verify(self):
        if self.name.get() == "":
            self.verify_message = "Enter a valid name."
            return False
        return True
    
    def ok(self):
        if not self.verify():
            messagebox.showerror("Validation Error", self.verify_message)
            self.top.lift()
            return
        if(messagebox.askquestion("Creating Sweep", "This will create a snapshot of your directory as it is and any edits to the original code will not be propagated. Ensure your code is how you want it. Create sweep?", icon='warning') == 'yes'):
            self.parameter_sweep = ParametricSweep(self.sim_dir, self.name.get())
            self.parameter_sweep.write_properties()
            
            self.confirm = True
            self.top.destroy()
            if self.callback:
                self.callback(self.parameter_sweep)
        
    def cancel(self):
        self.top.destroy()
    
class SweepEditor():
    
    def __init__(self, parent,sim_dir,parameter_sweep,callback=None,button_width=15):
        self.window_title = "Create Range"
        self.top = tk.Toplevel(parent)
        self.parent = parent
        
        self.sim_dir = sim_dir
        self.parameter_sweep = parameter_sweep
        icon = os.path.abspath("SimAgentMPI/icons/sa_icon.ico")
        self.top.iconbitmap(r'{}'.format(icon))
        self.confirm = False
        self.callback=callback  
        self.button_width = button_width
        self.verify_message = ""
        
        self.display()
        self.fill_fields()
        return
    
    def display(self):   
        #top.geometry('375x435')
        self.top.resizable(1,1)
        
        self.name = tk.StringVar(self.top)
        self.maxjobs = tk.StringVar(self.top)
        
        #tk.Label(self.top, text='New Value Range',fg="blue").grid(row=9,column=0,pady=5,padx=5,columnspan=2)
        #tk.Label(self.top, text='Start',width=15, background='light gray',relief=tk.GROOVE).grid(row=10,column=0,pady=5,padx=5)
        #self.start_e = tk.Entry(self.top,width=25,textvariable=self.start)
        #self.start_e.grid(row=10,column=1,padx=5)
        
        tk.Label(self.top, text='Name',width=15, background='light gray',relief=tk.GROOVE).grid(row=2,column=0,pady=5,padx=5)
        self.name_e = tk.Entry(self.top,width=25,textvariable=self.name)
        self.name_e.grid(row=2,column=1,padx=5)
        
        tk.Label(self.top, text='Max Jobs',width=15, background='light gray',relief=tk.GROOVE).grid(row=3,column=0,pady=5,padx=5)
        self.maxjobs_e = tk.Entry(self.top,width=25,textvariable=self.maxjobs)
        self.maxjobs_e.grid(row=3,column=1,padx=5)
        
        tk.Label(self.top, text='Job Template',width=15, background='light gray',relief=tk.GROOVE).grid(row=4,column=0,pady=5,padx=5)
        self.b_edit_job = tk.Button(self.top, text="Edit", command=self.edit_job)
        self.b_edit_job.grid(pady=5, padx=5, column=1, row=4, sticky="WE",rowspan=1)
        
        
        #tk.Label(self.top, text='Stride',width=15, background='light gray',relief=tk.GROOVE).grid(row=12,column=0,pady=5,padx=5)
        #self.stride_e = tk.Entry(self.top,width=25,textvariable=self.stride)
        #self.stride_e.grid(row=12,column=1,padx=5)
        
        self.b_submit = tk.Button(self.top, text="New Parameter Range", command=self.new_param)
        self.b_submit.grid(pady=5, padx=5, column=0, row=12, sticky="WE",rowspan=1)
        self.b_submit.config(state=tk.NORMAL)
        
        self.b_submit = tk.Button(self.top, text="Ok", command=self.ok, width=self.button_width)
        self.b_submit.grid(pady=5, padx=5, column=0, row=13, sticky="WE",rowspan=1)
        self.b_submit.config(state=tk.NORMAL)
        
        self.b_cancel = tk.Button(self.top, text="Cancel", command=self.cancel, width=self.button_width)
        self.b_cancel.grid(pady=5, padx=5, column=1, row=13, sticky="WE",rowspan=1)
        self.b_cancel.config(state=tk.NORMAL)
            
        if self.parameter_sweep: #Editor mode shouldn't be able to change the name
            self.name_e.config(state=tk.DISABLED)
        
    def fill_fields(self):
        if self.parameter_sweep:
            self.name.set(self.parameter_sweep.name)
        else:
            self.name.set("")
            
        return
    
    
    def edit_job(self):
        def edit_job_():
            return
        sj = self.sim_dir.get_job(ParametricSweep.job_template_name)
        if sj:
            sj.append_log("Template edited")
            JobEntryBox(self.top, self.parameter_sweep.sweep_project_dir, oncomplete_callback=edit_job_, edit_job=sj)
        else:
            sj = SimJob(self.sim_dir,ParametricSweep.job_template_name)
            sj.write_properties()
            sj.append_log("Template created")
            self.sim_dir.add_new_job(sj)
            JobEntryBox(self.top, self.parameter_sweep.sweep_project_dir,oncomplete_callback=edit_job_,edit_job=sj)
        return
    
    def new_param(self):
        """ TESTING START """
        file_read = filedialog.askopenfilename()
        if not file_read:
            self.top.lift()
            return
        
        file_read = os.path.abspath(file_read)
        def c(parameter_container):
            print(parameter_container.to_json())
            self.parameter_sweep.add_parameter(parameter_container)
            self.top.lift()
        ParameterSelectTextBox(self.top, file_read, callback=c)
        
        """ TESTING END """

    def verify(self):
        
        if self.name.get() == "":
            self.verify_message = "Enter a valid name."
            return False
        
        return True
    def write_ps(self):
        if not self.parameter_sweep:
            self.parameter_sweep = ParametricSweep(self.sim_dir, self.name.get())
                
        return
    
    def ok(self):
        if not self.verify():
            messagebox.showerror("Validation Error", self.verify_message)
            self.top.lift()
            return
        else:
            self.write_ps()
        self.parameter_sweep.write_properties()
        
        self.confirm = True
        self.top.destroy()
        if self.callback:
            self.callback(self.parameter_sweep)
        
    def cancel(self):
        self.top.destroy()
        
class ParameterTable():
    def __init__(self):
        return
    def dispaly(self):
        return
        
class ParameterSelectTextBox():
    
    class Ranger():
        def __init__(self, parent, callback=None, button_width=15):
            self.window_title = "Create Range"
            self.top = tk.Toplevel(parent)
            self.parent = parent
            icon = os.path.abspath("SimAgentMPI/icons/sa_icon.ico")
            self.top.iconbitmap(r'{}'.format(icon))
            self.confirm = False
            self.start = tk.StringVar(self.top)
            self.end = tk.StringVar(self.top)
            self.stride = tk.StringVar(self.top)
            self.stride.set("1")
            
            self.callback = callback
            self.button_width=button_width
            
            self.display()
            
        def display(self):   
            #top.geometry('375x435')
            self.top.resizable(1,1)
            tk.Label(self.top, text='New Value Range',fg="blue").grid(row=9,column=0,pady=5,padx=5,columnspan=2)
            tk.Label(self.top, text='Start',width=15, background='light gray',relief=tk.GROOVE).grid(row=10,column=0,pady=5,padx=5)
            self.start_e = tk.Entry(self.top,width=25,textvariable=self.start)
            self.start_e.grid(row=10,column=1,padx=5)
            
            tk.Label(self.top, text='End',width=15, background='light gray',relief=tk.GROOVE).grid(row=11,column=0,pady=5,padx=5)
            self.end_e = tk.Entry(self.top,width=25,textvariable=self.end)
            self.end_e.grid(row=11,column=1,padx=5)
            
            tk.Label(self.top, text='Stride',width=15, background='light gray',relief=tk.GROOVE).grid(row=12,column=0,pady=5,padx=5)
            self.stride_e = tk.Entry(self.top,width=25,textvariable=self.stride)
            self.stride_e.grid(row=12,column=1,padx=5)
            
            self.b_submit = tk.Button(self.top, text="Ok", command=self.ok, width=self.button_width)
            self.b_submit.grid(pady=5, padx=5, column=0, row=13, sticky="WE",rowspan=1)
            self.b_submit.config(state=tk.NORMAL)
            
            self.b_cancel = tk.Button(self.top, text="Cancel", command=self.cancel, width=self.button_width)
            self.b_cancel.grid(pady=5, padx=5, column=1, row=13, sticky="WE",rowspan=1)
            self.b_cancel.config(state=tk.NORMAL)
            
        def ok(self):
            self.top.destroy()
            if self.callback:
                self.callback()
        
        def cancel(self):
            self.top.destroy()
            
    
    def __init__(self, parent, file_, callback=None, edit_select=None, button_width=15):
        self.window_title = "New Parameter"
        if edit_select:
            self.window_title = "Edit Parameter Selection"
            
        self.parent = parent
        self.file_ = file_
        self.callback = callback
        self.edit_select = edit_select
        self.button_width = button_width
        self.valid_message = "Unspecified error, see console output"
        
        self.selected_text = ""
        self.selected_start = -1
        self.selected_end = -1
        self.selected_params = []
        
        self.top = tk.Toplevel(self.parent)
        icon = os.path.abspath("SimAgentMPI/icons/sa_icon.ico")
        self.top.iconbitmap(r'{}'.format(icon))
            
        self.confirm = False
        self.display()
        return
        
    def display(self):   
        #top.geometry('375x435')
        self.top.resizable(1,1)
        self.top.rowconfigure(2, weight=1)
        self.top.columnconfigure(0, weight=1)
        self.top.title(self.window_title)
        
        self.manage_frame = tk.LabelFrame(self.top, text="Management")
        self.manage_frame.rowconfigure(0, weight=1)
        self.manage_frame.columnconfigure(1, weight=2)
        self.manage_frame.columnconfigure(2, weight=2)
        
        self.text_frame = tk.LabelFrame(self.top, text=os.path.basename(self.file_),fg="blue")
        self.text_frame.rowconfigure(1, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        
        """ MANAGE FRAME """
        self.b_get_select = tk.Button(self.manage_frame, text="Mark Selection", command=self.get_selection, width=self.button_width)
        self.b_get_select.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
        self.b_get_select.config(state=tk.NORMAL,fg="white",bg="blue")
        
        self.params_var = tk.StringVar(self.top)
        tk.Label(self.manage_frame, text='Parameters to be used during sweep. Separate with commas.').grid(row=0,column=1,pady=5,padx=5,columnspan=2)
        self.params_e = tk.Entry(self.manage_frame,textvariable=self.params_var,width=2*self.button_width)
        self.params_e.grid(row=1,column=1,padx=5,columnspan=2,sticky="WE")
        
        self.b_new_list = tk.Button(self.manage_frame, text="New List", command=self.ok, width=self.button_width)
        #self.b_new_list.grid(pady=5, padx=5, column=0, row=1, sticky="WE",rowspan=1)
        self.b_new_list.config(state=tk.NORMAL)
        
        self.b_new_range = tk.Button(self.manage_frame, text="New Range", command=self.new_range, width=self.button_width)
        self.b_new_range.grid(pady=5, padx=5, column=0, row=1, sticky="WE",rowspan=1)
        self.b_new_range.config(state=tk.NORMAL)
        
        
        self.b_submit = tk.Button(self.manage_frame, text="Finish", command=self.ok, width=self.button_width)
        self.b_submit.grid(pady=5, padx=5, column=4, row=0, sticky="WE",rowspan=1)
        self.b_submit.config(state=tk.DISABLED)
        
        self.b_cancel = tk.Button(self.manage_frame, text="Cancel", command=self.cancel, width=self.button_width)
        self.b_cancel.grid(pady=5, padx=5, column=4, row=1, sticky="WE",rowspan=1)
        self.b_cancel.config(state=tk.NORMAL)
        
        """ TEXT FRAME """
        tk.Label(self.text_frame, text='Hightlight area to be replaced during parameter search and click \'Mark Selection\'.').grid(row=0,column=0,pady=5,padx=5,columnspan=1)
        
        self.text_console = tk.Text(self.text_frame)
        self.text_console.config( bg='white',fg='black')
        self.text_console.grid(column=0, row=1, padx=5, pady=5, sticky='NEWS')
        
        self.text_console.config(state=tk.NORMAL)
        text = self.get_file_text()
        self.text_console.delete('1.0', tk.END)
        self.text_console.insert(tk.END, text)
        self.text_console.config(state=tk.DISABLED)
        
        self.load_other_highlights()
        
        
        self.manage_frame.grid(column=0,row=1,sticky='news',padx=5,pady=5,columnspan=2)
        self.text_frame.grid(column=0,row=2,sticky='news',padx=5,pady=5,columnspan=2)
        

    def get_selection(self):
        tag = "currenthighlight"
        try:
            self.selected_text = self.text_console.selection_get()
            self.selected_start = self.text_console.index(tk.SEL_FIRST)
            self.selected_end = self.text_console.index(tk.SEL_LAST)
            
            self.text_console.tag_delete(tag)
            self.text_console.tag_add(tag, self.selected_start, self.selected_end)
            self.text_console.tag_config(tag, background="blue", foreground="white")
            
            self.b_submit.config(state=tk.NORMAL)
            
        except Exception as e:
            pass
        
    def new_range(self):
        def cb(*args):
            comma = ""
            if self.params_var.get() != "":
                comma = ","
                
            try:
                r_vals = ""
                rn = range(int(ranger.start.get()),int(ranger.end.get()),int(ranger.stride.get()))
                for i, r in enumerate(rn):
                    if i == 0:
                        r_vals = str(r)
                    else:
                        r_vals = r_vals + "," + str(r)
                self.params_var.set(self.params_var.get()+comma+r_vals)
            except Exception as e:
                messagebox.showwarning("Error", "Range formatted improperly")
            
            self.top.lift()
        
        ranger = ParameterSelectTextBox.Ranger(self.top,callback=cb)
        
    def get_file_text(self):
        f = open(self.file_,"r")
        string = f.read()
        f.close()
        return string
    
    def load_other_highlights(self):
        return
    
    def parse_params(self):
        self.selected_params = self.params_var.get().split(",")
        return
    
    def ok(self):
        self.confirm = True
        self.parse_params()
        cont = ParameterContainer().init(self.file_,"",self.selected_start,self.selected_end,self.selected_params)
        self.top.destroy()
        if self.callback:
            self.callback(cont)
        
    def cancel(self):
        self.top.destroy()
