# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:46:40 2018

@author: Tyler
"""
import os
import tkinter as tk
from tkinter import filedialog,OptionMenu,messagebox
import time, datetime

from SimServer import ServersFile
from NewServerConfig import ServerEntryBox
from ServerInterface import ServerInterface
from SimJob import SimJob
import Utils

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
            
            
            if(not job_name):
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%y%m%d%H%M%S')
                job_name = sim_directory.sim_directory_relative + "-" + st
            
            self.job_name = job_name
            self.simjob = None
            
            top = self.top = tk.Toplevel(self.parent)
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
            self.server_nsg_tool = tk.StringVar(top)
            self.server_ssh_tool = tk.StringVar(top)
            self.server_nsg_python = tk.IntVar(top)
            self.server_mpi_partition = tk.StringVar(top)
            self.server_max_runtime = tk.StringVar(top)
            self.server_max_runtime.set("1")
            #self.server_email = tk.StringVar(top)
            self.server_status_email = tk.IntVar(top)
            self.confirm = tk.BooleanVar(top)
            self.confirm.set(False)
            
            
            if edit_job:
                self.name.set(edit_job.sim_name)
                self.batch_file.set(edit_job.batch_file)
                self.update_interval.set(edit_job.update_interval)
                self.server_connector.set(edit_job.server_connector)
                self.server_nodes.set(edit_job.server_nodes)
                self.server_cores.set(edit_job.server_cores)
                self.server_nsg_tool.set(edit_job.server_nsg_tool)
                self.server_ssh_tool.set(edit_job.server_ssh_tool)
                self.server_nsg_python.set(edit_job.server_nsg_python)
                self.server_mpi_partition.set(edit_job.server_mpi_partition)
                self.server_max_runtime.set(edit_job.server_max_runtime)
                
                if clone_mode:
                    self.name.set(edit_job.sim_name+"_clone")
            
            
            self.display()
            return
        
        def display(self):            
            top = self.top
            top.geometry('375x435')
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
                self.batch_file.set(os.path.basename(filedialog.askopenfilename()))
                self.top.lift()
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
                on_server_type_change(s.type)
                
            def change_dropdown_nsg_tool(*args):
                return
            
            def change_dropdown_ssh_tool(*args):
                return
            
            def change_batch(*args):
                if self.batch_file.get() == "":
                    return
                
                batch_f = os.path.join(self.sim_directory.sim_directory,self.batch_file.get())
                part = "#SBATCH -p "
                nodes = "#SBATCH -N "
                cores = "#SBATCH -n "
                
                batch_part = Utils.get_line_with(batch_f,part)
                batch_nodes = Utils.get_line_with(batch_f,nodes)
                batch_cores = Utils.get_line_with(batch_f,cores)
                                
                if batch_part:
                    batch_part = batch_part.replace(part,"").rstrip("\n\r").rstrip("\r").rstrip("\n")
                    self.server_mpi_partition.set(batch_part) 
                if batch_nodes:
                    batch_nodes = batch_nodes.replace(nodes,"").rstrip("\n\r").rstrip("\r").rstrip("\n")
                    self.server_nodes.set(batch_nodes)
                if batch_nodes:
                    batch_cores = batch_cores.replace(cores,"").rstrip("\n\r").rstrip("\r").rstrip("\n")
                    self.server_cores.set(batch_cores)         
                     
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
            self.batch_file.trace('w', change_batch)
            
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
             
            #Return
                        
            button_frame = tk.Frame(top)
            button_frame.grid(row=20,column=0,columnspan=3)
            
            b = tk.Button(button_frame, text="Ok", command=self.ok)
            b.grid(pady=5, padx=5, column=0, row=0, sticky="WE")
            
            b = tk.Button(button_frame, text="Cancel", command=self.cancel)
            b.grid(pady=5, padx=5, column=1, row=0, sticky="WE")
            
            
        def verify_good(self):
            if (' ' in self.name.get()) == True:
                self.valid_message = "Name cannot contain spaces. (Issues with paths)"
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
            simjob.server_nsg_tool = self.server_nsg_tool.get()
            simjob.server_ssh_tool = self.server_ssh_tool.get()
            simjob.server_nsg_python = str(self.server_nsg_python.get())
            simjob.server_mpi_partition = self.server_mpi_partition.get()
            simjob.server_max_runtime = self.server_max_runtime.get()
                                    
            return simjob
        
        def ok(self):
            self.confirm.set(True)
            if(self.confirm.get() and self.is_valid()):
                if self.edit_job and not self.clone_mode:
                    simjob = self.to_simjob()
                    simjob.write_properties()
                    #simjob.append_log("Job edited")
                else:
                    simjob = self.to_simjob()
                    simjob.create_sim_directory()
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
            